"""
Test script for the Agents Tool with tool calling support
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.tool_manager import ToolManager
import json

def test_agents_tool():
    """Test the agents tool integration."""

    print("=" * 60)
    print("AGENTS TOOL TEST")
    print("=" * 60)

    # Initialize tool manager
    print("\n1. Initializing ToolManager...")
    tm = ToolManager()
    print(f"   ✓ Loaded {len(tm.tools)} tools")

    # Get agents tool
    print("\n2. Getting AGENTS tool...")
    agents_tool = tm.tools.get('AGENTS')
    if not agents_tool:
        print("   ✗ AGENTS tool not found!")
        return
    print("   ✓ AGENTS tool loaded")

    # Check tool manager integration
    print("\n3. Checking tool_manager integration...")
    if hasattr(agents_tool, 'tool_manager') and agents_tool.tool_manager:
        print("   ✓ tool_manager is set")
    else:
        print("   ✗ tool_manager is NOT set")
        return

    # List available agents
    print("\n4. Listing available agents...")
    result = agents_tool.list_agents()
    if result.get('success'):
        print(f"   ✓ Found {result['count']} agents:")
        for name, info in result['agents'].items():
            print(f"     - {name}: {info['description']}")
            print(f"       Model: {info['model']}")
    else:
        print(f"   ✗ Error: {result.get('error')}")

    # Test OpenRouter schema conversion
    print("\n5. Testing OpenRouter schema conversion...")
    schemas = agents_tool._convert_viper_tools_to_openrouter_schema()
    print(f"   ✓ Converted {len(schemas)} tool methods to OpenRouter format")
    print(f"   Example tools: {', '.join([s['function']['name'].split('__')[0] for s in schemas[:3]])}")

    # Get tool spec
    print("\n6. Getting tool specification...")
    spec = agents_tool.get_tool_spec()
    print(f"   ✓ Tool name: {spec['tool_name']}")
    print(f"   ✓ Methods: {', '.join([m['name'] for m in spec['methods']])}")

    # Show what the AI will see
    print("\n7. Tool description for AI:")
    print("   " + "-" * 56)
    desc_lines = spec['description'].split('\n')
    for line in desc_lines[:5]:
        print(f"   {line}")
    if len(desc_lines) > 5:
        print(f"   ... ({len(desc_lines) - 5} more lines)")
    print("   " + "-" * 56)

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nThe AGENTS tool is ready to use!")
    print("Agents can now invoke other agents with full tool access.")

if __name__ == "__main__":
    test_agents_tool()
