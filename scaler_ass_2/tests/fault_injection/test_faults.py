import requests
import pytest
from config import BASE_URL

def test_system_process_immunity():
    """Verify system processes do NOT downgrade even with low CPU usage."""
    proc = requests.post(f"{BASE_URL}/processes", json={
        "name": "MY_SYSTEM_SVC", "command": "kernel", "resource_class": "CRITICAL"
    }).json()
    p_id = proc["process_id"]

    # Simulate 15 minutes of 5% CPU usage
    requests.post(f"{BASE_URL}/admin/processes/{p_id}/update-usage", json={
        "cpu_percent": 5.0, "memory_mb": 100, "duration_minutes": 15
    })

    requests.post(f"{BASE_URL}/admin/rebalance")
    
    updated_proc = requests.get(f"{BASE_URL}/processes/{p_id}").json()
    assert updated_proc["resource_class"] == "CRITICAL" # Should not change