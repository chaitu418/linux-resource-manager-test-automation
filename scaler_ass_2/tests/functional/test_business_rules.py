import requests
import pytest
from config import BASE_URL


def test_database_memory_multiplier():
    """Verify Database processes get 2x memory limit (STANDARD: 2048 -> 4096)."""
    payload = {"name": "prod_postgres_db",
               "command": "pg_start", "resource_class": "STANDARD"}
    res = requests.post(f"{BASE_URL}/processes", json=payload).json()

    # Standard is 2048, DB should be 4096
    assert res["limits"]["memory_limit_mb"] == 4096


def test_system_process_initial_class():
    """Verify _SYSTEM_ name forces CRITICAL class regardless of input."""
    payload = {"name": "OS_SYSTEM_DAEMON",
               "command": "init", "resource_class": "BEST_EFFORT"}
    res = requests.post(f"{BASE_URL}/processes", json=payload).json()

    assert res["resource_class"] == "CRITICAL"


def test_critical_to_best_effort_transition():
    # 1. Create a Critical Process
    payload = {"name": "hive-metastore-mock",
               "command": "java -jar ...", "resource_class": "CRITICAL"}
    resp = requests.post(f"{BASE_URL}/processes", json=payload)
    proc_id = resp.json()["process_id"]

    # 2. Simulate high resource usage for a long duration
    usage_update = {"cpu_percent": 95.0,
                    "memory_mb": 4096, "duration_minutes": 30}
    requests.post(
        f"{BASE_URL}/admin/processes/{proc_id}/update-usage", json=usage_update)

    # 3. Trigger Admin Rebalance
    requests.post(f"{BASE_URL}/admin/rebalance")

    # 4. Assert Transition
    updated_proc = requests.get(f"{BASE_URL}/processes/{proc_id}").json()
    assert updated_proc["resource_class"] != "CRITICAL"
    # Logic check: High usage for long duration should downgrade to BEST_EFFORT or STANDARD
    assert updated_proc["limits"]["cpu_share_percent"] < 100


def test_memory_exhaustion_violation():
    """
    Validates that usage updates exceeding the class limit are rejected.
    BEST_EFFORT limit is 512MB.
    """
    # 1. Create a BEST_EFFORT process
    create_resp = requests.post(f"{BASE_URL}/processes", json={
        "name": "limit-test-proc",
        "command": "sleep",
        "resource_class": "BEST_EFFORT"
    }).json()
    pid = create_resp["process_id"]

    # 2. Attempt to update usage to 600MB (Limit is 512)
    # Expected: 400 Bad Request
    usage_resp = requests.post(f"{BASE_URL}/admin/processes/{pid}/update-usage", json={
        "cpu_percent": 10,
        "memory_mb": 600,
        "duration_minutes": 1
    })

    assert usage_resp.status_code == 400
    assert "exceeds limit" in usage_resp.json()["detail"].lower()

    # Cleanup
    requests.delete(f"{BASE_URL}/processes/{pid}")


def test_fd_and_process_limits_accuracy():
    """
    Validates that the system assigns the correct FD and Process limits.
    STANDARD: 8192 FDs, 1024 Max Processes.
    """
    resp = requests.post(f"{BASE_URL}/processes", json={
        "name": "standard-app",
        "command": "nginx",
        "resource_class": "STANDARD"
    }).json()
    pid = resp["process_id"]

    # Query resource details
    res_data = requests.get(f"{BASE_URL}/processes/{pid}/resources").json()

    assert res_data["limits"]["max_file_descriptors"] == 8192
    assert res_data["limits"]["max_processes"] == 1024

    requests.delete(f"{BASE_URL}/processes/{pid}")
