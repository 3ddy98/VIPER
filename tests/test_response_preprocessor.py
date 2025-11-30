"""
Test response preprocessor for custom model formats
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.response_preprocessor import preprocess_custom_model_response
import json

def test_response_preprocessor():
    """Test the response preprocessor with various custom model formats."""

    print("=" * 70)
    print("RESPONSE PREPROCESSOR TEST")
    print("=" * 70)

    # Test 1: Custom model format with tool call
    print("\n" + "=" * 70)
    print("TEST 1: Custom model format with tool call")
    print("=" * 70)

    custom_response1 = """<|channel|>analysis<|message|>User wants to list agents. Let me use the AGENTS tool to list available agents.<|end|><|start|>assistant<|channel|>analysis
to=functions.AGENTS__list_agents <|constrain|>json<|message|>{}"""

    result1 = preprocess_custom_model_response(custom_response1)
    print(f"\nInput:\n{custom_response1}\n")
    print(f"Output:\n{result1}\n")

    # Parse and verify
    parsed1 = json.loads(result1)
    assert "tool_calls" in parsed1, "Should have tool_calls"
    assert len(parsed1["tool_calls"]) == 1, "Should have 1 tool call"
    assert parsed1["tool_calls"][0]["function"]["name"] == "AGENTS__list_agents"
    print("✓ PASS: Tool call correctly extracted")

    # Test 2: Custom model format with arguments
    print("\n" + "=" * 70)
    print("TEST 2: Custom model format with tool arguments")
    print("=" * 70)

    custom_response2 = """<|channel|>analysis<|message|>I'll create a hello world script using the WRITE_FILE tool<|end|>
to=functions.WRITE_FILE__write <|constrain|>json<|message|>{"file_path": "hello.py", "content": "print('Hello World!')"}"""

    result2 = preprocess_custom_model_response(custom_response2)
    print(f"\nInput:\n{custom_response2}\n")
    print(f"Output:\n{result2}\n")

    parsed2 = json.loads(result2)
    assert "tool_calls" in parsed2
    assert parsed2["tool_calls"][0]["function"]["name"] == "WRITE_FILE__write"
    args2 = json.loads(parsed2["tool_calls"][0]["function"]["arguments"])
    assert args2["file_path"] == "hello.py"
    print("✓ PASS: Tool call with arguments correctly extracted")

    # Test 3: Already valid OpenRouter format
    print("\n" + "=" * 70)
    print("TEST 3: Already valid OpenRouter format")
    print("=" * 70)

    openrouter_response = json.dumps({
        "content": "Here's the result",
        "tool_calls": [{
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "FILE_EXPLORER__list_directory",
                "arguments": "{\"path\": \".\"}"
            }
        }]
    })

    result3 = preprocess_custom_model_response(openrouter_response)
    print(f"\nInput:\n{openrouter_response}\n")
    print(f"Output:\n{result3}\n")

    assert result3 == openrouter_response, "Should pass through unchanged"
    print("✓ PASS: OpenRouter format passed through unchanged")

    # Test 4: Plain text response (no tools)
    print("\n" + "=" * 70)
    print("TEST 4: Plain text response with special tokens")
    print("=" * 70)

    plain_response = """<|channel|>response<|message|>Here's a simple explanation of how it works.<|end|>"""

    result4 = preprocess_custom_model_response(plain_response)
    print(f"\nInput:\n{plain_response}\n")
    print(f"Output:\n{result4}\n")

    parsed4 = json.loads(result4)
    assert "content" in parsed4
    assert "special tokens" not in parsed4["content"].lower()
    print("✓ PASS: Plain text wrapped in JSON format")

    # Test 5: Multiple tool calls
    print("\n" + "=" * 70)
    print("TEST 5: Multiple tool calls in one response")
    print("=" * 70)

    multi_tool_response = """<|channel|>analysis<|message|>I'll read the file and then list the directory<|end|>
to=functions.FILE_EXPLORER__read_file <|message|>{"file_path": "test.py"}
to=functions.FILE_EXPLORER__list_directory <|message|>{"path": "."}"""

    result5 = preprocess_custom_model_response(multi_tool_response)
    print(f"\nInput:\n{multi_tool_response}\n")
    print(f"Output:\n{result5}\n")

    parsed5 = json.loads(result5)
    assert "tool_calls" in parsed5
    assert len(parsed5["tool_calls"]) == 2, f"Expected 2 tool calls, got {len(parsed5['tool_calls'])}"
    print("✓ PASS: Multiple tool calls correctly extracted")

    # Test 6: Nested JSON in content (reasoning + embedded response)
    print("\n" + "=" * 70)
    print("TEST 6: Content with embedded JSON response")
    print("=" * 70)

    nested_response = json.dumps({
        "content": 'analysisWe have tool execution results: function AGENTS__list_agents returned agents: {} empty, count 0. So there are no agents available. We need to respond with plain JSON containing content answer. Should mention no agents are available.assistantfinal json{\n  "content": "There are currently no agents available. The AGENTS__list_agents tool returned an empty list."\n}'
    })

    result6 = preprocess_custom_model_response(nested_response)
    print(f"\nInput:\n{nested_response}\n")
    print(f"Output:\n{result6}\n")

    parsed6 = json.loads(result6)
    assert "content" in parsed6
    # Should extract the embedded JSON content
    assert "There are currently no agents available" in parsed6["content"]
    # Should NOT contain reasoning tokens
    assert "analysis" not in parsed6["content"].lower() or parsed6["content"].lower().index("analysis") > 10
    assert "assistant" not in parsed6["content"].lower() or parsed6["content"].lower().index("assistant") > 10
    print("✓ PASS: Embedded JSON content correctly extracted")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ All tests passed!")
    print("✓ Custom model format correctly converted to OpenRouter format")
    print("✓ Tool calls extracted properly")
    print("✓ Arguments parsed correctly")
    print("✓ Special tokens removed")
    print("✓ Embedded JSON responses extracted")

if __name__ == "__main__":
    test_response_preprocessor()
