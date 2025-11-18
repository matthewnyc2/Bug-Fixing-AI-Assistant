"""
Tests for the detector modules.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.detectors.pattern_detector import detect_patterns, PatternDetector
from scanner.detectors.security_detector import detect_security_issues, SecurityDetector


class TestPatternDetector(unittest.TestCase):
    """Test cases for PatternDetector."""
    
    def test_detect_none_comparison(self):
        """Test detection of None comparison with ==."""
        code = """
def check(value):
    if value == None:
        return True
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_patterns(temp_file, code)
        
        none_issues = [i for i in issues if i['type'] == 'none_comparison']
        self.assertGreater(len(none_issues), 0)
    
    def test_detect_bare_except(self):
        """Test detection of bare except clause."""
        code = """
def divide(a, b):
    try:
        return a / b
    except:
        return None
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_patterns(temp_file, code)
        
        bare_except = [i for i in issues if i['type'] == 'bare_except']
        self.assertGreater(len(bare_except), 0)
    
    def test_detect_mutable_default(self):
        """Test detection of mutable default argument."""
        code = """
def process(items=[]):
    items.append(1)
    return items
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_patterns(temp_file, code)
        
        mutable_defaults = [i for i in issues if i['type'] == 'mutable_default_argument']
        self.assertGreater(len(mutable_defaults), 0)
    
    def test_detect_wildcard_import(self):
        """Test detection of wildcard imports."""
        code = """
from os import *
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_patterns(temp_file, code)
        
        wildcard_imports = [i for i in issues if i['type'] == 'wildcard_import']
        self.assertGreater(len(wildcard_imports), 0)
    
    def test_no_issues_in_clean_code(self):
        """Test that clean code produces no issues."""
        code = """
def add(a, b):
    return a + b

if __name__ == '__main__':
    print(add(1, 2))
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_patterns(temp_file, code)
        
        self.assertEqual(len(issues), 0)


class TestSecurityDetector(unittest.TestCase):
    """Test cases for SecurityDetector."""
    
    def test_detect_eval_usage(self):
        """Test detection of eval() usage."""
        code = """
def process(user_input):
    result = eval(user_input)
    return result
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_security_issues(temp_file, code)
        
        eval_issues = [i for i in issues if i['type'] == 'dangerous_eval']
        self.assertGreater(len(eval_issues), 0)
    
    def test_detect_exec_usage(self):
        """Test detection of exec() usage."""
        code = """
def run_code(code_str):
    exec(code_str)
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_security_issues(temp_file, code)
        
        exec_issues = [i for i in issues if i['type'] == 'dangerous_exec']
        self.assertGreater(len(exec_issues), 0)
    
    def test_detect_pickle_loads(self):
        """Test detection of pickle.loads() usage."""
        code = """
import pickle

def load_data(data):
    obj = pickle.loads(data)
    return obj
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_security_issues(temp_file, code)
        
        pickle_issues = [i for i in issues if i['type'] in ['unsafe_deserialization', 'insecure_module']]
        self.assertGreater(len(pickle_issues), 0)
    
    def test_no_security_issues_in_safe_code(self):
        """Test that safe code produces no security issues."""
        code = """
import json

def load_data(json_str):
    return json.loads(json_str)
"""
        temp_file = Path(tempfile.gettempdir()) / "test.py"
        issues = detect_security_issues(temp_file, code)
        
        # Should have no critical security issues
        critical = [i for i in issues if i.get('severity') == 'critical']
        self.assertEqual(len(critical), 0)


if __name__ == '__main__':
    unittest.main()
