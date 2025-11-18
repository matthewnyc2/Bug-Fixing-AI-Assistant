"""
Code patch generator for automated fixes.
"""

from typing import Dict, Any, List, Optional
import difflib


class PatchGenerator:
    """
    Generate patches for code fixes.
    """
    
    @staticmethod
    def generate_patch(original_code: str, fixed_code: str, file_path: str) -> str:
        """
        Generate a unified diff patch.
        
        Args:
            original_code: Original code content
            fixed_code: Fixed code content
            file_path: Path to the file
        
        Returns:
            Unified diff as string
        """
        original_lines = original_code.splitlines(keepends=True)
        fixed_lines = fixed_code.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f'a/{file_path}',
            tofile=f'b/{file_path}',
            lineterm=''
        )
        
        return ''.join(diff)
    
    @staticmethod
    def apply_simple_replacement(
        content: str,
        line_number: int,
        old_text: str,
        new_text: str
    ) -> Optional[str]:
        """
        Apply a simple text replacement at a specific line.
        
        Args:
            content: Original file content
            line_number: Line number to modify (1-indexed)
            old_text: Text to replace
            new_text: Replacement text
        
        Returns:
            Modified content or None if replacement failed
        """
        lines = content.splitlines(keepends=True)
        
        if line_number < 1 or line_number > len(lines):
            return None
        
        line_idx = line_number - 1
        if old_text in lines[line_idx]:
            lines[line_idx] = lines[line_idx].replace(old_text, new_text)
            return ''.join(lines)
        
        return None
    
    @staticmethod
    def create_fix_summary(fixes: List[Dict[str, Any]]) -> str:
        """
        Create a summary of applied fixes.
        
        Args:
            fixes: List of fix dictionaries
        
        Returns:
            Summary string
        """
        if not fixes:
            return "No fixes applied."
        
        summary_lines = [
            f"Applied {len(fixes)} fix(es):",
            ""
        ]
        
        for idx, fix in enumerate(fixes, 1):
            issue = fix.get('issue', {})
            summary_lines.append(
                f"{idx}. {fix.get('description', 'Unknown fix')} "
                f"(Line {issue.get('line', 'N/A')})"
            )
        
        return "\n".join(summary_lines)
