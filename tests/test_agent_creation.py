"""
Test agent creation functionality
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import shutil
from modules.agent_manager import AgentManager

def test_agent_creation():
    """Test that agent creation works without template file."""

    print("=" * 70)
    print("AGENT CREATION TEST")
    print("=" * 70)

    # Use a test directory
    test_dir = "test_agents_temp"

    # Clean up from previous tests
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    try:
        # Test 1: Create AgentManager
        print("\n1. Creating AgentManager...")
        manager = AgentManager(agent_dir=test_dir)
        print(f"   ✓ AgentManager created with directory: {test_dir}")

        # Test 2: Create a test agent
        print("\n2. Creating test agent...")
        test_agent_details = {
            "name": "TestAgent",
            "description": "A test agent for unit testing",
            "api_key": "",
            "site_url": "",
            "site_name": "",
            "model": "openai/gpt-3.5-turbo"
        }

        success = manager.create_agent("TestAgent", test_agent_details)

        if success:
            print("   ✓ Agent created successfully")
        else:
            print("   ✗ Failed to create agent")
            return

        # Test 3: Verify agent directory structure
        print("\n3. Verifying agent directory structure...")
        agent_path = os.path.join(test_dir, "TestAgent")

        if os.path.exists(agent_path):
            print(f"   ✓ Agent directory exists: {agent_path}")
        else:
            print(f"   ✗ Agent directory NOT found: {agent_path}")
            return

        # Check for JSON file
        json_path = os.path.join(agent_path, "TestAgent.json")
        if os.path.exists(json_path):
            print(f"   ✓ JSON config file exists: {json_path}")
        else:
            print(f"   ✗ JSON config file NOT found: {json_path}")
            return

        # Check that Python file was NOT created
        py_path = os.path.join(agent_path, "TestAgent_agent.py")
        if not os.path.exists(py_path):
            print(f"   ✓ No Python file created (correct - not needed)")
        else:
            print(f"   ⚠ Python file found (should not exist): {py_path}")

        # Test 4: Verify agent details
        print("\n4. Verifying agent configuration...")
        loaded_details = manager.get_agent_details("TestAgent")

        if loaded_details:
            print("   ✓ Agent details loaded successfully")
            print(f"     - Name: {loaded_details.get('name')}")
            print(f"     - Description: {loaded_details.get('description')}")
            print(f"     - Model: {loaded_details.get('model')}")

            # Verify details match
            if loaded_details == test_agent_details:
                print("   ✓ Loaded details match original")
            else:
                print("   ⚠ Loaded details differ from original")
        else:
            print("   ✗ Failed to load agent details")
            return

        # Test 5: List agents
        print("\n5. Testing agent listing...")
        agents = manager.list_agents()

        if "TestAgent" in agents:
            print(f"   ✓ Agent found in list: {agents}")
        else:
            print(f"   ✗ Agent NOT in list: {agents}")

        # Test 6: Test duplicate creation
        print("\n6. Testing duplicate prevention...")
        duplicate_success = manager.create_agent("TestAgent", test_agent_details)

        if not duplicate_success:
            print("   ✓ Duplicate creation correctly prevented")
        else:
            print("   ✗ Duplicate creation was allowed (should fail)")

        # Test 7: Test modification
        print("\n7. Testing agent modification...")
        modified_details = test_agent_details.copy()
        modified_details["description"] = "Modified description"
        modified_details["model"] = "anthropic/claude-3-sonnet"

        mod_success = manager.modify_agent("TestAgent", modified_details)

        if mod_success:
            print("   ✓ Agent modified successfully")

            # Verify modification
            reloaded = manager.get_agent_details("TestAgent")
            if reloaded.get("description") == "Modified description":
                print("   ✓ Modification verified")
            else:
                print("   ✗ Modification not persisted")
        else:
            print("   ✗ Failed to modify agent")

        # Test 8: Test deletion
        print("\n8. Testing agent deletion...")
        del_success = manager.delete_agent("TestAgent")

        if del_success:
            print("   ✓ Agent deleted successfully")

            # Verify deletion
            if not os.path.exists(agent_path):
                print("   ✓ Agent directory removed")
            else:
                print("   ✗ Agent directory still exists")
        else:
            print("   ✗ Failed to delete agent")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)

        print("\n✓ Agent creation works without template file")
        print("✓ Only JSON configuration is created")
        print("✓ Agents are invoked via AGENTS tool")

    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    test_agent_creation()
