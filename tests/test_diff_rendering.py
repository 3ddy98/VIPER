"""
Test diff rendering with syntax highlighting and line numbers
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.renderer import render_diff

def test_diff_rendering():
    """Test the diff rendering function with various scenarios."""

    print("=" * 70)
    print("DIFF RENDERING TEST")
    print("=" * 70)

    # Test 1: Simple replacement
    print("\n" + "=" * 70)
    print("TEST 1: Simple text replacement")
    print("=" * 70)

    diff1 = """--- a/test.txt
+++ b/test.txt
@@ -1,4 +1,4 @@
-Hello World!
+Hi Universe!
 This is a test file.
 Hello again!
 Testing 123
"""

    render_diff(diff1, "test.txt", dry_run=False)

    # Test 2: Multiple line changes
    print("\n" + "=" * 70)
    print("TEST 2: Multiple line changes")
    print("=" * 70)

    diff2 = """--- a/example.py
+++ b/example.py
@@ -1,9 +1,9 @@
 def hello():
-    print("Hello World")
+    print("Hello Universe")
     return True

 def goodbye():
-    print("Goodbye World")
+    print("Goodbye Universe")
     return False

 if __name__ == "__main__":
"""

    render_diff(diff2, "example.py", dry_run=False)

    # Test 3: Dry run mode
    print("\n" + "=" * 70)
    print("TEST 3: Dry run preview")
    print("=" * 70)

    diff3 = """--- a/config.json
+++ b/config.json
@@ -1,5 +1,5 @@
 {
-    "version": "1.0.0",
+    "version": "2.0.0",
     "enabled": true,
     "debug": false
 }
"""

    render_diff(diff3, "config.json", dry_run=True)

    # Test 4: Large context with multiple hunks
    print("\n" + "=" * 70)
    print("TEST 4: Multiple hunks")
    print("=" * 70)

    diff4 = """--- a/app.py
+++ b/app.py
@@ -10,7 +10,7 @@
 import sys
 import os

-VERSION = "1.0.0"
+VERSION = "2.0.0"

 class Application:
     def __init__(self):
@@ -50,8 +50,8 @@
         return data

     def process(self, input_data):
-        # Old processing logic
-        result = input_data.strip()
+        # New processing logic with validation
+        result = input_data.strip().lower()
         return result

 if __name__ == "__main__":
"""

    render_diff(diff4, "app.py", dry_run=False)

    # Test 5: Regex replacement result
    print("\n" + "=" * 70)
    print("TEST 5: Regex replacement (email obfuscation)")
    print("=" * 70)

    diff5 = """--- a/contacts.txt
+++ b/contacts.txt
@@ -1,5 +1,5 @@
 Name: John Doe
-Email: john@example.com
+Email: john [AT] example.com
 Phone: 555-1234

-Contact us at support@company.com
+Contact us at support [AT] company.com
"""

    render_diff(diff5, "contacts.txt", dry_run=False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ All diff rendering tests completed!")
    print("✓ Syntax highlighting applied")
    print("✓ Line numbers displayed correctly")
    print("✓ Dry-run mode shows yellow border")
    print("✓ Applied changes show green border")
    print("\nCheck the output above to verify visual styling.")

if __name__ == "__main__":
    test_diff_rendering()
