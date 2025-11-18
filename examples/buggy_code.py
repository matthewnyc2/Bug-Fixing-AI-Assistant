"""
Example buggy code for demonstration purposes.

This file contains intentional bugs that the Bug-Fixing-AI-Assistant
can detect and fix.
"""


def check_value(value):
    """Check if value is None using incorrect comparison."""
    # Bug: Using == instead of is for None comparison
    if value == None:
        return "Value is None"
    return "Value is not None"


def divide_numbers(a, b):
    """Divide two numbers with poor error handling."""
    # Bug: Bare except clause
    try:
        result = a / b
        return result
    except:
        return "Error occurred"


def process_data(items=[]):
    """Process a list of items."""
    # Bug: Mutable default argument
    items.append("new_item")
    return items


def unsafe_eval_example(user_input):
    """Example of unsafe eval usage."""
    # Bug: Using eval on user input
    result = eval(user_input)
    return result


def pickle_example():
    """Example of unsafe deserialization."""
    import pickle
    
    # Bug: Using pickle which can be unsafe
    data = b'\x80\x03}q\x00.'
    obj = pickle.loads(data)
    return obj


# Bug: Wildcard import
from os import *


class Calculator:
    """Simple calculator with bugs."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
    
    def divide(self, a, b):
        """Divide a by b."""
        # Bug: No zero division check
        return a / b
