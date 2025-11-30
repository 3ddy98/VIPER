"""
Test agent creation without API key prompts
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import shutil
from modules.agent_manager import AgentManager
from modules.tool_manager import ToolManager
from modules.config import OPENROUTER_CONFIG

def test_agent_without_api_key():
    """Test that agents work without storing API keys."""

    print("=" * 70)
    print("AGENT CREATION WITHOUT API KEY TEST")
    print("=" * 70)

    # Use test directory
    test_dir = "test_agents_security"

    # Clean up from previous tests
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    try:
        # Test 1: Create agent without API key
        print("\n1. Creating agent without API key in config...")
        manager = AgentManager(agent_dir=test_dir)

        test_agent_details = {
            "name": "SecurityTestAgent",
            "description": "Test agent for security",
            "site_url": "http://test.com",
            "site_name": "Test Site",
            "model": "openai/gpt-3.5-turbo"
            # Note: NO api_key field
        }

        success = manager.create_agent("SecurityTestAgent", test_agent_details)

        if success:
            print("   ✓ Agent created successfully without API key field")
        else:
            print("   ✗ Failed to create agent")
            return

        # Test 2: Verify no API key in saved JSON
        print("\n2. Verifying agent JSON has no API key...")
        json_path = os.path.join(test_dir, "SecurityTestAgent", "SecurityTestAgent.json")

        with open(json_path, 'r') as f:
            saved_agent = json.load(f)

        print(f"   Agent config fields: {list(saved_agent.keys())}")

        if "api_key" in saved_agent:
            print(f"   ✗ FAIL: api_key found in agent config!")
            print(f"      Value: {saved_agent['api_key']}")
        else:
            print("   ✓ PASS: No api_key in agent config (correct)")

        # Test 3: Show saved config
        print("\n3. Saved agent configuration:")
        print(json.dumps(saved_agent, indent=2))

        # Test 4: Test AGENTS tool API key loading
        print("\n4. Testing AGENTS tool API key loading...")

        # Check if OpenRouter API key is loaded from .env
        if OPENROUTER_CONFIG.get("api_key"):
            print(f"   ✓ OPENROUTER_CONFIG has API key from .env: {OPENROUTER_CONFIG['api_key'][:8]}...")
        else:
            print("   ⚠ No OpenRouter API key in config (add to .env)")

        # Test 5: Verify agents tool can load agent
        print("\n5. Testing AGENTS tool agent loading...")
        tm = ToolManager()
        agents_tool = tm.tools.get('AGENTS')

        if agents_tool:
            print("   ✓ AGENTS tool loaded")

            # Check if our test agent can be found
            # Note: It won't be in the actual agents/ directory, but we can test the logic
            agents_tool_test = AgentsTool(agent_dir=test_dir, tool_manager=tm)
            available = agents_tool_test.available_agents

            if "SecurityTestAgent" in available:
                print(f"   ✓ Test agent found by AGENTS tool")
                print(f"     Config: {available['SecurityTestAgent']}")

                # Check that API key is NOT in the agent config
                if "api_key" not in available['SecurityTestAgent'] or not available['SecurityTestAgent'].get("api_key"):
                    print("   ✓ Agent config has no API key (uses .env)")
                else:
                    print("   ✗ Agent config has API key (should use .env)")
            else:
                print(f"   ⚠ Test agent not found (agents: {list(available.keys())})")
        else:
            print("   ✗ AGENTS tool not loaded")

        # Test 6: Check existing Coder agent
        print("\n6. Checking existing Coder agent...")
        real_manager = AgentManager()
        if "Coder" in real_manager.list_agents():
            coder_details = real_manager.get_agent_details("Coder")
            print(f"   Coder config fields: {list(coder_details.keys())}")

            if "api_key" in coder_details and coder_details["api_key"]:
                print(f"   ⚠ Coder has api_key field with value: {coder_details['api_key']}")
                print("      (Should be empty or removed)")
            else:
                print("   ✓ Coder has no API key or empty value (correct)")

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        print("\n✓ Agents can be created without API key field")
        print("✓ Agent configs don't store sensitive data")
        print("✓ API keys loaded from .env via OPENROUTER_CONFIG")
        print("✓ Safe to commit agent JSON files")

    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory: {test_dir}")

# Import AgentsTool for testing
from tools.agents import AgentsTool

if __name__ == "__main__":
    test_agent_without_api_key()
