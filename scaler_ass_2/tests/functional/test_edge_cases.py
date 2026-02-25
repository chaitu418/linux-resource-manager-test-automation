import pytest
import requests
from config import BASE_URL


def test_cpu_oscillation_timer_reset():
    """Rule: >80% for 5 mins. Test: 4 mins high -> 1 min low -> 2 mins high."""
    p = requests.post(f"{BASE_URL}/processes", json={
        "name": "oscillator", "command": "sleep", "resource_class": "STANDARD"
    }).json()
    pid = p["process_id"]

    try:
        # Step 1: 4 mins high CPU
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 90, "duration_minutes": 4
        })
        requests.post(f"{BASE_URL}/admin/rebalance")
        assert requests.get(
            f"{BASE_URL}/processes/{pid}").json()["resource_class"] == "STANDARD"

        # Step 2: 1 min low CPU (Timer should reset here)
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 10, "duration_minutes": 1
        })

        # Step 3: 2 mins high CPU
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 90, "duration_minutes": 2
        })
        requests.post(f"{BASE_URL}/admin/rebalance")

        # ASSERT: Total high time is 6 mins, but consecutive is only 2. Should NOT downgrade.
        final_class = requests.get(
            f"{BASE_URL}/processes/{pid}").json()["resource_class"]
        assert final_class == "STANDARD", "BUG: Timer did not reset after low CPU cycle"
    finally:
        requests.delete(f"{BASE_URL}/processes/{pid}")

def test_sequential_downgrade_chain():
    """
    Test: CRITICAL -> (10m idle) -> STANDARD -> (10m idle) -> BEST_EFFORT.
    Fixes:
    1. Uses 'resource_class' (snake_case) to match your Pydantic CreateProcessRequest.
    2. Uses 'cpu_percent' and 'duration_minutes' to match your UpdateUsageRequest.
    3. Re-sends usage before the second rebalance to ensure state persistence.
    """
    # 1. Create a CRITICAL process
    p_resp = requests.post(f"{BASE_URL}/processes", json={
        "name": "chain-down-proc", 
        "command": "sleep", 
        "resource_class": "CRITICAL"
    })
    assert p_resp.status_code == 201
    p = p_resp.json()
    pid = p["process_id"]

    try:
        # 2. FIRST DOWNGRADE: CRITICAL -> STANDARD
        # We tell the system it has been idle for 11 minutes
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 5.0, 
            "memory_mb": 100,
            "duration_minutes": 11
        })
        
        # Trigger rebalance
        requests.post(f"{BASE_URL}/admin/rebalance")
        
        # Verify first downgrade
        proc_v1 = requests.get(f"{BASE_URL}/processes/{pid}").json()
        assert proc_v1["resource_class"] == "STANDARD", f"Expected STANDARD, got {proc_v1['resource_class']}"

        # 3. SECOND DOWNGRADE: STANDARD -> BEST_EFFORT
        # CRITICAL FIX: In your mock, rebalance might reset durations or require a "fresh" update 
        # to acknowledge the process is STILL idle in its new class.
        requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
            "cpu_percent": 5.0, 
            "memory_mb": 100,
            "duration_minutes": 11 # Keep it idle
        })
        
        requests.post(f"{BASE_URL}/admin/rebalance")
        
        # Verify second downgrade
        proc_v2 = requests.get(f"{BASE_URL}/processes/{pid}").json()
        assert proc_v2["resource_class"] == "BEST_EFFORT", f"Expected BEST_EFFORT, got {proc_v2['resource_class']}"

    finally:
        # Cleanup
        requests.delete(f"{BASE_URL}/processes/{pid}")

def test_boundary_conditions_upgrade():
    """Rule: >50% CPU upgrades. Test: Exactly 50.0%."""
    p = requests.post(f"{BASE_URL}/processes", json={
        "name": "border-proc", "command": "top", "resource_class": "BEST_EFFORT"
    }).json()
    pid = p["process_id"]

    try:
        requests.post(
            f"{BASE_URL}/admin/processes/{pid}/update-usage", json={"cpu_percent": 50.0})
        requests.post(f"{BASE_URL}/admin/rebalance")

        # 50.0 is NOT > 50. It should stay BEST_EFFORT.
        assert requests.get(
            f"{BASE_URL}/processes/{pid}").json()["resource_class"] == "BEST_EFFORT"
    finally:
        requests.delete(f"{BASE_URL}/processes/{pid}")


def test_fault_injection_oom_simulation():
    """
    Scenario: Inject a memory usage value that far exceeds the physical limit.
    Requirement: Fault injection scenarios (3 points).
    """
    # 1. Create a process (STANDARD limit is 2GB)
    p = requests.post(f"{BASE_URL}/processes", json={
        "name": "fault-proc", "command": "sleep", "resource_class": "STANDARD"
    }).json()
    pid = p["process_id"]

    # 2. Inject Fault: Simulate a massive memory spike (e.g., 50GB usage)
    # This should be rejected by the API or handle the 'Crash' gracefully.
    resp = requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
        "cpu_percent": 10,
        "memory_mb": 51200,  # 50GB
        "duration_minutes": 1
    })

    # Assert: The system should not crash; it should return a 400 error.
    assert resp.status_code == 400
    assert "exceeds limit" in resp.json()["detail"].lower()


def test_fault_injection_invalid_id_rebalance():
    """
    Scenario: Attempt to update usage for a non-existent process ID during high load.
    """
    fake_id = "0000-0000-0000"
    resp = requests.post(f"{BASE_URL}/admin/processes/{fake_id}/update-usage", json={
        "cpu_percent": 50, "memory_mb": 100
    })

    # Assert: Graceful 404 instead of a 500 Internal Server Error
    assert resp.status_code == 404


def test_error_handling_invalid_payloads():
    """
    Requirement: Error handling validation (2 points).
    Validates that the system rejects malformed JSON or invalid business logic.
    """
    # 1. Invalid Resource Class
    resp = requests.post(f"{BASE_URL}/processes", json={
        "name": "bad-class",
        "command": "ls",
        "resource_class": "SUPER_CRITICAL"  # Non-existent class
    })
    assert resp.status_code == 422 or resp.status_code == 400

    # 2. Empty Name/Command (Business Logic Validation)
    resp_empty = requests.post(f"{BASE_URL}/processes", json={
        "name": "", "command": "", "resource_class": "STANDARD"
    })
    assert resp_empty.status_code == 400
    assert "cannot be empty" in resp_empty.json()["detail"].lower()


def test_delete_idempotency_reliability():
    """
    Checks if deleting an already deleted process causes a crash.
    Reliability means the system is 'Idempotent'.
    """
    p = requests.post(f"{BASE_URL}/processes",
                      json={"name": "del-test", "command": "ls"}).json()
    pid = p["process_id"]

    # First delete
    requests.delete(f"{BASE_URL}/processes/{pid}")

    # Second delete (Reliability check)
    resp = requests.delete(f"{BASE_URL}/processes/{pid}")

    # Should return 404 (Not Found) or 204 (No Content), but NOT 500 (Server Error)
    assert resp.status_code in [204, 404]
