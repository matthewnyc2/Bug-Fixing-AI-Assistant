"""
Test runner for validating code changes.
"""

from typing import Dict, Any, List, Optional
import subprocess
import json


class TestRunner:
    """
    Run tests to validate code changes.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the test runner.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.test_results: List[Dict[str, Any]] = []
    
    def run_pytest(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run pytest tests.
        
        Args:
            test_path: Specific test file or directory to run
        
        Returns:
            Test execution results
        """
        cmd = ['pytest', '--verbose', '--tb=short']
        
        if test_path:
            cmd.append(test_path)
        
        return self._execute_test_command(cmd)
    
    def run_unittest(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run unittest tests.
        
        Args:
            test_path: Specific test module to run
        
        Returns:
            Test execution results
        """
        cmd = ['python', '-m', 'unittest', 'discover']
        
        if test_path:
            cmd = ['python', '-m', 'unittest', test_path]
        
        return self._execute_test_command(cmd)
    
    def _execute_test_command(self, cmd: List[str]) -> Dict[str, Any]:
        """
        Execute a test command.
        
        Args:
            cmd: Command to execute as list
        
        Returns:
            Test execution results
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            test_result = {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd)
            }
            
            self.test_results.append(test_result)
            return test_result
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Test execution timed out after 120 seconds',
                'command': ' '.join(cmd)
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'Test command not found: {cmd[0]}',
                'command': ' '.join(cmd)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error executing tests: {str(e)}',
                'command': ' '.join(cmd)
            }
    
    def get_test_summary(self) -> str:
        """
        Get a summary of all test runs.
        
        Returns:
            Summary string
        """
        if not self.test_results:
            return "No tests have been run."
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get('success'))
        failed = total - passed
        
        return f"Test Summary: {passed}/{total} passed, {failed}/{total} failed"
