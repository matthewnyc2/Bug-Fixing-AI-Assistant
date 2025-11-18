"""
Validator for generated code fixes.
"""

import ast
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
from pathlib import Path


class FixValidator:
    """
    Validate generated code fixes.
    """
    
    @staticmethod
    def validate_syntax(code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Validate code syntax.
        
        Args:
            code: Code content to validate
            language: Programming language
        
        Returns:
            Validation result dictionary
        """
        if language == 'python':
            return FixValidator._validate_python_syntax(code)
        
        return {
            'valid': False,
            'message': f'Unsupported language: {language}'
        }
    
    @staticmethod
    def _validate_python_syntax(code: str) -> Dict[str, Any]:
        """
        Validate Python code syntax.
        
        Args:
            code: Python code content
        
        Returns:
            Validation result dictionary
        """
        try:
            ast.parse(code)
            return {
                'valid': True,
                'message': 'Syntax is valid'
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'message': f'Syntax error: {e.msg} at line {e.lineno}',
                'line': e.lineno,
                'offset': e.offset
            }
    
    @staticmethod
    def validate_fix(original_code: str, fixed_code: str) -> Dict[str, Any]:
        """
        Validate that a fix doesn't introduce syntax errors.
        
        Args:
            original_code: Original code
            fixed_code: Fixed code
        
        Returns:
            Validation result dictionary
        """
        # Validate fixed code syntax
        syntax_result = FixValidator.validate_syntax(fixed_code)
        
        if not syntax_result['valid']:
            return {
                'valid': False,
                'message': 'Fix introduces syntax errors',
                'details': syntax_result
            }
        
        return {
            'valid': True,
            'message': 'Fix is valid'
        }
    
    @staticmethod
    def run_tests(test_command: str, working_dir: str) -> Dict[str, Any]:
        """
        Run tests to validate fixes.
        
        Args:
            test_command: Command to run tests
            working_dir: Working directory for test execution
        
        Returns:
            Test result dictionary
        """
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Test execution timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error running tests: {str(e)}'
            }
