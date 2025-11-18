"""
Setup script for Bug-Fixing-AI-Assistant.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="bug-fixing-ai-assistant",
    version="1.0.0",
    description="AI-powered assistant for automated bug detection and fixing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bug Fixing AI Team",
    author_email="bugs@example.com",
    url="https://github.com/matthewnyc2/Bug-Fixing-AI-Assistant",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.7",
    install_requires=[
        # Core functionality uses only standard library
    ],
    extras_require={
        "ai": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
            "requests>=2.31.0",
            "pyyaml>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bugfix-ai=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="bug-fixing ai automation code-quality testing",
)
