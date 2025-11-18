"""
Tests for the scanner core functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.core.scanner import CodeScanner
from scanner.core.report import ReportGenerator


class TestCodeScanner(unittest.TestCase):
    """Test cases for CodeScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = CodeScanner(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        self.assertEqual(str(self.scanner.root_path), self.temp_dir)
        self.assertEqual(len(self.scanner.results), 0)
    
    def test_find_python_files(self):
        """Test finding Python files in directory."""
        # Create test files
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")
        
        files = self.scanner._find_code_files(['.py'])
        self.assertEqual(len(files), 1)
        self.assertTrue(str(files[0]).endswith('test.py'))
    
    def test_scan_valid_python_file(self):
        """Test scanning valid Python file."""
        test_file = Path(self.temp_dir) / "valid.py"
        test_file.write_text("def hello():\n    return 'world'")
        
        results = self.scanner.scan_directory()
        # Valid file should produce no errors
        syntax_errors = [r for r in results if r['type'] == 'syntax_error']
        self.assertEqual(len(syntax_errors), 0)
    
    def test_scan_invalid_python_file(self):
        """Test scanning invalid Python file."""
        test_file = Path(self.temp_dir) / "invalid.py"
        test_file.write_text("def hello(\n    return 'world'")
        
        results = self.scanner.scan_directory()
        syntax_errors = [r for r in results if r['type'] == 'syntax_error']
        self.assertGreater(len(syntax_errors), 0)
    
    def test_clear_results(self):
        """Test clearing scan results."""
        self.scanner.results = [{'test': 'data'}]
        self.scanner.clear_results()
        self.assertEqual(len(self.scanner.results), 0)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def test_generate_json_report_empty(self):
        """Test generating JSON report with no issues."""
        report = ReportGenerator.generate_json_report([])
        self.assertIn('"total_issues": 0', report)
    
    def test_generate_json_report_with_issues(self):
        """Test generating JSON report with issues."""
        issues = [
            {
                'file': 'test.py',
                'line': 10,
                'type': 'test_issue',
                'severity': 'warning',
                'message': 'Test message'
            }
        ]
        
        report = ReportGenerator.generate_json_report(issues)
        self.assertIn('"total_issues": 1', report)
        self.assertIn('test_issue', report)
    
    def test_generate_text_report_empty(self):
        """Test generating text report with no issues."""
        report = ReportGenerator.generate_text_report([])
        self.assertEqual(report, "No issues found.")
    
    def test_generate_text_report_with_issues(self):
        """Test generating text report with issues."""
        issues = [
            {
                'file': 'test.py',
                'line': 10,
                'type': 'test_issue',
                'severity': 'warning',
                'message': 'Test message'
            }
        ]
        
        report = ReportGenerator.generate_text_report(issues)
        self.assertIn('Total Issues: 1', report)
        self.assertIn('test.py', report)
        self.assertIn('Line: 10', report)
    
    def test_count_by_severity(self):
        """Test counting issues by severity."""
        issues = [
            {'severity': 'critical'},
            {'severity': 'warning'},
            {'severity': 'warning'},
            {'severity': 'info'}
        ]
        
        counts = ReportGenerator._count_by_severity(issues)
        self.assertEqual(counts['critical'], 1)
        self.assertEqual(counts['warning'], 2)
        self.assertEqual(counts['info'], 1)


if __name__ == '__main__':
    unittest.main()
