"""
Detector for code quality issues in Python code.
"""

import ast
from typing import List, Dict, Any
from pathlib import Path


class QualityDetector(ast.NodeVisitor):
    """
    Detect code quality issues in Python code.
    """

    def __init__(self, file_path: Path):
        """
        Initialize the quality detector.

        Args:
            file_path: Path to the file being analyzed
        """
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []
        self.function_complexity: Dict[str, int] = {}
        self.current_function = None
        self.complexity_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check function definitions for quality issues.
        """
        # Save previous function context
        prev_function = self.current_function
        prev_complexity = self.complexity_count

        # Set current function context
        self.current_function = node.name
        self.complexity_count = 1  # Base complexity

        # Check for functions with too many arguments
        total_args = (
            len(node.args.args)
            + len(node.args.posonlyargs)
            + len(node.args.kwonlyargs)
        )

        if total_args > 7:
            self.issues.append(
                {
                    "file": str(self.file_path),
                    "line": node.lineno,
                    "type": "too_many_arguments",
                    "message": f'Function "{node.name}" has {total_args} arguments (max recommended: 7)',
                    "severity": "info",
                }
            )

        # Check for missing docstring
        if not ast.get_docstring(node):
            # Only warn for public functions (not starting with _)
            if not node.name.startswith("_"):
                self.issues.append(
                    {
                        "file": str(self.file_path),
                        "line": node.lineno,
                        "type": "missing_docstring",
                        "message": f'Public function "{node.name}" is missing a docstring',
                        "severity": "info",
                    }
                )

        # Visit function body to calculate complexity
        self.generic_visit(node)

        # Check cyclomatic complexity
        if self.complexity_count > 10:
            self.issues.append(
                {
                    "file": str(self.file_path),
                    "line": node.lineno,
                    "type": "high_complexity",
                    "message": f'Function "{node.name}" has high cyclomatic complexity ({self.complexity_count})',
                    "severity": "warning",
                }
            )

        # Restore previous function context
        self.current_function = prev_function
        self.complexity_count = prev_complexity

    def visit_If(self, node: ast.If) -> None:
        """Count if statements for complexity."""
        if self.current_function:
            self.complexity_count += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Count for loops for complexity."""
        if self.current_function:
            self.complexity_count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Count while loops for complexity."""
        if self.current_function:
            self.complexity_count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Count exception handlers for complexity."""
        if self.current_function:
            self.complexity_count += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Count with statements for complexity."""
        if self.current_function:
            self.complexity_count += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        """Check for assert statements in production code."""
        # Warn about assert usage (can be disabled with -O flag)
        self.issues.append(
            {
                "file": str(self.file_path),
                "line": node.lineno,
                "type": "assert_statement",
                "message": "Using assert in production code (can be disabled with python -O)",
                "severity": "info",
            }
        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions."""
        # Check for missing docstring
        if not ast.get_docstring(node):
            # Only warn for public classes
            if not node.name.startswith("_"):
                self.issues.append(
                    {
                        "file": str(self.file_path),
                        "line": node.lineno,
                        "type": "missing_docstring",
                        "message": f'Public class "{node.name}" is missing a docstring',
                        "severity": "info",
                    }
                )

        # Check for too many methods (God object antipattern)
        method_count = sum(
            1 for item in node.body if isinstance(item, ast.FunctionDef)
        )
        if method_count > 20:
            self.issues.append(
                {
                    "file": str(self.file_path),
                    "line": node.lineno,
                    "type": "too_many_methods",
                    "message": f'Class "{node.name}" has {method_count} methods (possible God object)',
                    "severity": "warning",
                }
            )

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check for magic numbers and strings."""
        # Check for magic numbers (ignore common values)
        if isinstance(node.value, (int, float)):
            if node.value not in [0, 1, -1, 2, 10, 100, 1000]:
                # Check if it's not in a constant assignment
                parent = getattr(node, "parent", None)
                if not isinstance(parent, ast.Assign):
                    self.issues.append(
                        {
                            "file": str(self.file_path),
                            "line": node.lineno,
                            "type": "magic_number",
                            "message": f"Magic number {node.value} should be a named constant",
                            "severity": "info",
                        }
                    )

        self.generic_visit(node)

    def get_issues(self) -> List[Dict[str, Any]]:
        """
        Get detected issues.

        Returns:
            List of detected issues
        """
        return self.issues


def detect_quality_issues(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """
    Detect code quality issues in a Python file.

    Args:
        file_path: Path to the file
        content: File content as string

    Returns:
        List of detected quality issues
    """
    try:
        tree = ast.parse(content, filename=str(file_path))
        detector = QualityDetector(file_path)
        detector.visit(tree)
        return detector.get_issues()
    except SyntaxError:
        # Syntax errors are handled by the scanner
        return []
