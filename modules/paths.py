"""
Paths Configuration Module

This module provides centralized path management for VIPER.
It handles both installed package mode and development mode.
"""

import os
import sys
from pathlib import Path


def get_viper_root() -> Path:
    """
    Get the root directory of the VIPER installation.

    This works in both development mode (running from source) and
    installed package mode (running via pip/pipx).

    Returns:
        Path object pointing to VIPER root directory
    """
    # Try to find the root based on main.py location
    # In development mode: modules/paths.py is at VIPER/modules/paths.py, so parent.parent is VIPER/
    # In installed mode: modules/paths.py is at VIPER/modules/paths.py, so parent.parent is VIPER/

    # First, try to find main.py in the current working directory (development mode)
    if (Path.cwd() / "main.py").exists():
        return Path.cwd()

    # Try to find it relative to this module
    # This file is in modules/, so parent is the package root, parent.parent is VIPER root
    module_path = Path(__file__).parent.parent
    if (module_path / "main.py").exists():
        return module_path

    # In installed package mode via pip, we need to go up from viper/modules/ to VIPER/
    # modules/paths.py -> __file__
    # modules/ -> parent
    # viper/ or VIPER/ -> parent.parent
    # If we're in viper/ package, go up one more level
    if module_path.name == "viper":
        viper_root = module_path.parent
        if (viper_root / "main.py").exists():
            return viper_root

    # If neither works, return current directory as fallback
    return Path.cwd()


def get_tools_dir() -> Path:
    """Get the tools directory path."""
    return get_viper_root() / "tools"


def get_modules_dir() -> Path:
    """Get the modules directory path."""
    return get_viper_root() / "modules"


def get_agents_dir() -> Path:
    """Get the agents directory path."""
    return get_viper_root() / "agents"


def get_data_dir() -> Path:
    """
    Get the data directory path.

    Data directory is in the VIPER installation root.
    This ensures configuration and conversations persist across all working directories.
    """
    return get_viper_root() / "data"


def ensure_data_dir() -> Path:
    """
    Ensure the data directory exists in the current working directory.

    Returns:
        Path to the data directory
    """
    data_dir = get_data_dir()
    data_dir.mkdir(exist_ok=True)
    return data_dir
