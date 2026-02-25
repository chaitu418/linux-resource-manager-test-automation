# Linux Process Resource Manager - Evaluation Criteria

This document outlines the evaluation criteria for the SDET assignment. The maximum possible score is 100 points.

## Code Authenticity Check (Pass/Fail)

Before evaluation, all submissions will be analyzed for AI-generated code patterns. Submissions that show strong indicators of AI generation will be subject to additional scrutiny and may be disqualified if they violate the assignment's AI usage policy.

### Verification Process
1. Automated analysis using our AI detection tool
2. Manual code review for consistency and understanding
3. Verification of problem-solving approach
4. Check for contextual understanding of the requirements
5. Assessment of Linux system knowledge depth

## Part 1: Testing (100% of base score)

### Code Authenticity (20%)
- [ ] Evidence of original thought and problem-solving (5 points)
- [ ] Consistent coding style throughout (5 points)
- [ ] Appropriate level of comments and documentation (5 points)
- [ ] Understanding of Linux resource management concepts (5 points)

## 1. Test Strategy (40 points)

### 1.1 Test Coverage (15 points)
- [ ] All API endpoints tested (5 points)
  - Process creation, retrieval, deletion
  - Resource usage queries
  - Admin operations (rebalance, stats)

- [ ] Resource class transitions tested (5 points)
  - CRITICAL → STANDARD → BEST_EFFORT
  - Upgrade scenarios (BEST_EFFORT → STANDARD)
  - Special rules (system processes, database processes)

- [ ] Business rule validation (5 points)
  - System processes always stay CRITICAL
  - Database processes get 2x memory
  - Rebalancing based on CPU usage patterns

### 1.2 Edge Case Consideration (10 points)
- [ ] Resource limit violations (3 points)
  - Memory exhaustion
  - File descriptor limits
  - Process count limits

- [ ] Concurrent operations (3 points)
  - Multiple processes created simultaneously
  - Rebalancing during process creation/deletion
  - Resource contention scenarios

- [ ] Rebalancing edge cases (4 points)
  - Oscillating CPU usage (high/low cycles)
  - Multiple downgrades in sequence
  - Processes at class boundaries

### 1.3 Performance Testing Approach (10 points)
- [ ] Rebalancing algorithm efficiency (4 points)
- [ ] Concurrent process creation (3 points)
- [ ] API response time benchmarks (3 points)

### 1.4 Reliability Testing (5 points)
- [ ] Fault injection scenarios (3 points)
- [ ] Error handling validation (2 points)

## 2. Test Implementation (40 points)

### 2.1 Code Quality (10 points)
- [ ] Clean, readable code (3 points)
  - Meaningful variable and function names
  - Proper code structure
  - Consistent formatting

- [ ] Proper error handling (3 points)
  - Expected exceptions caught
  - Error messages validated
  - Cleanup in failure scenarios

- [ ] Code organization (4 points)
  - Logical test file structure
  - Reusable fixtures and helpers
  - Separation of concerns

### 2.2 Test Quality (15 points)
- [ ] Meaningful test names (3 points)
  - Descriptive test function names
  - Clear test documentation

- [ ] Independent test cases (4 points)
  - No dependencies between tests
  - Proper setup and teardown
  - Isolated test data

- [ ] Specific assertions (4 points)
  - Not just status code checks
  - Validate response structure
  - Verify resource limits correctly set
  - Check resource usage values

- [ ] Test data management (4 points)
  - Appropriate test process configurations
  - Realistic resource usage scenarios
  - Edge case data (boundary values)

### 2.3 Advanced Testing (15 points)
- [ ] Concurrency testing (5 points)
  - Parallel process creation
  - Concurrent rebalancing
  - Race condition detection

- [ ] Fault injection (5 points)
  - Resource exhaustion simulation
  - OOM scenarios
  - Process crash during rebalancing
  - Invalid configurations

- [ ] Resource consistency checks (5 points)
  - Resource limits properly enforced
  - Class transitions maintain correct limits
  - Usage tracking accuracy

## 3. CI/CD Integration (20 points)

### 3.1 Pipeline Configuration (10 points)
- [ ] Automated test execution (5 points)
  - Tests run on push/PR
  - Multiple Python versions
  - Proper environment setup

- [ ] Test result reporting (5 points)
  - Clear test output
  - Failure reporting
  - Test duration tracking

### 3.2 Quality Gates (10 points)
- [ ] Test coverage reporting (5 points)
  - Coverage metrics tracked
  - Minimum coverage thresholds
  - Coverage report artifacts

- [ ] Code quality checks (5 points)
  - Linting (optional but recommended)
  - Type checking (optional)
  - Performance benchmarks

## Automated Test Evaluation

We provide an evaluation script that will automatically run and score the test implementation:

```python
def evaluate_implementation():
    results = {
        'test_strategy': evaluate_test_strategy(),
        'test_implementation': evaluate_test_implementation(),
        'ci_cd': evaluate_ci_cd()
    }
    results['total_score'] = (
        results['test_strategy']['score'] * 0.4 +
        results['test_implementation']['score'] * 0.4 +
        results['ci_cd']['score'] * 0.2
    )
    return results
```

## Scoring Rubric

| Score | Description |
|-------|-------------|
| 90-100 | Exceptional - Exceeds all requirements, demonstrates advanced testing techniques and deep Linux knowledge |
| 80-89  | Excellent - Meets all requirements, well-structured tests, good understanding of resource management |
| 70-79  | Good - Meets most requirements, minor issues present, basic Linux knowledge demonstrated |
| 60-69  | Satisfactory - Meets basic requirements, needs improvement in coverage or technique |
| Below 60 | Needs Work - Significant improvements needed |

## Review Process

1. Automated test execution
2. Code review for quality and best practices
3. Manual review of test strategy and documentation
4. Performance evaluation under load
5. Validation of Linux concept understanding

## Common Pitfalls to Avoid

- Not testing resource class transitions
- Ignoring rebalancing logic
- Not testing concurrent process management
- Hard-coded process IDs or resource values
- Lack of proper assertions for resource limits
- Inconsistent test coverage
- Poor error messages in tests
- Not cleaning up test processes
- Misunderstanding CPU share vs CPU limit
- Not testing special business rules (system/database processes)
- Missing fault injection tests
- No performance benchmarks

## Key Testing Scenarios

### Must-Have Test Cases
1. **Basic Process Lifecycle**
   - Create process in each resource class
   - Retrieve process details
   - Delete process

2. **Resource Class Transitions**
   - High CPU usage → downgrade to BEST_EFFORT
   - Low CPU usage → downgrade one class
   - BEST_EFFORT becomes active → upgrade to STANDARD

3. **Special Business Rules**
   - System process stays in CRITICAL regardless of usage
   - Database process gets 2x memory limit

4. **Resource Limits**
   - Verify correct limits set for each class
   - Test resource exhaustion scenarios

5. **Concurrent Operations**
   - Multiple processes created simultaneously
   - Rebalancing with concurrent process operations

6. **Error Handling**
   - Invalid resource class
   - Non-existent process ID
   - Invalid resource configurations

### Nice-to-Have Test Cases
1. Process oscillating between high/low CPU
2. Bulk process creation performance
3. Rebalancing algorithm efficiency benchmarks
4. Resource quota violations
5. OOM handling
6. File descriptor exhaustion

## Submission Guidelines

1. Fork the repository
2. Implement your solution
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request with your changes

## Example Strong Submission Indicators

- Tests demonstrate understanding of cgroups and ulimits
- Comprehensive rebalancing logic tests
- Good use of parametrized tests for multiple resource classes
- Meaningful performance benchmarks
- Well-structured fault injection tests
- Clear test documentation
- Proper CI/CD integration with coverage reporting
- Tests for edge cases like CPU oscillation
- Validation of special business rules
