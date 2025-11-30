"""
VIPER Setup Configuration

This file configures VIPER as an installable Python package with CLI support.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()
# Filter out empty lines and comments
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="viper-ai",
    version="1.0.0",
    description="A developer-focused, terminal-based AI chat interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Edward",
    author_email="",
    url="https://github.com/3ddy98/VIPER",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'VIPER=viper.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    package_data={
        'viper': ['data/*', 'tools/*', 'agents/*'],
    },
)
