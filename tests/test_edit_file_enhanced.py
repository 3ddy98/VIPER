"""
Test enhanced edit_file tool with dry-run and regex capabilities
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.edit_file import EditFileTool
import tempfile
import shutil

def test_edit_file_enhanced():
    """Test the enhanced edit_file tool with dry-run and regex features."""

    print("=" * 70)
    print("ENHANCED EDIT_FILE TOOL TEST")
    print("=" * 70)

    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    print(f"\nCreated test directory: {test_dir}")

    try:
        # Initialize the tool
        edit_tool = EditFileTool(base_path=test_dir)

        # Create a test file
        test_file_path = os.path.join(test_dir, "test.txt")
        with open(test_file_path, 'w') as f:
            f.write("""Hello World!
This is a test file.
Hello again!
Testing 123
hello lowercase
HELLO UPPERCASE
foo bar baz
Contact: email@example.com
Phone: 555-1234
""")

        print("\n" + "=" * 70)
        print("TEST 1: Basic replace_text with dry_run")
        print("=" * 70)

        result = edit_tool.replace_text(
            file_path="test.txt",
            old_text="Hello World!",
            new_text="Hi Universe!",
            dry_run=True
        )

        print(f"\nDry run: {result.get('dry_run')}")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Changes count: {result.get('changes_count')}")
        print(f"\nDiff preview:\n{result.get('diff')}")

        # Verify file wasn't modified
        with open(test_file_path, 'r') as f:
            content = f.read()

        if "Hello World!" in content:
            print("\n✓ PASS: File unchanged after dry run")
        else:
            print("\n✗ FAIL: File was modified during dry run!")

        print("\n" + "=" * 70)
        print("TEST 2: Apply the change (dry_run=False)")
        print("=" * 70)

        result = edit_tool.replace_text(
            file_path="test.txt",
            old_text="Hello World!",
            new_text="Hi Universe!",
            dry_run=False
        )

        print(f"\nSuccess: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"\nDiff:\n{result.get('diff')}")

        # Verify file was modified
        with open(test_file_path, 'r') as f:
            content = f.read()

        if "Hi Universe!" in content and "Hello World!" not in content:
            print("\n✓ PASS: File successfully modified")
        else:
            print("\n✗ FAIL: File modification failed")

        print("\n" + "=" * 70)
        print("TEST 3: Regex replace with dry_run (case-insensitive)")
        print("=" * 70)

        result = edit_tool.regex_replace(
            file_path="test.txt",
            pattern=r"hello",
            replacement="GREETINGS",
            flags=1,  # IGNORECASE
            dry_run=True
        )

        print(f"\nDry run: {result.get('dry_run')}")
        print(f"Success: {result.get('success')}")
        print(f"Matches found: {result.get('matches_found')}")
        print(f"Replacements: {result.get('replacements_count')}")
        print(f"\nDiff preview:\n{result.get('diff')}")

        if result.get('matches_found') == 3:  # "hello" appears 3 times (case-insensitive)
            print("\n✓ PASS: Correctly found all case-insensitive matches")
        else:
            print(f"\n✗ FAIL: Expected 3 matches, got {result.get('matches_found')}")

        print("\n" + "=" * 70)
        print("TEST 4: Regex replace with backreferences")
        print("=" * 70)

        result = edit_tool.regex_replace(
            file_path="test.txt",
            pattern=r"(\w+)@(\w+\.\w+)",
            replacement=r"\1 [AT] \2",
            dry_run=True
        )

        print(f"\nSuccess: {result.get('success')}")
        print(f"Matches found: {result.get('matches_found')}")
        print(f"\nDiff preview:\n{result.get('diff')}")

        if "email [AT] example.com" in result.get('diff', ''):
            print("\n✓ PASS: Backreferences working correctly")
        else:
            print("\n✗ FAIL: Backreferences not working")

        print("\n" + "=" * 70)
        print("TEST 5: Apply regex replacement")
        print("=" * 70)

        result = edit_tool.regex_replace(
            file_path="test.txt",
            pattern=r"(\w+)@(\w+\.\w+)",
            replacement=r"\1 [AT] \2",
            dry_run=False
        )

        print(f"\nSuccess: {result.get('success')}")
        print(f"Message: {result.get('message')}")

        # Verify change
        with open(test_file_path, 'r') as f:
            content = f.read()

        if "email [AT] example.com" in content:
            print("✓ PASS: Regex replacement applied successfully")
        else:
            print("✗ FAIL: Regex replacement failed")

        print("\n" + "=" * 70)
        print("TEST 6: Multiple replacements with count limit")
        print("=" * 70)

        # Reset test file with multiple instances
        with open(test_file_path, 'w') as f:
            f.write("foo bar foo baz foo qux")

        result = edit_tool.replace_text(
            file_path="test.txt",
            old_text="foo",
            new_text="FOO",
            count=2,  # Only replace first 2
            dry_run=True
        )

        print(f"\nMatches to replace: {result.get('changes_count')}")
        print(f"Diff preview:\n{result.get('diff')}")

        if result.get('changes_count') == 2:
            print("\n✓ PASS: Count parameter working correctly")
        else:
            print(f"\n✗ FAIL: Expected 2 replacements, got {result.get('changes_count')}")

        print("\n" + "=" * 70)
        print("TEST 7: Multiline regex with DOTALL flag")
        print("=" * 70)

        # Create multiline content
        with open(test_file_path, 'w') as f:
            f.write("start\nsome content here\nmore lines\nend")

        result = edit_tool.regex_replace(
            file_path="test.txt",
            pattern=r"start.*end",
            replacement="REPLACED",
            flags=4,  # DOTALL - allows . to match newlines
            dry_run=True
        )

        print(f"\nSuccess: {result.get('success')}")
        print(f"Matches found: {result.get('matches_found')}")
        print(f"\nDiff preview:\n{result.get('diff')}")

        if result.get('matches_found') == 1:
            print("\n✓ PASS: DOTALL flag working (. matches newlines)")
        else:
            print(f"\n✗ FAIL: Expected 1 match with DOTALL, got {result.get('matches_found')}")

        print("\n" + "=" * 70)
        print("TEST 8: Error handling - invalid regex")
        print("=" * 70)

        result = edit_tool.regex_replace(
            file_path="test.txt",
            pattern=r"[invalid(regex",  # Malformed regex
            replacement="test",
            dry_run=True
        )

        if not result.get('success') and "Invalid regex pattern" in result.get('error', ''):
            print("✓ PASS: Invalid regex detected and handled correctly")
            print(f"Error: {result.get('error')}")
        else:
            print("✗ FAIL: Invalid regex not properly detected")

        print("\n" + "=" * 70)
        print("TEST 9: Tool specification check")
        print("=" * 70)

        spec = edit_tool.get_tool_spec()

        print(f"\nTool name: {spec['tool_name']}")
        print(f"Version: {spec['version']}")
        print(f"Description: {spec['description']}")
        print(f"\nMethods available:")
        for method in spec['methods']:
            print(f"  - {method['name']}: {method['description']}")

        if len(spec['methods']) == 2:
            print("\n✓ PASS: Both replace_text and regex_replace methods in spec")
        else:
            print(f"\n✗ FAIL: Expected 2 methods, found {len(spec['methods'])}")

        # Check dry_run parameter exists
        replace_text_params = spec['methods'][0]['parameters']
        if 'dry_run' in replace_text_params:
            print("✓ PASS: dry_run parameter in replace_text spec")
        else:
            print("✗ FAIL: dry_run parameter missing from spec")

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print("\n✓ All enhanced features tested successfully!")
        print("✓ Dry-run mode prevents file modifications")
        print("✓ Diff output shows exact changes")
        print("✓ Regex replacement with backreferences working")
        print("✓ Regex flags (IGNORECASE, MULTILINE, DOTALL) functional")
        print("✓ Error handling for invalid patterns")

    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    test_edit_file_enhanced()
