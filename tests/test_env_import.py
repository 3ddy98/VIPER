"""
Test .env file import functionality
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.config_persistence import load_env_file, import_from_env, ENV_FILE
import json

def test_env_import():
    """Test that .env file is correctly parsed and imported."""

    print("=" * 70)
    print("ENV FILE IMPORT TEST")
    print("=" * 70)

    # Test 1: Check if .env file exists
    print("\n1. Checking for .env file...")
    if ENV_FILE.exists():
        print(f"   ✓ .env file found at: {ENV_FILE}")
    else:
        print(f"   ✗ .env file NOT found at: {ENV_FILE}")
        return

    # Test 2: Load and parse .env file
    print("\n2. Loading .env file...")
    env_vars = load_env_file()

    if env_vars:
        print(f"   ✓ Loaded {len(env_vars)} environment variables:")
        for key, value in env_vars.items():
            # Mask sensitive values
            if 'KEY' in key or 'API' in key:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"     - {key} = {masked_value}")
            else:
                print(f"     - {key} = {value}")
    else:
        print("   ✗ No environment variables loaded")
        return

    # Test 3: Import into config dictionaries
    print("\n3. Importing into config dictionaries...")
    imported = import_from_env()

    print(f"   Import results:")
    print(f"     - API Key: {'✓ Imported' if imported['api_key'] else '✗ Not found'}")
    print(f"     - Google API Key: {'✓ Imported' if imported['google_api_key'] else '✗ Not found'}")
    print(f"     - Google CX ID: {'✓ Imported' if imported['google_cx_id'] else '✗ Not found'}")
    print(f"     - OpenRouter API Key: {'✓ Imported' if imported['openrouter_api_key'] else '✗ Not found'}")

    # Test 4: Verify config dictionaries
    print("\n4. Verifying config dictionaries...")
    from modules.config import CLIENT_CONFIG, GOOGLE_SEARCH_CONFIG, OPENROUTER_CONFIG

    configs_verified = True

    if imported['api_key']:
        if CLIENT_CONFIG.get('api_key'):
            print(f"   ✓ CLIENT_CONFIG['api_key'] = {CLIENT_CONFIG['api_key'][:8]}...")
        else:
            print("   ✗ CLIENT_CONFIG['api_key'] not set")
            configs_verified = False

    if imported['google_api_key']:
        if GOOGLE_SEARCH_CONFIG.get('api_key'):
            print(f"   ✓ GOOGLE_SEARCH_CONFIG['api_key'] = {GOOGLE_SEARCH_CONFIG['api_key'][:8]}...")
        else:
            print("   ✗ GOOGLE_SEARCH_CONFIG['api_key'] not set")
            configs_verified = False

    if imported['google_cx_id']:
        if GOOGLE_SEARCH_CONFIG.get('search_engine_id'):
            print(f"   ✓ GOOGLE_SEARCH_CONFIG['search_engine_id'] = {GOOGLE_SEARCH_CONFIG['search_engine_id']}")
        else:
            print("   ✗ GOOGLE_SEARCH_CONFIG['search_engine_id'] not set")
            configs_verified = False

    if imported['openrouter_api_key']:
        if OPENROUTER_CONFIG.get('api_key'):
            print(f"   ✓ OPENROUTER_CONFIG['api_key'] = {OPENROUTER_CONFIG['api_key'][:8]}...")
        else:
            print("   ✗ OPENROUTER_CONFIG['api_key'] not set")
            configs_verified = False

    # Test 5: Expected .env format
    print("\n5. Expected .env file format:")
    print("   " + "-" * 66)
    print("   # API Keys for VIPER")
    print("   OPENAI_API_KEY=\"your-api-key-here\"")
    print("   GOOGLE_API_KEY=\"your-google-api-key\"")
    print("   GOOGLE_CX_ID=\"your-search-engine-id\"")
    print("   OPEN_ROUTER_API_KEY=\"sk-or-v1-...\"")
    print("   " + "-" * 66)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    # Summary
    keys_found = sum(imported.values())
    print(f"\nSummary:")
    print(f"✓ {keys_found}/4 keys found and imported from .env")
    print(f"✓ Config dictionaries {'verified' if configs_verified else 'FAILED verification'}")

    if keys_found > 0:
        print(f"\n🎉 Onboarding will skip {keys_found} key(s) that were found in .env!")
    else:
        print("\n⚠️  No keys found in .env. Full onboarding will be required.")

if __name__ == "__main__":
    test_env_import()
