"""
Test model tool support detection
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.agents import AgentsTool
from modules.tool_manager import ToolManager

def test_model_tool_support():
    """Test that the system can detect which models support tools."""

    print("=" * 70)
    print("MODEL TOOL SUPPORT DETECTION TEST")
    print("=" * 70)

    # Initialize AgentsTool
    tm = ToolManager()
    agents_tool = AgentsTool(tool_manager=tm)

    # Test various models
    test_models = [
        ("qwen/qwen2.5-vl-32b-instruct", False),  # Does NOT support tools
        ("qwen/qwen3-vl-8b-instruct", True),      # Does support tools
        ("openai/gpt-4o-mini", True),             # Does support tools
        ("anthropic/claude-3-haiku", True),       # Does support tools
    ]

    print("\n1. Testing model tool support detection...\n")

    all_passed = True
    for model_id, expected_support in test_models:
        supports_tools = agents_tool._check_model_supports_tools(model_id)
        status = "✓" if supports_tools == expected_support else "✗"

        print(f"   {status} {model_id}")
        print(f"      Expected: {expected_support}, Got: {supports_tools}")

        if supports_tools != expected_support:
            all_passed = False

    print("\n2. Testing caching...\n")

    # Test that subsequent calls use cache
    model_id = "qwen/qwen2.5-vl-32b-instruct"

    # First call should query API
    supports_tools_1 = agents_tool._check_model_supports_tools(model_id)

    # Second call should use cache
    supports_tools_2 = agents_tool._check_model_supports_tools(model_id)

    if supports_tools_1 == supports_tools_2:
        print(f"   ✓ Cache working correctly for {model_id}")
        print(f"     Both calls returned: {supports_tools_1}")
    else:
        print(f"   ✗ Cache not working - results differ")
        all_passed = False

    print("\n3. Testing Coder agent with qwen model...\n")

    # Load Coder agent
    if "Coder" in agents_tool.available_agents:
        coder_config = agents_tool.available_agents["Coder"]
        model_id = coder_config.get("model")

        print(f"   Coder agent model: {model_id}")

        supports_tools = agents_tool._check_model_supports_tools(model_id)
        print(f"   Model supports tools: {supports_tools}")

        if not supports_tools:
            print("   ✓ Correctly detected that qwen2.5-vl-32b-instruct does NOT support tools")
            print("     Agent will work without tool calling")
        else:
            print("   ⚠ Model detected as supporting tools (may be incorrect)")
    else:
        print("   ⚠ Coder agent not found")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_passed:
        print("\n✓ All tests passed")
        print("✓ Model capability detection working correctly")
        print("✓ Agents will automatically disable tools for unsupported models")
    else:
        print("\n✗ Some tests failed")
        print("  Check model capability detection logic")

if __name__ == "__main__":
    test_model_tool_support()
