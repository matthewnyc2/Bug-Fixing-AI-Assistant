# Example Bug Fixes

This directory contains example files demonstrating common bugs and their fixes.

## Files

### buggy_code.py
Contains intentional bugs for demonstration:
- None comparison using `==` instead of `is`
- Bare except clauses
- Mutable default arguments
- Unsafe `eval()` usage
- Unsafe pickle deserialization
- Wildcard imports
- Missing zero division checks

### fixed_code.py
Shows the corrected versions of the bugs:
- Proper None comparison using `is`
- Specific exception handling
- Immutable default arguments
- Safe evaluation using `ast.literal_eval()`
- Safe serialization using JSON
- Explicit imports
- Proper error handling for division

## Usage

Use these examples to:
1. Test the scanner to ensure it detects the bugs
2. Verify the fix generator produces appropriate fixes
3. Validate that the test suite catches regressions
4. Demonstrate the capabilities of Bug-Fixing-AI-Assistant

## Running the Scanner

```bash
python -m scanner.core.scanner examples/buggy_code.py
```

## Expected Issues

The scanner should detect approximately 7-8 issues in `buggy_code.py`:
- 1 None comparison issue
- 1 bare except issue
- 1 mutable default argument issue
- 1 dangerous eval usage
- 1 unsafe pickle usage
- 1 wildcard import
- 1+ potential security issues
