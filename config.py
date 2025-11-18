"""
Configuration management for Bug-Fixing-AI-Assistant.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration manager for the bug-fixing assistant.
    """

    DEFAULT_CONFIG = {
        # Scanner settings
        "scanner": {
            "file_extensions": [".py"],
            "exclude_patterns": [
                "**/venv/**",
                "**/.venv/**",
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/.git/**",
            ],
            "max_file_size_mb": 10,
        },
        # Fixer settings
        "fixer": {
            "auto_apply_fixes": False,
            "create_backup": True,
            "backup_suffix": ".backup",
        },
        # AI settings
        "ai": {
            "provider": "anthropic",  # 'anthropic' or 'openai'
            "model": "claude-sonnet-4-5-20250929",
            "api_key_env_var": "ANTHROPIC_API_KEY",
            "max_tokens": 4000,
            "temperature": 0.0,
        },
        # PR handler settings
        "pr": {
            "base_branch": "main",
            "branch_prefix": "bugfix/ai-",
            "auto_push": False,
            "create_pr": False,
        },
        # Validation settings
        "validation": {
            "run_tests": True,
            "test_command": "python -m pytest",
            "require_tests_pass": False,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path

        if config_path and Path(config_path).exists():
            self.load_from_file(config_path)

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file.

        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if config_file.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                with open(config_file, "r") as f:
                    file_config = yaml.safe_load(f) or {}
                self._merge_config(file_config)
            except ImportError:
                raise ImportError(
                    "PyYAML is required to load YAML config files. "
                    "Install with: pip install pyyaml"
                )
        elif config_file.suffix == ".json":
            import json
            with open(config_file, "r") as f:
                file_config = json.load(f)
            self._merge_config(file_config)
        else:
            raise ValueError(f"Unsupported config file format: {config_file.suffix}")

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge new configuration with existing config.

        Args:
            new_config: New configuration dictionary
        """
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict):
                if isinstance(value, dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
            else:
                self.config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'scanner.file_extensions')
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_ai_api_key(self) -> Optional[str]:
        """
        Get AI API key from environment variable.

        Returns:
            API key or None if not found
        """
        env_var = self.get("ai.api_key_env_var")
        if env_var:
            return os.environ.get(env_var)
        return None

    def save_to_file(self, output_path: str) -> None:
        """
        Save current configuration to a file.

        Args:
            output_path: Path to save configuration file
        """
        output_file = Path(output_path)

        if output_file.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                with open(output_file, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            except ImportError:
                raise ImportError(
                    "PyYAML is required to save YAML config files. "
                    "Install with: pip install pyyaml"
                )
        elif output_file.suffix == ".json":
            import json
            with open(output_file, "w") as f:
                json.dump(self.config, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {output_file.suffix}")

    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config({self.config})"
