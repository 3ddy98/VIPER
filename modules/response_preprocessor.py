"""
Response Preprocessor Module

This module handles preprocessing of AI model responses to convert various formats
into the standard OpenRouter tool calling format.

There are two preprocessors:
1. preprocess_primary_agent_response - For the primary VIPER agent (custom format)
2. preprocess_openrouter_response - For OpenRouter-compatible agents (standard format)
"""

import re
import json
from typing import Dict, Any, Optional, List


def preprocess_primary_agent_response(response: str) -> str:
    """
    Preprocess responses from the primary VIPER agent.

    Expected formats:
    1. Tool calls:
       THOUGHT: reasoning
       TOOL: TOOL_NAME__method
       ARGS: {"param": "value"}

    2. Plan:
       THOUGHT: reasoning
       PLAN: plan_name
       STEP: description
       TOOL: TOOL_NAME__method
       ARGS: {"param": "value"}

    3. Response:
       THOUGHT: reasoning
       RESPONSE: answer to user

    Also handles legacy GPT-OSS channel format and strips special tokens.

    Converts to standard OpenRouter JSON format:
    {
        "content": "...",
        "tool_calls": [...] OR "plan": {...}
    }

    Args:
        response: Raw response from the primary agent

    Returns:
        Preprocessed response in OpenRouter format
    """

    # Step 1: Clean up channel-based format
    # First, extract only the final assistant output (after <|channel|>final)
    final_match = re.search(r'<\|channel\|>final.*?<\|message\|>(.+)$', response, re.DOTALL)
    if final_match:
        response = final_match.group(1)

    # Step 1.5: Handle GPT-OSS "to=TOOL_NAME" format
    # Matches any channel format: commentary to=, analysis to=, etc.
    # Convert: <anything> to=FILE_EXPLORER__read_file {...}
    # To: TOOL: FILE_EXPLORER__read_file\nARGS: {...}
    tool_call_pattern = r'\bto=([A-Za-z0-9_]+)(?:\s*<\|constrain\|>\w+)?(?:\s*<\|message\|>)?\s*(\{[^}]*\})'
    tool_call_matches = list(re.finditer(tool_call_pattern, response, re.DOTALL | re.IGNORECASE))

    if tool_call_matches:
        # Found GPT-OSS "to=" format - convert to standard format
        converted_response = response
        for match in reversed(tool_call_matches):  # Reverse to preserve positions
            tool_name = match.group(1)
            args_json = match.group(2)

            # Extract THOUGHT if present before the tool call
            thought_before = converted_response[:match.start()]
            thought_match = re.search(r'THOUGHT:\s*(.+?)(?=\bto=|$)', thought_before, re.DOTALL | re.IGNORECASE)
            thought = thought_match.group(1).strip() if thought_match else ""

            # Build standard format
            standard_format = f"THOUGHT: {thought}\nTOOL: {tool_name}\nARGS: {args_json}"

            # Replace the "to=" block
            converted_response = converted_response[:match.start()] + standard_format + converted_response[match.end():]

        response = converted_response

    # Remove any remaining special tokens
    cleaned_response = re.sub(r'<\|channel\|>[^<]*<\|message\|>', '', response)
    cleaned_response = re.sub(r'<\|end\|>', '', cleaned_response)
    cleaned_response = re.sub(r'<\|start\|>assistant', '', cleaned_response)
    cleaned_response = re.sub(r'<\|constrain\|>\w+', '', cleaned_response)
    cleaned_response = re.sub(r'<\|[^|]+\|>', '', cleaned_response)

    # Use cleaned response for parsing
    response = cleaned_response.strip()

    # Extract THOUGHT content (reasoning)
    thought_match = re.search(r'THOUGHT:\s*(.+?)(?=(?:TOOL:|PLAN:|RESPONSE:|$))', response, re.DOTALL | re.IGNORECASE)
    thought_content = thought_match.group(1).strip() if thought_match else "Processing..."

    # Check if this has PLAN: directive (multi-step plan)
    if re.search(r'PLAN:\s*', response, re.IGNORECASE):
        plan_match = re.search(r'PLAN:\s*([^\n]+)', response, re.IGNORECASE)
        plan_name = plan_match.group(1).strip() if plan_match else "Unnamed Plan"

        # Extract all STEP blocks
        steps = []
        step_blocks = re.finditer(
            r'STEP:\s*([^\n]+)\s*\n\s*TOOL:\s*([A-Za-z0-9_]+)\s*\n\s*ARGS:\s*(\{[^\n]*\})',
            response,
            re.DOTALL | re.IGNORECASE
        )

        for step_idx, step_match in enumerate(step_blocks, 1):
            step_description = step_match.group(1).strip()
            tool_name = step_match.group(2).strip()
            args_str = step_match.group(3).strip()

            # Validate JSON
            try:
                json.loads(args_str)
            except json.JSONDecodeError:
                args_str = "{}"

            steps.append({
                "step_number": step_idx,
                "description": step_description,
                "tool": tool_name,
                "arguments": args_str
            })

        if steps:
            result = {
                "content": thought_content,
                "plan": {
                    "name": plan_name,
                    "steps": steps
                }
            }
            return json.dumps(result)

    # Check if this has TOOL: directives (tool calls)
    if re.search(r'TOOL:\s*', response, re.IGNORECASE):
        tool_calls = []

        # Find all TOOL: directives first
        tool_matches = list(re.finditer(r'TOOL:\s*([A-Za-z0-9_]+)', response, re.IGNORECASE))

        call_id = 1
        for i, tool_match in enumerate(tool_matches):
            function_name = tool_match.group(1).strip()

            # Find the ARGS: that follows this TOOL:
            # Look for ARGS: between this TOOL and the next TOOL (or end of string)
            start_pos = tool_match.end()
            end_pos = tool_matches[i + 1].start() if i + 1 < len(tool_matches) else len(response)
            segment = response[start_pos:end_pos]

            # Extract JSON from ARGS: line
            args_match = re.search(r'ARGS:\s*(\{.*?\})\s*(?=\n|$)', segment, re.DOTALL)

            if args_match:
                arguments_str = args_match.group(1).strip()

                # Try to find balanced braces for nested JSON
                # Start from the first { and count braces
                brace_count = 0
                start_idx = arguments_str.find('{')
                if start_idx != -1:
                    end_idx = start_idx
                    for j, char in enumerate(arguments_str[start_idx:], start=start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = j + 1
                                break
                    arguments_str = arguments_str[start_idx:end_idx]

                # Validate it's proper JSON
                try:
                    json.loads(arguments_str)
                except json.JSONDecodeError:
                    # If invalid, use empty object
                    arguments_str = "{}"
            else:
                arguments_str = "{}"

            tool_call = {
                "id": f"call_{call_id}",
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": arguments_str
                }
            }
            tool_calls.append(tool_call)
            call_id += 1

        # Build OpenRouter format response
        if tool_calls:
            result = {
                "content": thought_content,
                "tool_calls": tool_calls
            }
            return json.dumps(result)

    # Check for RESPONSE: directive (direct answer)
    response_match = re.search(r'RESPONSE:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
    if response_match:
        content = response_match.group(1).strip()
        result = {
            "content": content
        }
        return json.dumps(result)

    # Fallback: Return the whole response as content
    result = {
        "content": response.strip()
    }
    return json.dumps(result)


def preprocess_openrouter_response(response: str) -> str:
    """
    Preprocess responses from OpenRouter-compatible agents.

    This handles standard OpenRouter JSON format and ensures clean output.
    Does NOT handle custom token formats like <|channel|> or to=functions.

    Args:
        response: Raw response from OpenRouter agent

    Returns:
        Preprocessed response in OpenRouter format
    """
    # Check if response is already valid JSON
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            # Validate it's parseable
            data = json.loads(json_str)

            # Return as-is if it's valid OpenRouter format
            return json.dumps(data)
    except json.JSONDecodeError:
        pass

    # If not valid JSON, wrap in standard format
    result = {
        "content": response.strip()
    }
    return json.dumps(result)


def preprocess_custom_model_response(response: str) -> str:
    """
    Legacy function name - kept for backward compatibility.

    Delegates to preprocess_primary_agent_response().

    Args:
        response: Raw response from the model

    Returns:
        Preprocessed response in OpenRouter format
    """
    return preprocess_primary_agent_response(response)


def extract_content_from_response(response: str) -> str:
    """
    Extract clean content from a response, removing special tokens.

    Args:
        response: Raw response from model

    Returns:
        Clean content string
    """
    # Remove special tokens
    cleaned = re.sub(r'<\|[^|]+\|>', '', response)

    # Try to parse as JSON and extract content field
    try:
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            if "content" in data:
                return data["content"]
    except json.JSONDecodeError:
        pass

    return cleaned.strip()


def is_tool_call_response(response: str) -> bool:
    """
    Check if a response contains tool calls.

    Args:
        response: Raw response from model

    Returns:
        True if response contains tool calls
    """
    return "to=functions." in response or '"tool_calls"' in response
