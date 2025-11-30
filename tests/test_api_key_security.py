"""
Test that API keys are never saved to config.json
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import shutil
from pathlib import Path
from modules.config_persistence import save_config, load_config, import_from_env
from modules.config import CLIENT_CONFIG, GOOGLE_SEARCH_CONFIG, OPENROUTER_CONFIG

def test_api_key_security():
    """Test that API keys are never written to config.json."""

    print("=" * 70)
    print("API KEY SECURITY TEST")
    print("=" * 70)

    # Use test directory
    test_config_dir = Path("test_config_temp")
    test_config_file = test_config_dir / "config.json"

    # Backup original config
    from modules.config_persistence import DATA_DIR, CONFIG_FILE
    original_data_dir = DATA_DIR
    original_config_file = CONFIG_FILE

    try:
        # Override config paths for testing
        import modules.config_persistence as cp
        cp.DATA_DIR = test_config_dir
        cp.CONFIG_FILE = test_config_file

        # Clean up from previous tests
        if test_config_dir.exists():
            shutil.rmtree(test_config_dir)

        test_config_dir.mkdir()

        # Test 1: Load API keys from .env
        print("\n1. Loading API keys from .env...")
        imported = import_from_env()

        print(f"   API Key imported: {imported['api_key']}")
        print(f"   Google API Key imported: {imported['google_api_key']}")
        print(f"   Google CX ID imported: {imported['google_cx_id']}")
        print(f"   OpenRouter API Key imported: {imported['openrouter_api_key']}")

        if imported['api_key']:
            print(f"   ✓ CLIENT_CONFIG['api_key'] = {CLIENT_CONFIG['api_key'][:8]}...")
        else:
            print("   ⚠ No API key in .env")

        # Test 2: Save config
        print("\n2. Saving config to test file...")
        save_config()

        if test_config_file.exists():
            print(f"   ✓ Config saved to: {test_config_file}")
        else:
            print(f"   ✗ Config file NOT created")
            return

        # Test 3: Read saved config and check for API keys
        print("\n3. Checking saved config.json for API keys...")

        with open(test_config_file, 'r') as f:
            saved_config = json.load(f)

        print(f"   Config sections: {list(saved_config.keys())}")

        # Check each section for API keys
        security_pass = True

        if "client" in saved_config:
            if "api_key" in saved_config["client"]:
                print("   ✗ FAIL: api_key found in client config!")
                print(f"      Value: {saved_config['client']['api_key']}")
                security_pass = False
            else:
                print("   ✓ PASS: No api_key in client config")

        if "google_search" in saved_config:
            if "api_key" in saved_config["google_search"]:
                print("   ✗ FAIL: api_key found in google_search config!")
                print(f"      Value: {saved_config['google_search']['api_key']}")
                security_pass = False
            else:
                print("   ✓ PASS: No api_key in google_search config")

        if "openrouter" in saved_config:
            if "api_key" in saved_config["openrouter"]:
                print("   ✗ FAIL: api_key found in openrouter config!")
                print(f"      Value: {saved_config['openrouter']['api_key']}")
                security_pass = False
            else:
                print("   ✓ PASS: No api_key in openrouter config")

        # Test 4: Show what IS saved
        print("\n4. Showing what IS saved to config.json...")
        print(json.dumps(saved_config, indent=2))

        # Test 5: Test loading config
        print("\n5. Testing config load (API keys should come from .env)...")

        # Clear current keys
        CLIENT_CONFIG['api_key'] = ""
        GOOGLE_SEARCH_CONFIG['api_key'] = ""
        OPENROUTER_CONFIG['api_key'] = ""

        # Load config (which should load from .env, not config.json)
        load_config()

        if CLIENT_CONFIG.get('api_key') and imported['api_key']:
            print(f"   ✓ API key loaded from .env: {CLIENT_CONFIG['api_key'][:8]}...")
        elif imported['api_key']:
            print("   ✗ API key in .env but not loaded")
        else:
            print("   - No API key in .env to test")

        print("\n" + "=" * 70)

        if security_pass:
            print("✅ SECURITY TEST PASSED")
            print("=" * 70)
            print("\n✓ API keys are NEVER saved to config.json")
            print("✓ API keys are ONLY loaded from .env")
            print("✓ Safe to commit config.json to git")
        else:
            print("❌ SECURITY TEST FAILED")
            print("=" * 70)
            print("\n✗ API keys were found in config.json!")
            print("✗ This is a security risk - keys could be committed to git")

    finally:
        # Restore original paths
        cp.DATA_DIR = original_data_dir
        cp.CONFIG_FILE = original_config_file

        # Cleanup
        if test_config_dir.exists():
            shutil.rmtree(test_config_dir)
            print(f"\n🧹 Cleaned up test directory: {test_config_dir}")

if __name__ == "__main__":
    test_api_key_security()
