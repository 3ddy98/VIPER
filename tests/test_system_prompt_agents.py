"""
Test that agents are included in the system prompt
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.conversation_manager import ConversationManager
from modules.config_persistence import load_config

def test_agents_in_system_prompt():
    """Test that the system prompt includes the list of agents."""

    print("=" * 70)
    print("SYSTEM PROMPT AGENTS TEST")
    print("=" * 70)

    # Load config
    try:
        load_config()
    except:
        pass  # Config might not exist in test environment

    # Create conversation manager
    manager = ConversationManager()

    # Get the system prompt
    system_prompt = manager.system_prompt

    print("\n" + "=" * 70)
    print("SYSTEM PROMPT CONTENT")
    print("=" * 70)
    print(system_prompt)
    print("\n" + "=" * 70)

    # Check if AGENTS tool is mentioned
    if "AGENTS" in system_prompt:
        print("\n✓ PASS: AGENTS tool found in system prompt")
    else:
        print("\n✗ FAIL: AGENTS tool not found in system prompt")
        return

    # Check if available agents are listed
    if "Available agents:" in system_prompt:
        print("✓ PASS: 'Available agents:' section found")
    else:
        print("✗ FAIL: 'Available agents:' section not found")
        return

    # Check if Coder agent is listed
    if "Coder" in system_prompt:
        print("✓ PASS: Coder agent found in system prompt")
    else:
        print("✗ FAIL: Coder agent not found in system prompt")
        return

    # Extract and display the agents section
    if "Available agents:" in system_prompt:
        agents_section_start = system_prompt.find("Available agents:")
        agents_section_end = system_prompt.find("\n\n", agents_section_start)
        if agents_section_end == -1:
            agents_section_end = len(system_prompt)

        agents_section = system_prompt[agents_section_start:agents_section_end]
        print("\n" + "=" * 70)
        print("AGENTS SECTION IN SYSTEM PROMPT")
        print("=" * 70)
        print(agents_section)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ System prompt correctly includes agents list")
    print("✓ AI will be able to see and invoke available agents")

if __name__ == "__main__":
    test_agents_in_system_prompt()
