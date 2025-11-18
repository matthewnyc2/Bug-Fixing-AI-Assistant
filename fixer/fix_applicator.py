"""
Automated fix applicator for applying fixes to code files.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import difflib


class FixApplicator:
    """
    Apply automated fixes to code files.
    """

    def __init__(self, create_backup: bool = True, backup_suffix: str = ".backup"):
        """
        Initialize the fix applicator.

        Args:
            create_backup: Whether to create backup files before applying fixes
            backup_suffix: Suffix to add to backup files
        """
        self.create_backup = create_backup
        self.backup_suffix = backup_suffix
        self.applied_fixes: List[Dict[str, Any]] = []

    def apply_fix(self, fix: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply a single fix to a file.

        Args:
            fix: Fix dictionary containing issue and fix information
            dry_run: If True, don't actually modify files

        Returns:
            Result dictionary with success status
        """
        issue = fix.get("issue", {})
        file_path = issue.get("file")

        if not file_path or not Path(file_path).exists():
            return {
                "success": False,
                "message": f"File not found: {file_path}",
                "fix": fix,
            }

        try:
            # Read original file
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Apply the fix
            fixed_content = self._apply_fix_to_content(fix, original_content)

            if fixed_content is None:
                return {
                    "success": False,
                    "message": "Could not apply fix to content",
                    "fix": fix,
                }

            # Validate syntax of fixed code
            from fixer.validators.fix_validator import FixValidator

            validation = FixValidator.validate_syntax(fixed_content)

            if not validation["valid"]:
                return {
                    "success": False,
                    "message": f"Fix introduces syntax errors: {validation['message']}",
                    "fix": fix,
                    "validation": validation,
                }

            if not dry_run:
                # Create backup if requested
                if self.create_backup:
                    backup_path = f"{file_path}{self.backup_suffix}"
                    shutil.copy2(file_path, backup_path)

                # Write fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                self.applied_fixes.append(fix)

            # Generate diff for reference
            diff = self._generate_diff(original_content, fixed_content, file_path)

            return {
                "success": True,
                "message": "Fix applied successfully",
                "fix": fix,
                "file": file_path,
                "diff": diff,
                "dry_run": dry_run,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error applying fix: {str(e)}",
                "fix": fix,
                "error": str(e),
            }

    def _apply_fix_to_content(
        self, fix: Dict[str, Any], content: str
    ) -> Optional[str]:
        """
        Apply a fix to file content.

        Args:
            fix: Fix dictionary
            content: Original file content

        Returns:
            Fixed content or None if fix cannot be applied
        """
        issue = fix.get("issue", {})
        changes = fix.get("changes", [])

        if not changes:
            # Try to apply simple fix based on suggestion
            return self._apply_simple_fix(fix, content)

        # Apply multiple changes
        lines = content.splitlines(keepends=True)

        # Sort changes by line number in reverse order to avoid offset issues
        sorted_changes = sorted(changes, key=lambda x: x.get("line_number", 0), reverse=True)

        for change in sorted_changes:
            line_num = change.get("line_number")
            new_code = change.get("new_code")

            if line_num and new_code is not None:
                if 1 <= line_num <= len(lines):
                    # Replace the line
                    lines[line_num - 1] = new_code if new_code.endswith("\n") else new_code + "\n"

        return "".join(lines)

    def _apply_simple_fix(self, fix: Dict[str, Any], content: str) -> Optional[str]:
        """
        Apply a simple fix based on issue type and suggestion.

        Args:
            fix: Fix dictionary
            content: Original file content

        Returns:
            Fixed content or None
        """
        issue = fix.get("issue", {})
        issue_type = issue.get("type")
        line_number = issue.get("line")

        if not line_number:
            return None

        lines = content.splitlines(keepends=True)
        if line_number < 1 or line_number > len(lines):
            return None

        line_idx = line_number - 1
        original_line = lines[line_idx]

        # Apply type-specific fixes
        if issue_type == "none_comparison":
            fixed_line = original_line.replace("== None", "is None").replace("!= None", "is not None")
            lines[line_idx] = fixed_line
            return "".join(lines)

        elif issue_type == "bare_except":
            # Replace bare except with except Exception
            if "except:" in original_line:
                fixed_line = original_line.replace("except:", "except Exception:")
                lines[line_idx] = fixed_line
                return "".join(lines)

        elif issue_type == "wildcard_import":
            # This is complex and requires knowing what names are used
            # For now, return None to indicate manual fix needed
            return None

        # For AI-generated fixes with a suggestion
        suggestion = fix.get("suggestion", "")
        if suggestion and len(suggestion.splitlines()) == 1:
            # Single-line suggestion, replace the line
            lines[line_idx] = suggestion if suggestion.endswith("\n") else suggestion + "\n"
            return "".join(lines)

        return None

    def _generate_diff(
        self, original: str, fixed: str, filename: str
    ) -> str:
        """
        Generate a unified diff between original and fixed content.

        Args:
            original: Original content
            fixed: Fixed content
            filename: File name for diff headers

        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm="",
        )

        return "".join(diff)

    def apply_fixes_batch(
        self, fixes: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Apply multiple fixes.

        Args:
            fixes: List of fix dictionaries
            dry_run: If True, don't actually modify files

        Returns:
            List of result dictionaries
        """
        results = []
        for fix in fixes:
            result = self.apply_fix(fix, dry_run=dry_run)
            results.append(result)
        return results

    def restore_backups(self, file_paths: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Restore files from backup.

        Args:
            file_paths: List of file paths to restore (None for all applied fixes)

        Returns:
            List of restore results
        """
        results = []

        if file_paths is None:
            # Restore all applied fixes
            file_paths = [fix.get("issue", {}).get("file") for fix in self.applied_fixes]
            file_paths = [fp for fp in file_paths if fp]  # Filter out None values

        for file_path in file_paths:
            backup_path = f"{file_path}{self.backup_suffix}"

            if not Path(backup_path).exists():
                results.append({
                    "success": False,
                    "file": file_path,
                    "message": f"No backup found: {backup_path}",
                })
                continue

            try:
                shutil.copy2(backup_path, file_path)
                results.append({
                    "success": True,
                    "file": file_path,
                    "message": "File restored from backup",
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "file": file_path,
                    "message": f"Error restoring backup: {str(e)}",
                    "error": str(e),
                })

        return results

    def get_applied_fixes(self) -> List[Dict[str, Any]]:
        """
        Get list of successfully applied fixes.

        Returns:
            List of applied fix dictionaries
        """
        return self.applied_fixes.copy()
