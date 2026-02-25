**Test Cases List**

| Test Case File | Test Case Name | Description |
| ----- | ----- | ----- |
| functional tests/test\_life\_cycle.py | test\_complete\_process\_lifecycle | Process creation, retrieval, and termination. Verifies process state validation throughout the lifecycle. |
| functional tests/test\_life\_cycle.py | test\_resource\_usage\_query | Resource usage queries. Verifies resource usage tracking by creating a process and subsequently updating its usage metrics. |
| functional tests/test\_life\_cycle.py | test\_admin\_rebalance\_trigger | Verifies the upgrade transition from best effort to standard resource class via a rebalance operation. |
| functional tests/test\_life\_cycle.py | test\_admin\_system\_stats | Retrieves and verifies system statistics. |
| functional tests/test\_life\_cycle.py | test\_invalid\_process\_creation | Tests resource class downgrade transitions, specifically: CRITICAL → STANDARD → BEST\_EFFORT. |
| functional tests/test\_life\_cycle.py | test\_admin\_system\_stats | Verifies the integrity and accuracy of system statistics. |
| functional tests/test\_life\_cycle.py | test\_system\_rule | Ensures system processes consistently maintain the CRITICAL resource class. |
| functional tests/test\_life\_cycle.py | test\_database\_memory\_boost\_on\_creation | Verifies that database processes are allocated a 2x memory boost upon creation. |
| functional tests/test\_life\_cycle.py | test\_invalid\_process\_creation | Assesses process creation failure with invalid JSON input, expecting a 422 error response. |

| Test Function | Requirement Category | Logic Validated |
| :---- | :---- | :---- |
| test\_cpu\_oscillation\_timer\_reset | Rebalancing Edge Cases | Verifies that the 5-minute "High CPU" timer resets if usage drops below 80%. Prevents false-positive downgrades. |
| test\_sequential\_downgrade\_chain | Rebalancing Edge Cases | Validates the "Step-Down" lifecycle: CRITICAL $\\rightarrow$ STANDARD $\\rightarrow$ BEST\_EFFORT. |
| test\_boundary\_conditions\_upgrade | Rebalancing Edge Cases | Checks the "Off-by-One" error at the 50% CPU threshold to ensure upgrades only happen when $\>50\\%$. |
| test\_fault\_injection\_oom\_simulation | Reliability Testing | Simulates an "Out of Memory" (OOM) event by injecting 50GB usage into a 2GB container. |
| test\_fault\_injection\_invalid\_id | Reliability Testing | Ensures the admin API returns 404 Not Found rather than crashing (500) when given a fake UUID. |
| test\_error\_handling\_invalid\_payloads | Error Handling | Validates Pydantic schema enforcement for non-existent classes and empty strings. |
| test\_delete\_idempotency\_reliability | Reliability Testing | Confirms that calling DELETE twice on the same PID is safe (Idempotency). |

| Test Case | Objective | Logic Validated |
| :---- | :---- | :---- |
| test\_complete\_process\_lifecycle | E2E Path | Verifies a process can be created, retrieved, and deleted with the correct HTTP codes (201, 200, 204, 404). |
| test\_resource\_usage\_query | Utilization Stats | Confirms the system calculates utilization math correctly (e.g., $512MB$ usage on $2GB$ limit \= $25.0\\%$). |
| test\_admin\_system\_stats | Data Aggregation | Ensures the global stats endpoint correctly categorizes processes by class and state. |
| test\_invalid\_process\_creation | Negative Testing | Validates that missing mandatory fields (like command) are caught by the schema validator (422). |

| Limit Type | Test Case | Expected Behavior |
| :---- | :---- | :---- |
| Memory Exhaustion | test\_memory\_exhaustion\_violation | POST /update-usage fails with 400 Bad Request when usage \> limit. |
| File Descriptors | test\_fd\_and\_process\_limits\_accuracy | Verifies ulimit \-n is set to 8192 for STANDARD class. |
| Process Count | test\_fd\_and\_process\_limits\_accuracy | Verifies ulimit \-u is set to 1024 for STANDARD class. |

