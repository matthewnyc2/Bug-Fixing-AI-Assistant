"""
Base fix generator for creating code fixes.
"""

from typing import Dict, Any, Optional
import ast


class FixGenerator:
    """
    Base class for generating code fixes.
    """
    
    def __init__(self):
        """Initialize the fix generator."""
        self.fixes = []
    
    def generate_fix(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a fix for a detected issue.
        
        Args:
            issue: Dictionary containing issue information
        
        Returns:
            Dictionary containing fix information or None if no fix available
        """
        issue_type = issue.get('type')
        
        if issue_type == 'none_comparison':
            return self._fix_none_comparison(issue)
        elif issue_type == 'bare_except':
            return self._fix_bare_except(issue)
        elif issue_type == 'dangerous_eval':
            return self._fix_dangerous_eval(issue)
        elif issue_type == 'wildcard_import':
            return self._fix_wildcard_import(issue)
        
        return None
    
    def _fix_none_comparison(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fix for None comparison issue.
        
        Args:
            issue: Issue dictionary
        
        Returns:
            Fix dictionary
        """
        return {
            'issue': issue,
            'fix_type': 'replace',
            'description': 'Replace == None with is None',
            'suggestion': 'Replace "== None" with "is None" or "!= None" with "is not None"',
            'automated': False  # Requires context to determine exact replacement
        }
    
    def _fix_bare_except(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fix for bare except clause.
        
        Args:
            issue: Issue dictionary
        
        Returns:
            Fix dictionary
        """
        return {
            'issue': issue,
            'fix_type': 'replace',
            'description': 'Specify exception type in except clause',
            'suggestion': 'Replace "except:" with "except Exception:" or more specific exception',
            'automated': False  # Requires understanding of context
        }
    
    def _fix_dangerous_eval(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fix for dangerous eval usage.
        
        Args:
            issue: Issue dictionary
        
        Returns:
            Fix dictionary
        """
        return {
            'issue': issue,
            'fix_type': 'refactor',
            'description': 'Remove eval() and use safer alternative',
            'suggestion': 'Consider using ast.literal_eval() for literals or json.loads() for JSON',
            'automated': False  # Requires code refactoring
        }
    
    def _fix_wildcard_import(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fix for wildcard import.
        
        Args:
            issue: Issue dictionary
        
        Returns:
            Fix dictionary
        """
        return {
            'issue': issue,
            'fix_type': 'replace',
            'description': 'Replace wildcard import with explicit imports',
            'suggestion': 'Import only the specific names you need',
            'automated': False  # Requires analyzing what names are actually used
        }
