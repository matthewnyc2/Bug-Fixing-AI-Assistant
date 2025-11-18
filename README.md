# Bug-Fixing-AI-Assistant

An AI assistant dedicated to scanning codebases for bugs, generating fixes autonomously, validating changes with automated tests, and integrating fixes into the codebase via pull requests.

## Project Structure

```
Bug-Fixing-AI-Assistant/
├── scanner/                 # Code scanning and bug detection
│   ├── core/               # Core scanning functionality
│   │   ├── scanner.py      # Base scanner class
│   │   └── report.py       # Report generation
│   └── detectors/          # Bug detection modules
│       ├── pattern_detector.py    # Pattern-based bug detection
│       └── security_detector.py   # Security vulnerability detection
├── fixer/                  # Bug fixing and code generation
│   ├── generators/         # Fix generation modules
│   │   ├── fix_generator.py      # Base fix generator
│   │   └── patch_generator.py    # Patch and diff generation
│   └── validators/         # Fix validation modules
│       ├── fix_validator.py      # Fix syntax validation
│       └── test_runner.py        # Test execution
├── pr-handler/             # Pull request management
│   └── pr_creator.py       # PR creation and management
├── examples/               # Example buggy and fixed code
│   ├── buggy_code.py       # Intentionally buggy code samples
│   ├── fixed_code.py       # Fixed versions of buggy code
│   └── README.md           # Example documentation
└── tests/                  # Comprehensive test suite
    ├── test_scanner.py     # Scanner tests
    ├── test_detectors.py   # Detector tests
    ├── test_fixer.py       # Fixer tests
    ├── test_pr_handler.py  # PR handler tests
    └── README.md           # Test documentation
```

## Features

### 1. Code Scanning
- **Pattern Detection**: Identifies common code anti-patterns
  - None comparison using `==` instead of `is`
  - Bare except clauses
  - Mutable default arguments
  - Wildcard imports
- **Security Analysis**: Detects security vulnerabilities
  - Dangerous `eval()` and `exec()` usage
  - Unsafe deserialization (pickle)
  - Insecure module imports

### 2. Automated Fixes
- Generate fixes for detected issues
- Create unified diff patches
- Validate fixes with syntax checking
- Support for multiple fix strategies

### 3. Validation
- Python syntax validation
- Test execution framework
- Fix verification before applying

### 4. Pull Request Integration
- Automated branch creation
- Commit management
- PR description generation with detailed fix summaries

## Quick Start

### Installation

Clone the repository:
```bash
git clone https://github.com/matthewnyc2/Bug-Fixing-AI-Assistant.git
cd Bug-Fixing-AI-Assistant
```

### Usage Examples

#### Scan a file for bugs
```python
from scanner.core.scanner import CodeScanner
from scanner.core.report import ReportGenerator

# Create scanner
scanner = CodeScanner('/path/to/your/code')

# Scan for Python files
results = scanner.scan_directory(['.py'])

# Generate report
report = ReportGenerator.generate_text_report(results)
print(report)
```

#### Detect specific patterns
```python
from scanner.detectors.pattern_detector import detect_patterns
from pathlib import Path

# Read file
file_path = Path('examples/buggy_code.py')
with open(file_path, 'r') as f:
    content = f.read()

# Detect issues
issues = detect_patterns(file_path, content)
print(f'Found {len(issues)} issues')
```

#### Generate fixes
```python
from fixer.generators.fix_generator import FixGenerator

generator = FixGenerator()

# Generate fix for an issue
issue = {
    'type': 'none_comparison',
    'file': 'test.py',
    'line': 10,
    'severity': 'warning'
}

fix = generator.generate_fix(issue)
print(fix['suggestion'])
```

#### Validate fixes
```python
from fixer.validators.fix_validator import FixValidator

# Validate fixed code
result = FixValidator.validate_syntax("def hello():\n    return 'world'")
print(f"Valid: {result['valid']}")
```

## Running Tests

Run all tests:
```bash
python -m unittest discover tests -v
```

Run specific test suite:
```bash
python -m unittest tests.test_scanner -v
python -m unittest tests.test_detectors -v
python -m unittest tests.test_fixer -v
python -m unittest tests.test_pr_handler -v
```

## Examples

The `examples/` directory contains sample files demonstrating the assistant's capabilities:

- **buggy_code.py**: Contains intentional bugs for testing
- **fixed_code.py**: Shows corrected versions of the bugs
- **README.md**: Detailed explanation of each bug and fix

Test the scanner on examples:
```bash
python -c "
from scanner.detectors.pattern_detector import detect_patterns
from scanner.detectors.security_detector import detect_security_issues
from pathlib import Path

file_path = Path('examples/buggy_code.py')
with open(file_path) as f:
    content = f.read()

issues = detect_patterns(file_path, content) + detect_security_issues(file_path, content)
print(f'Found {len(issues)} issues')
"
```

## Development

### Project Requirements

- Python 3.7+
- No external dependencies for core functionality
- Uses Python standard library only

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## Architecture

### Scanner Module
The scanner module is responsible for analyzing code and detecting potential issues. It uses Python's `ast` module for syntax tree analysis.

### Fixer Module
The fixer module generates suggested fixes for detected issues. It includes validators to ensure fixes don't introduce new problems.

### PR Handler Module
The PR handler automates the process of creating pull requests with fixes, including branch management and commit operations.

## Supported Issue Types

| Issue Type | Severity | Auto-Fix |
|------------|----------|----------|
| None comparison | Warning | Manual |
| Bare except | Warning | Manual |
| Mutable default argument | Warning | Manual |
| Wildcard import | Info | Manual |
| Dangerous eval() | Critical | Manual |
| Dangerous exec() | Critical | Manual |
| Unsafe pickle | High | Manual |

## Future Enhancements

- [ ] Automated fix application
- [ ] Support for more programming languages
- [ ] Integration with CI/CD pipelines
- [ ] Machine learning-based bug detection
- [ ] Performance optimization analysis
- [ ] Code complexity metrics
- [ ] Custom rule definitions

## License

This project is open source. See LICENSE file for details.

## Contact

For questions or suggestions, please open an issue on GitHub.

