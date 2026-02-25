Test Strategy: Linux Process Resource Manager
1. Overview
The primary objective of this test suite is to rigorously validate the lifecycle management, resource allocation mechanisms, and dynamic rebalancing logic implemented within the Linux Process Resource Manager. The central focus is to ensure accurate process categorization, strict enforcement of resource limits via cgroups/ulimits, and maintenance of system stability under anticipated operational load.
2. Test Scope and Coverage
2.1 Functional Testing (API Endpoints)
Process Lifecycle: Validate the operations of POST /processes, GET /processes/{id}, and DELETE /processes/{id}.
Resource Queries: Ensure that usage statistics for CPU, Memory, and File Descriptors (FDs) return precise, real-time data.
Administrative Operations: Trigger manual resource rebalancing and retrieve system-wide usage metrics.
2.2 Business Rule Validation
Class Limits: Verify adherence to the established hardware constraints for each process class:
CRITICAL: 80%
STANDARD: 50%
BEST EFFORT: 20%
Special Rules:
System processes shall retain the CRITICAL classification irrespective of current low resource consumption.
Database processes shall be allocated a memory resource that is twice (2x) the limit of their assigned class.
2.3 Transition and Rebalancing Logic
Downgrade Path: Simulate elevated CPU usage to trigger the classification transition sequence: CRITICAL → STANDARD → BEST_EFFORT.
Upgrade Path: Simulate an active status for a BEST_EFFORT process to facilitate its promotion to the STANDARD classification.
Boundary Testing: Test processes at the precise resource usage thresholds (e.g., 49.9% versus 50.1% of CPU limit).

3. Edge Case and Reliability Testing
3.1 Resource Exhaustion (Fault Injection)
Memory OOM (Out-of-Memory): Simulate a process request for 9GB of RAM within the CRITICAL class limits.
FD Leak: Instigate a process to attempt the opening of 10,000 files while classified as STANDARD (where the limit is 8192).
Process Saturation: Attempt to provision processes in excess of the configured maximum allowance for concurrent processes.
3.2 Concurrency & Race Conditions
Parallel Creation: Employ threading or asynchronous operations (asyncio) to create 50 processes simultaneously.
Collision Testing: Trigger a rebalance operation concurrently with the initiation of a process deletion.
4. Performance Testing Approach
Response Benchmarking: Measure the API response latency for GET /stats under a simulated load of 100 or more active processes.
Rebalance Efficiency: Quantify the time required for the system to reclassify 100 processes subsequent to a rapid resource usage spike.
Stability: Continuously monitor the process_manager.py service itself for potential memory leaks during extended, long-running test execution.
5. Test Implementation Details
Framework: Python utilizing the pytest framework.
Mocking: Employ unittest.mock to simulate Linux kernel usage data (e.g., CPU/RAM consumption), as this refers to a simulated service environment.
Fixtures: Utilize pytest.fixture for:
Automatic setup (service initiation).
Teardown (cleanup and termination of orphaned processes).
Reporting: Integrate pytest-cov for code coverage analysis and pytest-html for generating visual result logs.
6. CI/CD Integration
GitHub Actions: Define the continuous integration pipeline within the .github/workflows/tests.yml configuration file.
Triggers: The test suite shall execute upon every code push and pull request event.
Artifacts: Store coverage reports and logs of failed tests, retaining them for a period of 14 days.

