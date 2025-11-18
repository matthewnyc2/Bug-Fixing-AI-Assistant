"""
AI-powered fix generator using Claude or GPT.
"""

from typing import Dict, Any, List, Optional
import os


class AIFixer:
    """
    Generate intelligent code fixes using AI (Claude or GPT).
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the AI fixer.

        Args:
            provider: AI provider ('anthropic' or 'openai')
            model: Model to use (defaults based on provider)
            api_key: API key (if not provided, reads from environment)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()

        if self.provider == "anthropic":
            self.model = model or "claude-sonnet-4-5-20250929"
            self.client = self._init_anthropic()
        elif self.provider == "openai":
            self.model = model or "gpt-4-turbo-preview"
            self.client = self._init_openai()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        if self.provider == "anthropic":
            return os.environ.get("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.environ.get("OPENAI_API_KEY")
        return None

    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic client: {e}")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")

    def generate_fix(
        self,
        issue: Dict[str, Any],
        file_content: str,
        context_lines: int = 10,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an AI-powered fix for a detected issue.

        Args:
            issue: Issue dictionary with type, line, message, etc.
            file_content: Full content of the file
            context_lines: Number of context lines to show around the issue

        Returns:
            Fix dictionary with suggested code change
        """
        if not self.api_key:
            raise ValueError(
                f"No API key found. Set {self.provider.upper()}_API_KEY environment variable."
            )

        prompt = self._build_fix_prompt(issue, file_content, context_lines)

        if self.provider == "anthropic":
            return self._generate_fix_anthropic(issue, prompt)
        elif self.provider == "openai":
            return self._generate_fix_openai(issue, prompt)

        return None

    def _build_fix_prompt(
        self, issue: Dict[str, Any], file_content: str, context_lines: int
    ) -> str:
        """Build prompt for AI to generate fix."""
        lines = file_content.splitlines()
        issue_line = issue.get("line", 1) - 1  # Convert to 0-indexed

        # Get context around the issue
        start_line = max(0, issue_line - context_lines)
        end_line = min(len(lines), issue_line + context_lines + 1)
        context = "\n".join(
            f"{i+1:4d} | {line}" for i, line in enumerate(lines[start_line:end_line], start=start_line)
        )

        prompt = f"""You are an expert code reviewer and bug fixer. Analyze the following code issue and provide a fix.

## Issue Details
- Type: {issue.get('type', 'Unknown')}
- Severity: {issue.get('severity', 'Unknown')}
- Line: {issue.get('line', 'N/A')}
- Message: {issue.get('message', 'No message')}
- File: {issue.get('file', 'N/A')}

## Code Context
```python
{context}
```

## Instructions
1. Identify the exact problem on line {issue.get('line', 'N/A')}
2. Provide the corrected code for that line
3. Explain why the fix is correct
4. If the fix requires changes to multiple lines, provide all necessary changes

Respond in the following format:
```json
{{
    "fixed_code": "the corrected code",
    "explanation": "explanation of the fix",
    "confidence": "high|medium|low",
    "changes": [
        {{
            "line_number": line_number,
            "old_code": "original code",
            "new_code": "fixed code"
        }}
    ]
}}
```

Provide ONLY the JSON response, nothing else."""

        return prompt

    def _generate_fix_anthropic(
        self, issue: Dict[str, Any], prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Generate fix using Anthropic Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract JSON from response
            content = response.content[0].text
            return self._parse_ai_response(issue, content)

        except Exception as e:
            return {
                "issue": issue,
                "fix_type": "ai_error",
                "description": f"AI fix generation failed: {str(e)}",
                "suggestion": "Manual review required",
                "automated": False,
                "error": str(e),
            }

    def _generate_fix_openai(
        self, issue: Dict[str, Any], prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Generate fix using OpenAI GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            return self._parse_ai_response(issue, content)

        except Exception as e:
            return {
                "issue": issue,
                "fix_type": "ai_error",
                "description": f"AI fix generation failed: {str(e)}",
                "suggestion": "Manual review required",
                "automated": False,
                "error": str(e),
            }

    def _parse_ai_response(
        self, issue: Dict[str, Any], response_text: str
    ) -> Dict[str, Any]:
        """Parse AI response and extract fix information."""
        import json
        import re

        # Try to extract JSON from response
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to parse the whole response as JSON
            json_str = response_text.strip()

        try:
            ai_fix = json.loads(json_str)

            return {
                "issue": issue,
                "fix_type": "ai_generated",
                "description": f"AI-generated fix: {ai_fix.get('explanation', 'No explanation')}",
                "suggestion": ai_fix.get("fixed_code", ""),
                "changes": ai_fix.get("changes", []),
                "confidence": ai_fix.get("confidence", "unknown"),
                "explanation": ai_fix.get("explanation", ""),
                "automated": True,
                "provider": self.provider,
                "model": self.model,
            }

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw response
            return {
                "issue": issue,
                "fix_type": "ai_response",
                "description": "AI provided a fix but response format was unexpected",
                "suggestion": response_text,
                "automated": False,
                "error": f"JSON parse error: {str(e)}",
            }

    def generate_fixes_batch(
        self, issues: List[Dict[str, Any]], file_content: str
    ) -> List[Dict[str, Any]]:
        """
        Generate fixes for multiple issues.

        Args:
            issues: List of issue dictionaries
            file_content: Full content of the file

        Returns:
            List of fix dictionaries
        """
        fixes = []
        for issue in issues:
            fix = self.generate_fix(issue, file_content)
            if fix:
                fixes.append(fix)
        return fixes
