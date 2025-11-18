"""
Detector for security vulnerabilities in Python code.
"""

import ast
from typing import List, Dict, Any
from pathlib import Path


class SecurityDetector(ast.NodeVisitor):
    """
    Detect potential security vulnerabilities in Python code.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize the security detector.
        
        Args:
            file_path: Path to the file being analyzed
        """
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []
    
    def visit_Call(self, node: ast.Call) -> None:
        """
        Check for dangerous function calls.
        """
        # Check for eval() usage
        if isinstance(node.func, ast.Name) and node.func.id == 'eval':
            self.issues.append({
                'file': str(self.file_path),
                'line': node.lineno,
                'type': 'dangerous_eval',
                'message': 'Use of eval() is dangerous and should be avoided',
                'severity': 'critical'
            })
        
        # Check for exec() usage
        if isinstance(node.func, ast.Name) and node.func.id == 'exec':
            self.issues.append({
                'file': str(self.file_path),
                'line': node.lineno,
                'type': 'dangerous_exec',
                'message': 'Use of exec() is dangerous and should be avoided',
                'severity': 'critical'
            })
        
        # Check for pickle.loads() usage
        if isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'pickle' and 
                node.func.attr == 'loads'):
                self.issues.append({
                    'file': str(self.file_path),
                    'line': node.lineno,
                    'type': 'unsafe_deserialization',
                    'message': 'pickle.loads() can execute arbitrary code; use with caution',
                    'severity': 'high'
                })
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """
        Check for imports of deprecated or insecure modules.
        """
        for alias in node.names:
            if alias.name == 'pickle':
                self.issues.append({
                    'file': str(self.file_path),
                    'line': node.lineno,
                    'type': 'insecure_module',
                    'message': 'pickle module can be unsafe; consider using json instead',
                    'severity': 'info'
                })
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[Dict[str, Any]]:
        """
        Get detected security issues.
        
        Returns:
            List of detected security issues
        """
        return self.issues


def detect_security_issues(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """
    Detect security issues in a Python file.
    
    Args:
        file_path: Path to the file
        content: File content as string
    
    Returns:
        List of detected security issues
    """
    try:
        tree = ast.parse(content, filename=str(file_path))
        detector = SecurityDetector(file_path)
        detector.visit(tree)
        return detector.get_issues()
    except SyntaxError:
        # Syntax errors are handled by the scanner
        return []
