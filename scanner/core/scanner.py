"""
Base scanner class for code analysis.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class CodeScanner:
    """
    Base class for scanning code files for potential bugs.
    """
    
    def __init__(self, root_path: str):
        """
        Initialize the code scanner.
        
        Args:
            root_path: Root directory to scan for code files
        """
        self.root_path = Path(root_path)
        self.results: List[Dict[str, Any]] = []
    
    def scan_directory(self, extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan directory for code files and analyze them.
        
        Args:
            extensions: List of file extensions to scan (e.g., ['.py', '.js'])
        
        Returns:
            List of dictionaries containing scan results
        """
        if extensions is None:
            extensions = ['.py']
        
        code_files = self._find_code_files(extensions)
        
        for file_path in code_files:
            self._scan_file(file_path)
        
        return self.results
    
    def _find_code_files(self, extensions: List[str]) -> List[Path]:
        """
        Find all code files with specified extensions in the directory.
        
        Args:
            extensions: List of file extensions to search for
        
        Returns:
            List of Path objects for matching files
        """
        code_files = []
        
        for ext in extensions:
            code_files.extend(self.root_path.rglob(f'*{ext}'))
        
        return code_files
    
    def _scan_file(self, file_path: Path) -> None:
        """
        Scan a single file for potential issues.
        
        Args:
            file_path: Path to the file to scan
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For Python files, parse AST
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path, content)
        
        except Exception as e:
            self.results.append({
                'file': str(file_path),
                'type': 'scan_error',
                'message': f'Error scanning file: {str(e)}',
                'severity': 'error'
            })
    
    def _analyze_python_file(self, file_path: Path, content: str) -> None:
        """
        Analyze Python file using AST.
        
        Args:
            file_path: Path to the Python file
            content: File content as string
        """
        try:
            tree = ast.parse(content, filename=str(file_path))
            # Base implementation - subclasses will add specific analysis
        except SyntaxError as e:
            self.results.append({
                'file': str(file_path),
                'line': e.lineno,
                'type': 'syntax_error',
                'message': e.msg,
                'severity': 'critical'
            })
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get scan results.
        
        Returns:
            List of scan results
        """
        return self.results
    
    def clear_results(self) -> None:
        """Clear the scan results."""
        self.results = []
