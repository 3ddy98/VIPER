"""
VIPER CLI Entry Point

This module provides the command-line interface for VIPER.
It handles argument parsing and sets up the working directory before launching the main application.
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    """
    CLI entry point for VIPER.

    Supports:
    - VIPER: Run in current working directory
    - VIPER --dir /path/to/project: Run in specified directory
    """
    parser = argparse.ArgumentParser(
        description="VIPER - A developer-focused, terminal-based AI chat interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  VIPER                    Run in current directory
  VIPER --dir ~/projects   Run in specified directory
  VIPER --version          Show version information
        """
    )

    parser.add_argument(
        '--dir', '-d',
        dest='directory',
        type=str,
        default=None,
        help='Working directory for VIPER (default: current directory)'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='VIPER 1.0.0'
    )

    args = parser.parse_args()

    # Determine working directory
    if args.directory:
        working_dir = Path(args.directory).resolve()

        # Validate directory exists
        if not working_dir.exists():
            print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
            sys.exit(1)

        if not working_dir.is_dir():
            print(f"Error: Path is not a directory: {args.directory}", file=sys.stderr)
            sys.exit(1)

        # Change to the specified directory
        os.chdir(working_dir)
        print(f"Working directory: {working_dir}\n")
    else:
        working_dir = Path.cwd()

    # Import and run the main application
    # The main.py file should be in the parent directory of this package
    try:
        # Add the parent directory to sys.path to import main
        viper_root = Path(__file__).parent.parent
        if str(viper_root) not in sys.path:
            sys.path.insert(0, str(viper_root))

        # Import and run main
        from main import main as run_app
        run_app()

    except ImportError as e:
        print(f"Error: Could not import VIPER main application: {e}", file=sys.stderr)
        print(f"Make sure VIPER is properly installed.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nVIPER terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
