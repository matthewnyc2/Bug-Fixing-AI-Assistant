"""
Tests for the PR handler module.
"""

import unittest
import tempfile
import subprocess
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from pr-handler directory (note: hyphens in directory names require special handling)
import importlib.util
spec = importlib.util.spec_from_file_location("pr_creator", os.path.join(os.path.dirname(__file__), '..', 'pr-handler', 'pr_creator.py'))
pr_creator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr_creator_module)
PRCreator = pr_creator_module.PRCreator


class TestPRCreator(unittest.TestCase):
    """Test cases for PRCreator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize a git repo
        subprocess.run(['git', 'init'], cwd=self.temp_dir, capture_output=True)
        subprocess.run(
            ['git', 'config', 'user.email', 'test@example.com'],
            cwd=self.temp_dir,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'user.name', 'Test User'],
            cwd=self.temp_dir,
            capture_output=True
        )
        
        # Create initial commit
        test_file = Path(self.temp_dir) / "README.md"
        test_file.write_text("# Test Repo")
        subprocess.run(['git', 'add', 'README.md'], cwd=self.temp_dir, capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit'],
            cwd=self.temp_dir,
            capture_output=True
        )
        
        self.pr_creator = PRCreator(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_branch(self):
        """Test creating a new branch."""
        result = self.pr_creator.create_branch('feature/test-branch')
        self.assertTrue(result['success'])
        self.assertEqual(result['branch'], 'feature/test-branch')
    
    def test_create_existing_branch(self):
        """Test creating a branch that already exists."""
        # Create branch first
        self.pr_creator.create_branch('feature/existing')
        
        # Try to create it again
        result = self.pr_creator.create_branch('feature/existing')
        self.assertFalse(result['success'])
        self.assertIn('already exists', result['message'])
    
    def test_commit_changes(self):
        """Test committing changes."""
        # Create a new file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        result = self.pr_creator.commit_changes('Add test file')
        self.assertTrue(result['success'])
    
    def test_generate_pr_description_empty(self):
        """Test generating PR description with no fixes."""
        description = self.pr_creator.generate_pr_description([], [])
        self.assertIn('Automated Bug Fixes', description)
        self.assertIn('Total issues found: 0', description)
        self.assertIn('Fixes applied: 0', description)
    
    def test_generate_pr_description_with_fixes(self):
        """Test generating PR description with fixes."""
        scan_results = [
            {
                'file': 'test.py',
                'line': 10,
                'type': 'none_comparison',
                'severity': 'warning'
            },
            {
                'file': 'test.py',
                'line': 20,
                'type': 'bare_except',
                'severity': 'warning'
            }
        ]
        
        fixes = [
            {
                'description': 'Fixed None comparison',
                'issue': scan_results[0]
            }
        ]
        
        description = self.pr_creator.generate_pr_description(fixes, scan_results)
        self.assertIn('Total issues found: 2', description)
        self.assertIn('Fixes applied: 1', description)
        self.assertIn('Fixed None comparison', description)
        self.assertIn('Remaining Issues', description)


if __name__ == '__main__':
    unittest.main()
