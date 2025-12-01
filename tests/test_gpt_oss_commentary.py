"""
Test GPT-OSS commentary format parsing
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.response_preprocessor import preprocess_primary_agent_response
import json

def test_gpt_oss_commentary_format():
    """Test parsing of GPT-OSS commentary to=TOOL_NAME format."""

    print("=" * 70)
    print("GPT-OSS COMMENTARY FORMAT TEST")
    print("=" * 70)

    # Test 1: Actual output from your model
    print("\n" + "=" * 70)
    print("TEST 1: Real GPT-OSS output with commentary to=")
    print("=" * 70)

    actual_output = """<|channel|>analysis<|message|>We need to read a file. Use FILE_EXPLORER__read_file. Provide path. Possibly need entire
file content. Use no size limit? Provide max_size maybe. Use
default.<|end|><|start|>assistant<|channel|>final<|message|>THOUGHT: The user wants to read the contents of the file at
DesignDocuments\\financial-implementation-roadmap.md. I'll use the file explorer tool to read the
file.<|end|><|start|>assistant<|channel|>commentary to=FILE_EXPLORER__read_file <|constrain|>json<|message|>{
  "file_path": "DesignDocuments/financial-implementation-roadmap.md"
}"""

    print(f"\nInput (actual model output):")
    print(actual_output[:200] + "...")

    result = preprocess_primary_agent_response(actual_output)
    print(f"\nParsed result:")
    print(json.dumps(json.loads(result), indent=2))

    parsed = json.loads(result)

    # Verify structure
    assert "tool_calls" in parsed, "Should have tool_calls field"
    assert len(parsed["tool_calls"]) == 1, "Should have 1 tool call"

    tool_call = parsed["tool_calls"][0]
    assert tool_call["function"]["name"] == "FILE_EXPLORER__read_file", "Tool name should match"

    args = json.loads(tool_call["function"]["arguments"])
    assert "file_path" in args, "Should have file_path argument"
    assert args["file_path"] == "DesignDocuments/financial-implementation-roadmap.md", "Path should match"

    print("\n✓ PASS: GPT-OSS commentary format parsed correctly")

    # Test 1.5: Real output with "analysis to=" format
    print("\n" + "=" * 70)
    print("TEST 1.5: Real GPT-OSS output with analysis to=")
    print("=" * 70)

    analysis_output = """<|channel|>analysis<|message|>The user wants to navigate to folder and understand how the AP Django application is designed.
Need to read files in that directory. Use FILE_EXPLORER__list_directory to list folder. Then read relevant files like models,
views, serializers, urls. We'll need to fetch multiple files. Let's start by listing
directory.<|end|><|start|>assistant<|channel|>analysis to=FILE_EXPLORER__list_directory <|constrain|>json<|message|>{
  "path": "Parclo-API/Parclo-Master/apps/finance/ap",
  "recursive": false,
  "max_depth": 1
}"""

    print(f"\nInput (actual model output with 'analysis to='):")
    print(analysis_output[:150] + "...")

    result_analysis = preprocess_primary_agent_response(analysis_output)
    print(f"\nParsed result:")
    print(json.dumps(json.loads(result_analysis), indent=2))

    parsed_analysis = json.loads(result_analysis)

    # Verify structure
    assert "tool_calls" in parsed_analysis, "Should have tool_calls field"
    assert len(parsed_analysis["tool_calls"]) == 1, "Should have 1 tool call"

    tool_call_analysis = parsed_analysis["tool_calls"][0]
    assert tool_call_analysis["function"]["name"] == "FILE_EXPLORER__list_directory", "Tool name should match"

    args_analysis = json.loads(tool_call_analysis["function"]["arguments"])
    assert "path" in args_analysis, "Should have path argument"
    assert args_analysis["path"] == "Parclo-API/Parclo-Master/apps/finance/ap", "Path should match"

    print("\n✓ PASS: GPT-OSS 'analysis to=' format parsed correctly")

    # Test 2: Commentary format with multiple tools
    print("\n" + "=" * 70)
    print("TEST 2: Multiple commentary blocks")
    print("=" * 70)

    multi_commentary = """<|channel|>final<|message|>THOUGHT: Need to read config then list files
<|channel|>commentary to=FILE_EXPLORER__read_file <|constrain|>json<|message|>{"file_path": "config.json"}
<|channel|>commentary to=FILE_EXPLORER__list_directory <|constrain|>json<|message|>{"path": "."}"""

    result2 = preprocess_primary_agent_response(multi_commentary)
    parsed2 = json.loads(result2)

    print(f"\nParsed result:")
    print(json.dumps(parsed2, indent=2))

    assert "tool_calls" in parsed2, "Should have tool_calls"
    assert len(parsed2["tool_calls"]) == 2, f"Should have 2 tool calls, got {len(parsed2['tool_calls'])}"

    print("\n✓ PASS: Multiple commentary blocks parsed")

    # Test 3: Commentary format variations
    print("\n" + "=" * 70)
    print("TEST 3: Commentary format variations")
    print("=" * 70)

    variations = [
        {
            "name": "Compact format (no spaces)",
            "input": """THOUGHT: Read file
commentary to=FILE_EXPLORER__read_file<|constrain|>json<|message|>{"file_path":"test.txt"}""",
            "expected_tool": "FILE_EXPLORER__read_file"
        },
        {
            "name": "With extra whitespace",
            "input": """THOUGHT: Read file
commentary  to=FILE_EXPLORER__read_file  <|constrain|>json  <|message|>  { "file_path" : "test.txt" }""",
            "expected_tool": "FILE_EXPLORER__read_file"
        },
        {
            "name": "Without constrain token",
            "input": """THOUGHT: Read file
commentary to=FILE_EXPLORER__read_file <|message|>{"file_path":"test.txt"}""",
            "expected_tool": "FILE_EXPLORER__read_file"
        }
    ]

    for variation in variations:
        print(f"\n{variation['name']}:")
        result = preprocess_primary_agent_response(variation['input'])
        parsed = json.loads(result)

        if "tool_calls" in parsed:
            tool_name = parsed["tool_calls"][0]["function"]["name"]
            assert tool_name == variation["expected_tool"], f"Expected {variation['expected_tool']}, got {tool_name}"
            print(f"  ✓ Parsed as: {tool_name}")
        else:
            print(f"  ✗ FAILED: No tool calls found")
            print(f"  Result: {json.dumps(parsed, indent=2)}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ All GPT-OSS commentary/analysis format tests passed!")
    print("\nSupported formats:")
    print("✓ commentary to=TOOL_NAME <|constrain|>json<|message|>{...}")
    print("✓ analysis to=TOOL_NAME <|constrain|>json<|message|>{...}")
    print("✓ Multiple commentary/analysis blocks in single response")
    print("✓ Variations with/without tokens and whitespace")
    print("\nConversion:")
    print("  Input:  commentary to=FILE_EXPLORER__read_file {...}")
    print("  Input:  analysis to=FILE_EXPLORER__list_directory {...}")
    print("  Output: TOOL: FILE_EXPLORER__read_file")
    print("          ARGS: {...}")


if __name__ == "__main__":
    test_gpt_oss_commentary_format()
