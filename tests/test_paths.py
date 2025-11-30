"""
Test path resolution for VIPER installation
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.paths import get_viper_root, get_tools_dir, get_agents_dir, get_data_dir
from pathlib import Path

def test_path_resolution():
    """Test that all paths resolve to the VIPER installation directory."""

    print("=" * 70)
    print("PATH RESOLUTION TEST")
    print("=" * 70)

    # Get VIPER root
    viper_root = get_viper_root()
    print(f"\nVIPER Root: {viper_root}")
    print(f"VIPER Root exists: {viper_root.exists()}")
    print(f"main.py exists: {(viper_root / 'main.py').exists()}")

    # Get tools directory
    tools_dir = get_tools_dir()
    print(f"\nTools Directory: {tools_dir}")
    print(f"Tools Directory exists: {tools_dir.exists()}")
    print(f"Tools Directory is inside VIPER root: {str(viper_root) in str(tools_dir)}")

    # Get agents directory
    agents_dir = get_agents_dir()
    print(f"\nAgents Directory: {agents_dir}")
    print(f"Agents Directory exists: {agents_dir.exists()}")
    print(f"Agents Directory is inside VIPER root: {str(viper_root) in str(agents_dir)}")

    # Get data directory
    data_dir = get_data_dir()
    print(f"\nData Directory: {data_dir}")
    print(f"Data Directory is inside VIPER root: {str(viper_root) in str(data_dir)}")

    # Test that changing working directory doesn't affect VIPER root
    original_cwd = Path.cwd()
    print(f"\nOriginal CWD: {original_cwd}")

    # Change to a different directory (parent directory)
    test_dir = viper_root.parent
    os.chdir(test_dir)
    print(f"Changed CWD to: {Path.cwd()}")

    # Re-import to get fresh path resolution
    import importlib
    import modules.paths
    importlib.reload(modules.paths)
    from modules.paths import get_viper_root as get_viper_root_2

    viper_root_after_cd = get_viper_root_2()
    print(f"VIPER Root after changing directory: {viper_root_after_cd}")
    print(f"VIPER Root unchanged: {viper_root == viper_root_after_cd}")

    # Restore original directory
    os.chdir(original_cwd)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Verify all paths are in VIPER root
    all_in_root = (
        str(viper_root) in str(tools_dir) and
        str(viper_root) in str(agents_dir) and
        str(viper_root) in str(data_dir)
    )

    if all_in_root:
        print("\n✓ All paths correctly resolve to VIPER installation directory")
        print("✓ Configuration and agents will persist across working directories")
    else:
        print("\n✗ Some paths are not in VIPER root")
        print("✗ This may cause configuration/agent persistence issues")

    print("\nPath Configuration:")
    print(f"  - VIPER Root:  {viper_root}")
    print(f"  - Tools:       {tools_dir}")
    print(f"  - Agents:      {agents_dir}")
    print(f"  - Data:        {data_dir}")

if __name__ == "__main__":
    test_path_resolution()
