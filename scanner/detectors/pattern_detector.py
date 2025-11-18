"""
Detector for common Python code patterns and anti-patterns.
"""

import ast
from typing import List, Dict, Any
from pathlib import Path


class PatternDetector(ast.NodeVisitor):
    """
    Detect common code patterns and anti-patterns in Python code.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize the pattern detector.
        
        Args:
            file_path: Path to the file being analyzed
        """
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []
    
    def visit_Compare(self, node: ast.Compare) -> None:
        """
        Check for comparison with None using == instead of is.
        """
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'type': 'none_comparison',
                        'message': 'Use "is None" or "is not None" instead of "== None" or "!= None"',
                        'severity': 'warning'
                    })
        
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """
        Check for bare except clauses.
        """
        if node.type is None:
            self.issues.append({
                'file': str(self.file_path),
                'line': node.lineno,
                'type': 'bare_except',
                'message': 'Bare except clause should specify exception type',
                'severity': 'warning'
            })
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check for mutable default arguments.
        """
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append({
                    'file': str(self.file_path),
                    'line': node.lineno,
                    'type': 'mutable_default_argument',
                    'message': f'Function "{node.name}" has mutable default argument',
                    'severity': 'warning'
                })
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """
        Check for wildcard imports.
        """
        for alias in node.names:
            if alias.name == '*':
                self.issues.append({
                    'file': str(self.file_path),
                    'line': node.lineno,
                    'type': 'wildcard_import',
                    'message': 'Avoid wildcard imports (from module import *)',
                    'severity': 'info'
                })
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Check for wildcard imports in from...import statements.
        """
        for alias in node.names:
            if alias.name == '*':
                self.issues.append({
                    'file': str(self.file_path),
                    'line': node.lineno,
                    'type': 'wildcard_import',
                    'message': f'Avoid wildcard imports (from {node.module} import *)',
                    'severity': 'info'
                })
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[Dict[str, Any]]:
        """
        Get detected issues.
        
        Returns:
            List of detected issues
        """
        return self.issues


def detect_patterns(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """
    Detect code patterns in a Python file.
    
    Args:
        file_path: Path to the file
        content: File content as string
    
    Returns:
        List of detected issues
    """
    try:
        tree = ast.parse(content, filename=str(file_path))
        detector = PatternDetector(file_path)
        detector.visit(tree)
        return detector.get_issues()
    except SyntaxError:
        # Syntax errors are handled by the scanner
        return []
