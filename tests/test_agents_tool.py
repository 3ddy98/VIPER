"""
Test AGENTS tool can find agents from any directory
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.agents import AgentsTool
from pathlib import Path

def test_agents_tool_path_resolution():
    """Test that AGENTS tool finds agents from any working directory."""

    print("=" * 70)
    print("AGENTS TOOL PATH RESOLUTION TEST")
    print("=" * 70)

    # Store original directory
    original_cwd = Path.cwd()
    print(f"\nOriginal CWD: {original_cwd}")

    # Test 1: From VIPER directory
    print("\n" + "=" * 70)
    print("TEST 1: Initialize AGENTS tool from VIPER directory")
    print("=" * 70)

    agents_tool = AgentsTool()
    print(f"Agent directory: {agents_tool.agent_dir}")
    print(f"Available agents: {list(agents_tool.available_agents.keys())}")

    assert len(agents_tool.available_agents) > 0, "Should find at least one agent"
    assert "Coder" in agents_tool.available_agents, "Should find Coder agent"
    print("✓ PASS: Found agents from VIPER directory")

    # Test 2: From different directory
    print("\n" + "=" * 70)
    print("TEST 2: Initialize AGENTS tool from different directory")
    print("=" * 70)

    # Change to parent directory
    test_dir = original_cwd.parent
    os.chdir(test_dir)
    print(f"Changed CWD to: {Path.cwd()}")

    # Create new instance
    agents_tool2 = AgentsTool()
    print(f"Agent directory: {agents_tool2.agent_dir}")
    print(f"Available agents: {list(agents_tool2.available_agents.keys())}")

    assert len(agents_tool2.available_agents) > 0, "Should still find agents from different directory"
    assert "Coder" in agents_tool2.available_agents, "Should still find Coder agent"
    print("✓ PASS: Found agents from different directory")

    # Restore directory
    os.chdir(original_cwd)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ AGENTS tool correctly finds agents from any working directory")
    print(f"✓ Agent directory resolves to: {agents_tool2.agent_dir}")
    print(f"✓ Found {len(agents_tool2.available_agents)} agent(s): {', '.join(agents_tool2.available_agents.keys())}")

if __name__ == "__main__":
    test_agents_tool_path_resolution()
