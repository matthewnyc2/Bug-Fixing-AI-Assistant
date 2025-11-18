"""
Report generation for scan results.
"""

from typing import List, Dict, Any
import json


class ReportGenerator:
    """
    Generate reports from scan results.
    """
    
    @staticmethod
    def generate_json_report(results: List[Dict[str, Any]]) -> str:
        """
        Generate JSON report from scan results.
        
        Args:
            results: List of scan results
        
        Returns:
            JSON string of the report
        """
        report = {
            'total_issues': len(results),
            'issues_by_severity': ReportGenerator._count_by_severity(results),
            'issues': results
        }
        
        return json.dumps(report, indent=2)
    
    @staticmethod
    def generate_text_report(results: List[Dict[str, Any]]) -> str:
        """
        Generate text report from scan results.
        
        Args:
            results: List of scan results
        
        Returns:
            Text string of the report
        """
        if not results:
            return "No issues found."
        
        report_lines = [
            "=" * 60,
            f"Bug Scan Report - Total Issues: {len(results)}",
            "=" * 60,
            ""
        ]
        
        severity_counts = ReportGenerator._count_by_severity(results)
        report_lines.append("Issues by Severity:")
        for severity, count in severity_counts.items():
            report_lines.append(f"  {severity}: {count}")
        
        report_lines.append("\n" + "=" * 60)
        report_lines.append("Detailed Issues:")
        report_lines.append("=" * 60)
        
        for idx, issue in enumerate(results, 1):
            report_lines.append(f"\n{idx}. {issue.get('type', 'unknown')}")
            report_lines.append(f"   File: {issue.get('file', 'N/A')}")
            if 'line' in issue:
                report_lines.append(f"   Line: {issue['line']}")
            report_lines.append(f"   Severity: {issue.get('severity', 'unknown')}")
            report_lines.append(f"   Message: {issue.get('message', 'No message')}")
        
        return "\n".join(report_lines)
    
    @staticmethod
    def _count_by_severity(results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count issues by severity level.
        
        Args:
            results: List of scan results
        
        Returns:
            Dictionary mapping severity to count
        """
        counts = {}
        for result in results:
            severity = result.get('severity', 'unknown')
            counts[severity] = counts.get(severity, 0) + 1
        
        return counts
