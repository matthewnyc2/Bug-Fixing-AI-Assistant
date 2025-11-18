#!/usr/bin/env python3
"""
Main entry point for Bug-Fixing-AI-Assistant.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import Config
from scanner.core.scanner import CodeScanner
from scanner.core.report import ReportGenerator
from scanner.detectors.pattern_detector import detect_patterns
from scanner.detectors.security_detector import detect_security_issues
from scanner.detectors.quality_detector import detect_quality_issues
from fixer.generators.fix_generator import FixGenerator
from fixer.fix_applicator import FixApplicator
from fixer.validators.fix_validator import FixValidator
from fixer.validators.test_runner import TestRunner


class BugFixingAssistant:
    """
    Main orchestrator for the bug-fixing AI assistant.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the assistant.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.scanner = None
        self.ai_fixer = None
        self.fix_generator = FixGenerator()
        self.fix_applicator = FixApplicator(
            create_backup=self.config.get("fixer.create_backup", True),
            backup_suffix=self.config.get("fixer.backup_suffix", ".backup"),
        )
        self.all_issues: List[Dict[str, Any]] = []
        self.all_fixes: List[Dict[str, Any]] = []

    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Scan a directory for bugs.

        Args:
            directory: Path to directory to scan

        Returns:
            List of detected issues
        """
        print(f"Scanning directory: {directory}")

        self.scanner = CodeScanner(directory)
        extensions = self.config.get("scanner.file_extensions", [".py"])

        # Scan with the base scanner (finds syntax errors)
        results = self.scanner.scan_directory(extensions)

        # Find all Python files and run detectors on them
        code_files = self.scanner._find_code_files(extensions)

        for file_path in code_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Run pattern detector
                pattern_issues = detect_patterns(file_path, content)
                results.extend(pattern_issues)

                # Run security detector
                security_issues = detect_security_issues(file_path, content)
                results.extend(security_issues)

                # Run quality detector
                quality_issues = detect_quality_issues(file_path, content)
                results.extend(quality_issues)

            except Exception as e:
                print(f"Error scanning {file_path}: {e}")

        self.all_issues = results
        print(f"Found {len(results)} issues")

        return results

    def generate_fixes(
        self, issues: Optional[List[Dict[str, Any]]] = None, use_ai: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate fixes for detected issues.

        Args:
            issues: List of issues to fix (uses all_issues if None)
            use_ai: Whether to use AI for fix generation

        Returns:
            List of generated fixes
        """
        if issues is None:
            issues = self.all_issues

        print(f"Generating fixes for {len(issues)} issues...")

        if use_ai:
            fixes = self._generate_ai_fixes(issues)
        else:
            fixes = self._generate_basic_fixes(issues)

        self.all_fixes = fixes
        print(f"Generated {len(fixes)} fixes")

        return fixes

    def _generate_basic_fixes(
        self, issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate fixes using basic fix generator."""
        fixes = []
        for issue in issues:
            fix = self.fix_generator.generate_fix(issue)
            if fix:
                fixes.append(fix)
        return fixes

    def _generate_ai_fixes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate fixes using AI."""
        if self.ai_fixer is None:
            # Initialize AI fixer
            provider = self.config.get("ai.provider", "anthropic")
            model = self.config.get("ai.model")
            api_key = self.config.get_ai_api_key()

            try:
                from fixer.ai_fixer import AIFixer

                self.ai_fixer = AIFixer(provider=provider, model=model, api_key=api_key)
            except Exception as e:
                print(f"Error initializing AI fixer: {e}")
                print("Falling back to basic fix generation")
                return self._generate_basic_fixes(issues)

        fixes = []

        # Group issues by file
        issues_by_file: Dict[str, List[Dict[str, Any]]] = {}
        for issue in issues:
            file_path = issue.get("file", "")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        # Generate AI fixes for each file
        for file_path, file_issues in issues_by_file.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_fixes = self.ai_fixer.generate_fixes_batch(file_issues, content)
                fixes.extend(file_fixes)

            except Exception as e:
                print(f"Error generating AI fixes for {file_path}: {e}")
                # Fall back to basic fixes for this file
                for issue in file_issues:
                    fix = self.fix_generator.generate_fix(issue)
                    if fix:
                        fixes.append(fix)

        return fixes

    def apply_fixes(
        self,
        fixes: Optional[List[Dict[str, Any]]] = None,
        dry_run: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Apply fixes to files.

        Args:
            fixes: List of fixes to apply (uses all_fixes if None)
            dry_run: If True, don't actually modify files

        Returns:
            List of application results
        """
        if fixes is None:
            fixes = self.all_fixes

        print(f"Applying {len(fixes)} fixes (dry_run={dry_run})...")

        results = self.fix_applicator.apply_fixes_batch(fixes, dry_run=dry_run)

        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful

        print(f"Successfully applied: {successful}, Failed: {failed}")

        return results

    def create_pr(
        self, fixes: List[Dict[str, Any]], branch_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a pull request with the fixes.

        Args:
            fixes: List of applied fixes
            branch_name: Branch name (auto-generated if None)

        Returns:
            PR creation result
        """
        from pr_handler.pr_creator import PRCreator
        import datetime

        if branch_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            prefix = self.config.get("pr.branch_prefix", "bugfix/ai-")
            branch_name = f"{prefix}{timestamp}"

        repo_path = Path.cwd()
        base_branch = self.config.get("pr.base_branch", "main")

        pr_creator = PRCreator(str(repo_path), base_branch)

        # Create branch
        branch_result = pr_creator.create_branch(branch_name)
        if not branch_result.get("success"):
            return {
                "success": False,
                "message": f"Failed to create branch: {branch_result.get('message')}",
            }

        # Commit changes
        commit_msg = f"Fix {len(fixes)} issues found by Bug-Fixing-AI-Assistant"
        commit_result = pr_creator.commit_changes(commit_msg)

        if not commit_result.get("success"):
            return {
                "success": False,
                "message": f"Failed to commit changes: {commit_result.get('message')}",
            }

        # Generate PR description
        pr_description = pr_creator.generate_pr_description(fixes, self.all_issues)

        result = {
            "success": True,
            "branch": branch_name,
            "commit": commit_result,
            "pr_description": pr_description,
        }

        # Push if configured
        if self.config.get("pr.auto_push", False):
            push_result = pr_creator.push_branch(branch_name)
            result["push"] = push_result

        return result

    def run_tests(self) -> Dict[str, Any]:
        """
        Run tests to validate fixes.

        Returns:
            Test execution results
        """
        test_command = self.config.get("validation.test_command", "python -m pytest")
        runner = TestRunner(str(Path.cwd()))

        print(f"Running tests: {test_command}")

        if "pytest" in test_command:
            result = runner.run_pytest()
        else:
            result = runner.run_unittest()

        return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Bug-Fixing AI Assistant - Automated bug detection and fixing"
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--ai",
        action="store_true",
        help="Use AI for fix generation",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Automatically apply fixes",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without applying changes",
    )

    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Create a pull request with fixes",
    )

    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests after applying fixes",
    )

    parser.add_argument(
        "--report",
        choices=["text", "json"],
        default="text",
        help="Report format (default: text)",
    )

    args = parser.parse_args()

    # Load configuration
    config = Config(args.config) if args.config else Config()

    # Initialize assistant
    assistant = BugFixingAssistant(config)

    try:
        # Step 1: Scan directory
        issues = assistant.scan_directory(args.directory)

        if not issues:
            print("\nNo issues found!")
            return 0

        # Step 2: Generate report
        if args.report == "json":
            report = ReportGenerator.generate_json_report(issues)
        else:
            report = ReportGenerator.generate_text_report(issues)

        print("\n" + report)

        # Step 3: Generate fixes
        if args.apply or args.create_pr or args.dry_run:
            fixes = assistant.generate_fixes(use_ai=args.ai)

            if not fixes:
                print("\nNo fixes could be generated.")
                return 0

            # Step 4: Apply fixes
            if args.apply or args.create_pr:
                results = assistant.apply_fixes(dry_run=args.dry_run)

                # Show results
                for result in results:
                    if result.get("success"):
                        print(f"\n✓ Fixed: {result.get('file')}")
                        if result.get("diff"):
                            print(result["diff"])
                    else:
                        print(f"\n✗ Failed: {result.get('message')}")

            # Step 5: Run tests if requested
            if args.run_tests and not args.dry_run:
                test_result = assistant.run_tests()
                if test_result.get("success"):
                    print("\n✓ Tests passed")
                else:
                    print("\n✗ Tests failed")
                    print(test_result.get("stderr", ""))

            # Step 6: Create PR if requested
            if args.create_pr and not args.dry_run:
                pr_result = assistant.create_pr(fixes)
                if pr_result.get("success"):
                    print(f"\n✓ Created branch: {pr_result.get('branch')}")
                    print("\nPR Description:")
                    print(pr_result.get("pr_description"))
                else:
                    print(f"\n✗ Failed to create PR: {pr_result.get('message')}")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
