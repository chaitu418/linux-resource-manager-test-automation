import requests
import pytest
import requests
from config import BASE_URL

def test_complete_process_lifecycle():
    """Here we are tesing the complete cycle 
    """
    # 1. POST /processes - Create
    payload = {"name": "functional_test_proc", "command": "sleep 100", "resource_class": "STANDARD"}
    create_res = requests.post(f"{BASE_URL}/processes", json=payload)
    assert create_res.status_code == 201
    proc_id = create_res.json()["process_id"]

    # 2. GET /processes/{id} - Retrieve
    get_res = requests.get(f"{BASE_URL}/processes/{proc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "functional_test_proc"

    # 3. DELETE /processes/{id} - Terminate
    del_res = requests.delete(f"{BASE_URL}/processes/{proc_id}")
    assert del_res.status_code == 204

    # 4. Verify 404 after deletion
    verify_res = requests.get(f"{BASE_URL}/processes/{proc_id}")
    assert verify_res.status_code == 404
    

def test_resource_usage_query():
    """Resource a dn utilization tests
    """
    # Create process
    proc = requests.post(f"{BASE_URL}/processes", json={
        "name": "resource_monitor", "command": "top"
    }).json()
    proc_id = proc["process_id"]

    # Update usage manually via admin endpoint
    requests.post(f"{BASE_URL}/admin/processes/{proc_id}/update-usage", json={
        "cpu_percent": 10.0, "memory_mb": 512
    })

    # Query resources
    res = requests.get(f"{BASE_URL}/processes/{proc_id}/resources")
    assert res.status_code == 200
    data = res.json()
    assert "utilization" in data
    # STANDARD limit is 2048MB. 512MB usage should be 25.0%
    assert data["utilization"]["memory_utilization"] == "25.0%"
    
def test_admin_rebalance_trigger():
    # Setup a process in BEST_EFFORT with high CPU (>50%)
    proc = requests.post(f"{BASE_URL}/processes", json={
        "name": "upgrade_task", "command": "stress", "resource_class": "BEST_EFFORT"
    }).json()
    p_id = proc["process_id"]

    # Simulate high activity
    requests.post(f"{BASE_URL}/admin/processes/{p_id}/update-usage", json={
        "cpu_percent": 65.0, "memory_mb": 100
    })

    # Trigger Admin Rebalance
    rebalance_res = requests.post(f"{BASE_URL}/admin/rebalance")
    assert rebalance_res.status_code == 200
    assert rebalance_res.json()["upgrades"] >= 1

    # Verify upgrade to STANDARD
    updated_proc = requests.get(f"{BASE_URL}/processes/{p_id}").json()
    assert updated_proc["resource_class"] == "STANDARD"

def test_admin_system_stats():
    # Verify the stats endpoint aggregates correctly
    stats_res = requests.get(f"{BASE_URL}/admin/stats")
    assert stats_res.status_code == 200
    data = stats_res.json()
    assert "total_processes" in data
    assert "by_class" in data

def test_invalid_process_creation():
    # Missing 'command' field should trigger 422
    invalid_payload = {"name": "broken_proc"}
    response = requests.post(f"{BASE_URL}/processes", json=invalid_payload)
    assert response.status_code == 422


def test_system_rule_enforcement():
    """
    Validates: System processes (containing _SYSTEM_ in name) always stay in CRITICAL.
    This test verifies that the 'Idle' rule does NOT apply to System processes.
    """
    pid = None
    try:
        # 1. Setup - Create a System Process
        name = "NETWORK_SYSTEM_MANAGER"
        create_resp = requests.post(f"{BASE_URL}/processes", json={
            "name": name, 
            "command": "/usr/sbin/netmgr", 
            "resource_class": "CRITICAL"
        })
        assert create_resp.status_code == 201
        pid = create_resp.json()["process_id"]

        # 2. Simulate Idle State (10% CPU for 15 mins)
        # Policy: <20% CPU for 10 mins -> downgrade one class
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 10, 
            "memory_mb": 500, 
            "duration_minutes": 15
        })

        # 3. Trigger Rebalance
        requests.post(f"{BASE_URL}/admin/rebalance")

        # 4. Final Validation
        final_proc = requests.get(f"{BASE_URL}/processes/{pid}").json()
        
        # Highlighting the failure specifically
        assert final_proc["resource_class"] == "CRITICAL", \
            f"BUG: System process '{name}' was wrongly downgraded to {final_proc['resource_class']}"
        
        assert final_proc["limits"]["cpu_share_percent"] == 80, \
            f"BUG: Resource limits were reduced for system process '{name}'"

    finally:
        # Cleanup: Ensure the process is deleted so it doesn't skew stats for other tests
        if pid:
            requests.delete(f"{BASE_URL}/processes/{pid}")
            
@pytest.mark.parametrize("db_name, r_class, expected_mb", [
    ("user_postgres_db", "STANDARD", 4096),   # 2GB * 2
    ("cache_redis", "BEST_EFFORT", 1024),     # 512MB * 2
    ("mysql_prod_master", "CRITICAL", 16384)  # 8GB * 2
])
def test_database_memory_boost_on_creation(db_name, r_class, expected_mb):
    """
    Validates that database processes receive 2x memory limits upon creation.
    Requirement: Business rule validation - Database processes get 2x memory.
    """
    pid = None
    try:
        # 1. Create Process
        payload = {
            "name": db_name,
            "command": "/usr/bin/db-service",
            "resource_class": r_class
        }
        resp = requests.post(f"{BASE_URL}/processes", json=payload)
        assert resp.status_code == 201
        
        data = resp.json()
        pid = data["process_id"]

        # 2. Verify Memory Limit
        actual_mem = data["limits"]["memory_limit_mb"]
        assert actual_mem == expected_mb, f"Expected {expected_mb}MB for {db_name}, got {actual_mem}MB"

    finally:
        # Cleanup
        if pid:
            requests.delete(f"{BASE_URL}/processes/{pid}")


@pytest.mark.parametrize("start_class, cpu, duration, expected_class", [
    ("CRITICAL", 10.0, 11, "STANDARD"),     # Rule: <20% for 10m -> Drop one
    ("STANDARD", 15.0, 12, "BEST_EFFORT"), # Rule: <20% for 10m -> Drop one
    ("CRITICAL", 90.0, 6, "BEST_EFFORT")    # Rule: >80% for 5m -> Direct drop
])
def test_resource_downgrade_transitions(start_class, cpu, duration, expected_class):
    """
    Validates the state machine transitions from CRITICAL to lower tiers.
    Requirement: Resource class transitions tested (5 points).
    """
    pid = None
    try:
        # 1. Create process in the high-tier class
        create_resp = requests.post(f"{BASE_URL}/processes", json={
            "name": f"downgrade-test-{start_class}",
            "command": "/usr/bin/app",
            "resource_class": start_class
        })
        assert create_resp.status_code == 201
        pid = create_resp.json()["process_id"]

        # 2. Inject the usage pattern to trigger the policy
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": cpu,
            "memory_mb": 500,
            "duration_minutes": duration
        })

        # 3. Trigger rebalancing logic
        rebalance_resp = requests.post(f"{BASE_URL}/admin/rebalance")
        assert rebalance_resp.json()["downgrades"] >= 1

        # 4. Verify the new state and hardware limits
        final_proc = requests.get(f"{BASE_URL}/processes/{pid}").json()
        assert final_proc["resource_class"] == expected_class
        
        # Verify limits updated (Example: STANDARD should be 50% CPU)
        if expected_class == "STANDARD":
            assert final_proc["limits"]["cpu_share_percent"] == 50
        elif expected_class == "BEST_EFFORT":
            assert final_proc["limits"]["cpu_share_percent"] == 20

    finally:
        if pid:
            requests.delete(f"{BASE_URL}/processes/{pid}")


