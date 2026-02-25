# Linux Process Resource Manager - SDET Assignment

## Overview
This assignment has two parts:
1. **Main Task**: Design and implement comprehensive test automation for a Linux Process Resource Manager
2. **Bonus Challenge**: Implement additional features and fix identified issues in the service

You'll be working with a system that manages Linux processes and automatically adjusts their resource allocations based on usage patterns and policies.

## Problem Statement

### System Architecture
You'll be testing a Linux Process Resource Manager with the following components:

1. **Process Resource Classes**:
   - **CRITICAL**: Maximum resources (system processes, databases)
     - CPU Share: 80%
     - Memory Limit: 8GB
     - File Descriptors: 65535
     - Max Processes: 4096
     - I/O Weight: 1000

   - **STANDARD**: Normal allocation (web servers, APIs)
     - CPU Share: 50%
     - Memory Limit: 2GB
     - File Descriptors: 8192
     - Max Processes: 1024
     - I/O Weight: 500

   - **BEST_EFFORT**: Minimal resources (batch jobs, background tasks)
     - CPU Share: 20%
     - Memory Limit: 512MB
     - File Descriptors: 1024
     - Max Processes: 256
     - I/O Weight: 100

2. **Resource Rebalancing Policies**:
   - Processes consuming >80% CPU for 5 minutes → downgrade to BEST_EFFORT
   - Processes consuming <20% CPU for 10 minutes → downgrade one class
   - Processes in BEST_EFFORT that become active (>50% CPU) → upgrade to STANDARD
   - System processes (containing `_SYSTEM_` in name) always stay in CRITICAL
   - Database processes get 2x memory limits regardless of class

3. **Resource Limits** (based on ulimits and cgroups):
   - **CPU**: CPU share percentage (cgroups CPU controller)
   - **Memory**: Maximum memory in MB (cgroups memory controller)
   - **File Descriptors**: Maximum open files (ulimit -n)
   - **Process Count**: Maximum number of processes (ulimit -u)
   - **I/O Weight**: I/O priority weight (cgroups I/O controller)

### API Endpoints

#### Process Operations
- `POST /processes` - Create a new managed process
  - Request: `{ "name": "webserver", "command": "/usr/bin/nginx", "resourceClass": "STANDARD" }`
  - Response: `{ "processId": "uuid", "name": "webserver", "resourceClass": "STANDARD", "state": "RUNNING", "resources": {...} }`

- `GET /processes/{processId}` - Get process details
  - Response: `{ "processId": "uuid", "name": "webserver", "state": "RUNNING", "resourceClass": "STANDARD", "uptime": 120, "resources": {...} }`

- `GET /processes/{processId}/resources` - Get detailed resource usage
  - Response: `{ "processId": "uuid", "limits": {...}, "usage": {...}, "utilization": {...} }`

- `DELETE /processes/{processId}` - Terminate a process
  - Response: 204 No Content

#### Admin Operations
- `POST /admin/rebalance` - Manually trigger resource rebalancing
  - Response: `{ "status": "success", "processesRebalanced": 5, "upgrades": 2, "downgrades": 3 }`

- `GET /admin/stats` - Get system statistics
  - Response: `{ "totalProcesses": 100, "critical": { "count": 10, "cpuUsage": "75%" }, ... }`

- `POST /admin/processes/{processId}/update-usage` - Update resource usage (testing only)
  - Request: `{ "cpuPercent": 85, "memoryMB": 1500, "durationMinutes": 6 }`
  - Response: `{ "status": "success", "processId": "uuid" }`

## Part 1: Testing (Required)

### Your Tasks

1. **Test Strategy (30%)**
   - Design a comprehensive test strategy document
   - Identify test scenarios including edge cases
   - Define test data requirements
   - Document your testing approach and rationale

2. **Test Implementation (50%)**
   - Write comprehensive test cases for all API endpoints
   - Include unit, integration, and system tests
   - Test for both happy paths and error conditions
   - Include performance and security test cases where applicable

3. **Bug Report (20%)**
   - Document any issues or bugs you find in the implementation
   - Include steps to reproduce, expected vs actual behavior
   - Suggest potential fixes for critical issues

## Part 2: Implementation (Bonus)

### Bonus Challenges

1. **Fix Identified Issues**
   - The implementation contains several known issues (documented in your bug report)
   - Fix the most critical issues you've identified

2. **Implement New Features**
   - Add process grouping support (manage multiple processes together)
   - Implement resource reservation (pre-allocate resources)
   - Add support for custom resource profiles

3. **Performance Improvements**
   - Optimize the rebalancing algorithm
   - Add pagination to list endpoints
   - Implement caching where appropriate
   - Consider performance and reliability aspects

## Evaluation Focus Areas

1. **Test Strategy (40%)**
   - Completeness of test scenarios
   - Identification of edge cases
   - Performance testing approach
   - Reliability considerations
   - Understanding of Linux resource management concepts

2. **Test Automation (40%)**
   - Implement automated tests for all API endpoints
   - Include tests for resource limit enforcement
   - Implement performance tests for rebalancing operations
   - Add fault injection tests for system reliability
   - Test concurrent process management scenarios
   - Test resource exhaustion scenarios

3. **CI/CD Integration (20%)**
   - Set up GitHub Actions workflow for test execution
   - Include test reporting
   - Add appropriate test coverage reporting

### Deliverables
1. Source code for all test automation
2. Test documentation including test cases and results
3. CI/CD pipeline configuration
4. A README with setup and execution instructions

## Evaluation Criteria

Your submission will be evaluated based on:

1. **Test Strategy (40 points)**
   - Completeness of test scenarios
   - Identification of edge cases
   - Performance testing approach
   - Reliability considerations

2. **Test Implementation (40 points)**
   - Code quality and organization
   - Test coverage
   - Quality of assertions
   - Error handling
   - Concurrency testing

3. **CI/CD Integration (20 points)**
   - Pipeline configuration
   - Test reporting
   - Automation level

## Getting Started

1. Fork this repository
2. Set up your development environment
3. Implement your solution
4. Document your approach and findings
5. Submit a pull request with your changes

## Time Allocation

We expect this assignment to take approximately 4-6 hours to complete. Focus on quality over quantity - it's better to have fewer, well-thought-out tests than many superficial ones.

## Important Concepts to Test

### Resource Limit Edge Cases
- What happens when a process exceeds its memory limit?
- How does the system handle file descriptor exhaustion?
- What happens when CPU usage spikes suddenly?

### Rebalancing Scenarios
- Process oscillating between high and low CPU usage
- Multiple processes competing for resources
- System processes attempting to be downgraded

### Concurrent Operations
- Creating multiple processes simultaneously
- Rebalancing while processes are being created/deleted
- Multiple rebalance operations triggered concurrently

### Error Conditions
- Invalid resource class specifications
- Attempting to create processes with invalid configurations
- Resource quota violations
- Process termination during rebalancing

## Questions?

If you have any questions about the assignment, please open an issue in the repository.
