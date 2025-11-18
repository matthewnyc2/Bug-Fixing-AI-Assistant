"""
Example of fixed code showing how bugs are corrected.

This file demonstrates the corrected versions of the bugs
found in buggy_code.py.
"""


def check_value(value):
    """Check if value is None using correct comparison."""
    # Fixed: Using is instead of == for None comparison
    if value is None:
        return "Value is None"
    return "Value is not None"


def divide_numbers(a, b):
    """Divide two numbers with proper error handling."""
    # Fixed: Specific exception handling
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except TypeError:
        return "Invalid input types"


def process_data(items=None):
    """Process a list of items."""
    # Fixed: Using None as default and creating new list
    if items is None:
        items = []
    items.append("new_item")
    return items


def safe_eval_example(user_input):
    """Example of safe evaluation."""
    # Fixed: Using ast.literal_eval instead of eval
    import ast
    try:
        result = ast.literal_eval(user_input)
        return result
    except (ValueError, SyntaxError):
        return "Invalid input"


def json_example():
    """Example of safe serialization using JSON."""
    import json
    
    # Fixed: Using json instead of pickle for safe serialization
    data = '{"key": "value"}'
    obj = json.loads(data)
    return obj


# Fixed: Explicit imports instead of wildcard
from os import path, getcwd


class Calculator:
    """Simple calculator with proper error handling."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
    
    def divide(self, a, b):
        """Divide a by b with zero division check."""
        # Fixed: Adding zero division check
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
