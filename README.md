# Bug-Fixing-AI-Assistant 🤖🔧

An intelligent AI-powered assistant that automatically scans codebases for bugs, generates fixes using Claude or GPT, validates changes with automated tests, and integrates fixes into your codebase via pull requests.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

## ✨ Features

### 1. 🔍 Intelligent Code Scanning
- **Pattern Detection**: Identifies common code anti-patterns
  - None comparison using `==` instead of `is`
  - Bare except clauses
  - Mutable default arguments
  - Wildcard imports
- **Security Analysis**: Detects security vulnerabilities
  - Dangerous `eval()` and `exec()` usage
  - Unsafe deserialization (pickle)
  - Insecure module imports
- **Code Quality**: Analyzes code quality issues
  - High cyclomatic complexity
  - Too many function arguments
  - Missing docstrings
  - Magic numbers
  - Functions with too many methods (God objects)

### 2. 🤖 AI-Powered Fix Generation
- **Claude Integration**: Uses Anthropic's Claude for intelligent fixes
- **OpenAI Integration**: Supports GPT-4 and GPT-3.5-turbo
- **Context-Aware**: Provides surrounding code context to AI
- **Confidence Scoring**: AI rates fix confidence level
- **Fallback Support**: Falls back to rule-based fixes when AI unavailable

### 3. ⚡ Automated Fix Application
- **Smart Application**: Automatically applies fixes to files
- **Backup Creation**: Creates backups before modifying files
- **Syntax Validation**: Validates fixed code syntax before applying
- **Dry Run Mode**: Preview changes without modifying files
- **Batch Processing**: Apply multiple fixes at once

### 4. ✅ Validation & Testing
- **Python Syntax Validation**: Ensures fixes don't introduce syntax errors
- **Test Execution**: Runs pytest or unittest after fixing
- **Configurable**: Control whether tests must pass
- **Fix Verification**: Validates fixes before committing

### 5. 🔄 Pull Request Integration
- **Automated Branching**: Creates feature branches automatically
- **Smart Commits**: Generates descriptive commit messages
- **PR Descriptions**: Creates detailed PR descriptions with fix summaries
- **Auto-Push**: Optionally pushes to remote automatically
- **GitHub Integration**: Works with gh CLI for PR creation

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/matthewnyc2/Bug-Fixing-AI-Assistant.git
cd Bug-Fixing-AI-Assistant
```

2. **Install dependencies (optional, for AI features):**
```bash
# For Anthropic Claude
pip install anthropic

# For OpenAI GPT
pip install openai

# Or install all optional dependencies
pip install -e ".[full]"
```

3. **Set up your AI API key (optional):**
```bash
# For Anthropic Claude
export ANTHROPIC_API_KEY=your-api-key-here

# For OpenAI GPT
export OPENAI_API_KEY=your-api-key-here
```

### Command Line Usage

#### Basic Scanning (No AI)
```bash
# Scan current directory and show report
python main.py

# Scan a specific directory
python main.py /path/to/your/project

# Generate JSON report
python main.py --report json
```

#### AI-Powered Fixing
```bash
# Scan and generate AI fixes (dry run - no changes)
python main.py --ai --dry-run

# Scan, generate AI fixes, and apply them
python main.py --ai --apply

# Full workflow: scan, fix, test, and create PR
python main.py --ai --apply --run-tests --create-pr
```

#### Using Configuration File
```bash
# Copy example config
cp config.example.yaml config.yaml

# Edit config.yaml with your preferences
# Then run with config
python main.py --config config.yaml --ai --apply
```

### Python API Usage

#### Simple Scanning
```python
from main import BugFixingAssistant

# Create assistant
assistant = BugFixingAssistant()

# Scan directory
issues = assistant.scan_directory('.')

# Print issues
for issue in issues:
    print(f"{issue['type']} at {issue['file']}:{issue['line']}")
```

#### AI-Powered Fixing
```python
from main import BugFixingAssistant
from config import Config

# Create config with AI enabled
config = Config()
config.set('ai.provider', 'anthropic')
config.set('ai.model', 'claude-sonnet-4-5-20250929')

# Create assistant
assistant = BugFixingAssistant(config)

# Scan and fix
issues = assistant.scan_directory('.')
fixes = assistant.generate_fixes(use_ai=True)

# Apply fixes (with backup)
results = assistant.apply_fixes()

# Show what was fixed
for result in results:
    if result['success']:
        print(f"✓ Fixed {result['file']}")
        print(result['diff'])
```

#### Create Pull Request
```python
from main import BugFixingAssistant

assistant = BugFixingAssistant()
issues = assistant.scan_directory('.')
fixes = assistant.generate_fixes()
assistant.apply_fixes()

# Create PR with fixes
pr_result = assistant.create_pr(fixes)
print(pr_result['pr_description'])
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

## 📋 Supported Issue Types

| Issue Type | Severity | Auto-Fix | AI-Fix |
|------------|----------|----------|--------|
| **Pattern Issues** ||||
| None comparison (`==` instead of `is`) | Warning | ✅ Yes | ✅ Yes |
| Bare except clause | Warning | ✅ Yes | ✅ Yes |
| Mutable default argument | Warning | ❌ No | ✅ Yes |
| Wildcard import | Info | ❌ No | ✅ Yes |
| **Security Issues** ||||
| Dangerous `eval()` usage | Critical | ❌ No | ✅ Yes |
| Dangerous `exec()` usage | Critical | ❌ No | ✅ Yes |
| Unsafe pickle deserialization | High | ❌ No | ✅ Yes |
| Insecure module import | Info | ❌ No | ✅ Yes |
| **Quality Issues** ||||
| High cyclomatic complexity | Warning | ❌ No | ✅ Yes |
| Too many function arguments | Info | ❌ No | ✅ Yes |
| Missing docstrings | Info | ❌ No | ✅ Yes |
| Magic numbers | Info | ❌ No | ✅ Yes |
| Too many methods (God object) | Warning | ❌ No | ✅ Yes |
| Assert in production code | Info | ❌ No | ✅ Yes |

**Legend:**
- ✅ Yes = Fully automated fix available
- ❌ No = Requires manual intervention or AI
- AI-Fix = Can be fixed using AI (Claude/GPT)

## 🎯 Roadmap & Future Enhancements

### Completed ✅
- [x] Automated fix application
- [x] AI-powered bug detection and fixing
- [x] Code quality metrics and complexity analysis
- [x] Comprehensive test suite
- [x] Configuration file support
- [x] Pull request automation

### Planned 🚧
- [ ] Support for more programming languages (JavaScript, TypeScript, Java, Go)
- [ ] Integration with CI/CD pipelines (GitHub Actions, GitLab CI)
- [ ] Web dashboard for visualization
- [ ] Custom rule definitions and plugins
- [ ] Performance optimization analysis
- [ ] Dead code detection
- [ ] Dependency vulnerability scanning
- [ ] Integration with issue trackers (Jira, Linear)
- [ ] Multi-file refactoring support
- [ ] Incremental scanning (only changed files)

## License

This project is open source. See LICENSE file for details.

## Contact

For questions or suggestions, please open an issue on GitHub.

