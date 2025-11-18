# Tests for Bug-Fixing-AI-Assistant

This directory contains comprehensive test suites for all components of the Bug-Fixing-AI-Assistant.

## Test Files

### test_scanner.py
Tests for the core scanner functionality:
- `TestCodeScanner`: Tests for the base CodeScanner class
  - Scanner initialization
  - Finding Python files in directories
  - Scanning valid and invalid Python files
  - Handling syntax errors
  - Result management
- `TestReportGenerator`: Tests for report generation
  - JSON report generation
  - Text report generation
  - Issue counting and categorization

### test_detectors.py
Tests for bug detection modules:
- `TestPatternDetector`: Tests for pattern-based bug detection
  - None comparison detection (== vs is)
  - Bare except clause detection
  - Mutable default argument detection
  - Wildcard import detection
- `TestSecurityDetector`: Tests for security vulnerability detection
  - Dangerous eval() usage
  - Dangerous exec() usage
  - Unsafe pickle.loads() usage
  - Insecure module imports

### test_fixer.py
Tests for fix generation and validation:
- `TestFixGenerator`: Tests for fix generation
  - None comparison fixes
  - Bare except fixes
  - Dangerous eval fixes
  - Handling unsupported issue types
- `TestPatchGenerator`: Tests for patch generation
  - Unified diff generation
  - Simple text replacement
  - Fix summaries
- `TestFixValidator`: Tests for fix validation
  - Python syntax validation
  - Fix validation workflow
  - Test execution

### test_pr_handler.py
Tests for pull request creation:
- `TestPRCreator`: Tests for PR management
  - Branch creation
  - Commit management
  - PR description generation

## Running Tests

### Run all tests
```bash
python -m unittest discover tests -v
```

### Run specific test file
```bash
python -m unittest tests.test_scanner -v
```

### Run specific test class
```bash
python -m unittest tests.test_scanner.TestCodeScanner -v
```

### Run specific test method
```bash
python -m unittest tests.test_scanner.TestCodeScanner.test_scanner_initialization -v
```

## Test Statistics

- **Total Tests**: 38
- **Test Coverage Areas**:
  - Scanner Core: 10 tests
  - Detectors: 9 tests
  - Fixers: 14 tests
  - PR Handler: 5 tests

## Test Requirements

The tests use Python's built-in `unittest` framework, so no additional dependencies are required beyond the standard library.

## Writing New Tests

When adding new functionality:
1. Create or update the appropriate test file
2. Follow the existing test structure and naming conventions
3. Include docstrings explaining what each test validates
4. Run all tests to ensure no regressions
5. Aim for >80% code coverage

## Continuous Integration

These tests are designed to be run in CI/CD pipelines. All tests should pass before merging any pull requests.
