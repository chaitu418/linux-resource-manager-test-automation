import requests
from concurrent.futures import ThreadPoolExecutor
import pytest
import time
from config import BASE_URL


def test_aggressive_downgrade():
    # Setup: Create Critical Process
    proc = requests.post(f"{BASE_URL}/processes", json={
        "name": "heavy_task", "command": "compute", "resource_class": "CRITICAL"
    }).json()
    p_id = proc["process_id"]

    # 1. Update usage to High CPU for 6 minutes
    requests.post(f"{BASE_URL}/admin/processes/{p_id}/update-usage", json={
        "cpu_percent": 90.0, "memory_mb": 1000, "duration_minutes": 6
    })

    # 2. Trigger Rebalance
    rebalance = requests.post(f"{BASE_URL}/admin/rebalance").json()
    assert rebalance["downgrades"] >= 1

    # 3. Verify Result
    updated_proc = requests.get(f"{BASE_URL}/processes/{p_id}").json()
    assert updated_proc["resource_class"] == "BEST_EFFORT"