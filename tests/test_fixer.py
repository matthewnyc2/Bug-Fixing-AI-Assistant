"""
Tests for the fixer modules.
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fixer.generators.fix_generator import FixGenerator
from fixer.generators.patch_generator import PatchGenerator
from fixer.validators.fix_validator import FixValidator


class TestFixGenerator(unittest.TestCase):
    """Test cases for FixGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = FixGenerator()
    
    def test_generate_none_comparison_fix(self):
        """Test generating fix for None comparison."""
        issue = {
            'type': 'none_comparison',
            'file': 'test.py',
            'line': 5,
            'severity': 'warning'
        }
        
        fix = self.generator.generate_fix(issue)
        self.assertIsNotNone(fix)
        self.assertEqual(fix['fix_type'], 'replace')
        self.assertIn('is None', fix['suggestion'])
    
    def test_generate_bare_except_fix(self):
        """Test generating fix for bare except."""
        issue = {
            'type': 'bare_except',
            'file': 'test.py',
            'line': 10,
            'severity': 'warning'
        }
        
        fix = self.generator.generate_fix(issue)
        self.assertIsNotNone(fix)
        self.assertEqual(fix['fix_type'], 'replace')
        self.assertIn('Exception', fix['suggestion'])
    
    def test_generate_eval_fix(self):
        """Test generating fix for dangerous eval."""
        issue = {
            'type': 'dangerous_eval',
            'file': 'test.py',
            'line': 15,
            'severity': 'critical'
        }
        
        fix = self.generator.generate_fix(issue)
        self.assertIsNotNone(fix)
        self.assertIn('ast.literal_eval', fix['suggestion'])
    
    def test_unsupported_issue_type(self):
        """Test handling of unsupported issue type."""
        issue = {
            'type': 'unknown_issue_type',
            'file': 'test.py',
            'line': 20
        }
        
        fix = self.generator.generate_fix(issue)
        self.assertIsNone(fix)


class TestPatchGenerator(unittest.TestCase):
    """Test cases for PatchGenerator."""
    
    def test_generate_patch(self):
        """Test generating a unified diff patch."""
        original = "def hello():\n    return 'world'"
        fixed = "def hello():\n    return 'universe'"
        
        patch = PatchGenerator.generate_patch(original, fixed, "test.py")
        self.assertIn('test.py', patch)
        self.assertIn('-', patch)
        self.assertIn('+', patch)
    
    def test_apply_simple_replacement(self):
        """Test applying simple text replacement."""
        content = "line 1\nif value == None:\n    pass\n"
        
        result = PatchGenerator.apply_simple_replacement(
            content, 2, "== None", "is None"
        )
        
        self.assertIsNotNone(result)
        self.assertIn("is None", result)
        self.assertNotIn("== None", result)
    
    def test_apply_replacement_invalid_line(self):
        """Test replacement with invalid line number."""
        content = "line 1\nline 2\n"
        
        result = PatchGenerator.apply_simple_replacement(
            content, 10, "old", "new"
        )
        
        self.assertIsNone(result)
    
    def test_create_fix_summary_empty(self):
        """Test creating summary with no fixes."""
        summary = PatchGenerator.create_fix_summary([])
        self.assertEqual(summary, "No fixes applied.")
    
    def test_create_fix_summary_with_fixes(self):
        """Test creating summary with fixes."""
        fixes = [
            {
                'description': 'Fixed None comparison',
                'issue': {'line': 5}
            },
            {
                'description': 'Fixed bare except',
                'issue': {'line': 10}
            }
        ]
        
        summary = PatchGenerator.create_fix_summary(fixes)
        self.assertIn('Applied 2 fix(es)', summary)
        self.assertIn('Fixed None comparison', summary)


class TestFixValidator(unittest.TestCase):
    """Test cases for FixValidator."""
    
    def test_validate_valid_python_syntax(self):
        """Test validating valid Python syntax."""
        code = "def hello():\n    return 'world'"
        
        result = FixValidator.validate_syntax(code, 'python')
        self.assertTrue(result['valid'])
    
    def test_validate_invalid_python_syntax(self):
        """Test validating invalid Python syntax."""
        code = "def hello(\n    return 'world'"
        
        result = FixValidator.validate_syntax(code, 'python')
        self.assertFalse(result['valid'])
        self.assertIn('Syntax error', result['message'])
    
    def test_validate_fix_with_valid_code(self):
        """Test validating a fix that produces valid code."""
        original = "if value == None:\n    pass"
        fixed = "if value is None:\n    pass"
        
        result = FixValidator.validate_fix(original, fixed)
        self.assertTrue(result['valid'])
    
    def test_validate_fix_with_invalid_code(self):
        """Test validating a fix that produces invalid code."""
        original = "if value == None:\n    pass"
        fixed = "if value is None\n    pass"  # Missing colon
        
        result = FixValidator.validate_fix(original, fixed)
        self.assertFalse(result['valid'])
    
    def test_unsupported_language(self):
        """Test validation with unsupported language."""
        code = "console.log('hello');"
        
        result = FixValidator.validate_syntax(code, 'javascript')
        self.assertFalse(result['valid'])
        self.assertIn('Unsupported language', result['message'])


if __name__ == '__main__':
    unittest.main()
