# Linux Process Resource Manager - SDET Assignment

Welcome to the Linux Process Resource Manager assignment! This assignment is designed to evaluate your skills in test automation and software development.

## IMPORTANT: AI/LLM Usage Policy

**The use of AI/LLM tools (including but not limited to ChatGPT, GitHub Copilot, etc.) is strictly prohibited for this assignment.**

We employ advanced detection tools to identify AI-generated solutions. Any submission found to be generated or significantly assisted by AI/LLM tools will be automatically disqualified. This assignment is designed to evaluate your personal skills and understanding, and we want to ensure a fair evaluation for all candidates.

### What we're looking for:
- Your unique problem-solving approach
- Your understanding of testing principles and Linux resource management
- Your ability to write clean, maintainable code
- Your attention to edge cases and error handling

### What we're not looking for:
- Perfectly polished AI-generated solutions
- Code that doesn't reflect your personal understanding
- Solutions that don't address the specific requirements

## Assignment Overview

This assignment focuses on evaluating your skills in testing a **Linux Process Resource Manager**. The system automatically manages process resource allocations (CPU, memory, file descriptors, I/O) across different resource classes based on usage patterns.

### Two-Part Assignment:
1. **Required**: Test the provided Linux Process Resource Manager implementation
2. **Bonus**: Implement improvements and new features

You are expected to:
- Design and implement a test strategy
- Automate tests for API endpoints
- Report bugs with clarity
- (Optional) Fix known issues or propose improvements

## Getting Started

### Prerequisites

#### Option 1: Python
- Python 3.8+
- pip (Python package manager)
- Git

#### Option 2: Java
- Java 11+
- Maven or Gradle
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gdaggarwal/linux-process-sdet-assignment.git
   cd linux-process-sdet-assignment
   ```

2. **For Python:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **For Java:**
   ```bash
   mvn clean install
   # or
   gradle build
   ```

## Project Structure

```
linux-process-sdet-assignment/
├── docs/                    # Documentation
│   ├── PROBLEM_STATEMENT.md  # Assignment details
│   ├── EVALUATOR_GUIDE.md   # Evaluation process
│   └── EVALUATION.md        # Evaluation criteria
├── src/                     # Source code
│   └── process_manager.py   # Mock process manager service
├── .github/workflows/       # CI/CD workflows
│   └── tests.yml
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Running the Service

Start the mock service:
```bash
python src/process_manager.py
# Service will run on http://localhost:8000
```

API documentation available at: http://localhost:8000/docs

## Running Tests

Run all tests:
```bash
pytest tests/
# or for Java
mvn test
```

Run specific test categories:
```bash
pytest tests/functional/
pytest tests/performance/
pytest tests/fault_injection/
```

## Common Libraries You May Use

### Python
- **Testing Frameworks**: `pytest`, `unittest`, `nose2`
- **HTTP Client**: `requests`, `httpx`
- **Mocking**: `pytest-mock`, `unittest.mock`
- **Concurrency**: `threading`, `asyncio`, `concurrent.futures`
- **Performance**: `pytest-benchmark`, `locust`
- **Coverage**: `pytest-cov`, `coverage`
- **Data Validation**: `pydantic`, `marshmallow`
- **Assertions**: `assertpy`, `hamcrest`

### Java
- **Testing Frameworks**: `JUnit 5`, `TestNG`
- **HTTP Client**: `RestAssured`, `OkHttp`, `Apache HttpClient`
- **Mocking**: `Mockito`, `PowerMock`, `EasyMock`
- **Concurrency**: `ExecutorService`, `CompletableFuture`
- **Performance**: `JMH`, `Gatling`, `JMeter`
- **Assertions**: `AssertJ`, `Hamcrest`
- **JSON Processing**: `Jackson`, `Gson`
- **Build Tools**: `Maven`, `Gradle`

## System Under Test

The Linux Process Resource Manager provides REST APIs to:
- Create and manage processes with resource limits
- Monitor resource usage (CPU, memory, file descriptors, I/O)
- Automatically rebalance resources based on usage patterns
- Enforce resource quotas (ulimits and cgroups)

### Resource Classes:
- **CRITICAL**: Maximum resources (80% CPU, 8GB RAM, 65535 FDs)
- **STANDARD**: Normal allocation (50% CPU, 2GB RAM, 8192 FDs)
- **BEST_EFFORT**: Minimal resources (20% CPU, 512MB RAM, 1024 FDs)

See [PROBLEM_STATEMENT.md](docs/PROBLEM_STATEMENT.md) for detailed API documentation.

## Evaluation

Your submission will be evaluated based on:
1. **Test Strategy (40%)**: Coverage, edge cases, performance approach
2. **Test Implementation (40%)**: Code quality, assertions, advanced techniques
3. **CI/CD Integration (20%)**: Pipeline configuration, reporting

See [EVALUATION.md](docs/EVALUATION.md) for detailed scoring rubric.

## Deliverables

1. Test strategy document (Markdown or Excel)
2. Source code for all tests
3. Bug report(s) in Markdown format
4. Test case documentation (Excel or Markdown)
5. (Optional) CI pipeline configuration

## Time Allocation

**Estimated time**: 4-6 hours

Focus on quality and creativity over quantity. It's better to have fewer, well-designed tests than many superficial ones.

## Submission

1. Fork this repository
2. Implement your solution
3. Ensure all tests pass
4. Create a pull request with your changes
5. Include:
   - Test strategy document
   - Bug reports (at least 1)
   - Test documentation
   - Any additional notes in PR description

## Support

Feel free to reach out during this assignment for questions or clarifications. Also, use public documentation and project README as your guide.

## Important Notes

- You may use **Python, Java, Golang, or any language** you are comfortable with
- Use **pytest, TestNG, JUnit, or any framework** you prefer
- Include at least **2 edge cases** (e.g., resource exhaustion, concurrent operations)
- Automate resource class transitions using mocked usage data
- Document at least **1 bug or improvement** with clear reproduction steps

Good luck!
