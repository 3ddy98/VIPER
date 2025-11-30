"""
Response Preprocessor Module

This module handles preprocessing of AI model responses to convert various formats
into the standard OpenRouter tool calling format.
"""

import re
import json
from typing import Dict, Any, Optional, List


def preprocess_custom_model_response(response: str) -> str:
    """
    Preprocess responses from custom models that use special token formats.

    Handles formats like:
    - <|channel|>analysis<|message|>...
    - to=functions.TOOL_NAME__method_name
    - <|constrain|>json<|message|>{"args"}

    Converts them to standard OpenRouter JSON format:
    {
        "content": "...",
        "tool_calls": [...]
    }

    Args:
        response: Raw response from the model

    Returns:
        Preprocessed response in OpenRouter format
    """
    # Remove all special tokens first to get clean content
    cleaned_response = response

    # Check if this is a tool call response
    if "to=functions." in response or "<|channel|>" in response:
        # Extract the reasoning/analysis content
        analysis_match = re.search(r'<\|channel\|>analysis<\|message\|>(.*?)(?:<\|end\|>|to=functions\.)', response, re.DOTALL)
        content = analysis_match.group(1).strip() if analysis_match else "Processing your request..."

        # Extract tool calls
        tool_calls = []

        # Pattern: to=functions.TOOL_NAME__method_name <|constrain|>json<|message|>{...}
        tool_pattern = r'to=functions\.([A-Z_]+__[a-z_]+)\s*(?:<\|constrain\|>json)?<\|message\|>(\{[^}]*\}|\{\})'

        tool_matches = re.finditer(tool_pattern, response, re.DOTALL)

        call_id = 1
        for match in tool_matches:
            function_name = match.group(1)
            arguments_str = match.group(2).strip()

            # Clean up the arguments string
            arguments_str = re.sub(r'<\|.*?\|>', '', arguments_str).strip()

            # Validate it's proper JSON
            try:
                # Test parse to validate
                json.loads(arguments_str)
            except json.JSONDecodeError:
                # If invalid, use empty object
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
                "content": content,
                "tool_calls": tool_calls
            }
            return json.dumps(result)

    # Check if response is already valid JSON
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            # Validate it's parseable
            data = json.loads(json_str)

            # Clean the content field if present
            if "content" in data and isinstance(data["content"], str):
                content = data["content"]

                # Remove special tokens from content
                content = re.sub(r'<\|[^|]+\|>', '', content).strip()

                # Check if content contains an embedded JSON response
                # Pattern: the model sometimes outputs reasoning followed by the actual JSON it wants to return
                # Example: "analysisWe need to...assistantfinal json{\"content\": \"actual message\"}"
                # Use DOTALL flag to match across newlines
                embedded_json_match = re.search(r'\{[^{}]*"content"[^{}]*\}', content, re.DOTALL)
                if embedded_json_match:
                    try:
                        embedded_data = json.loads(embedded_json_match.group(0))
                        if "content" in embedded_data:
                            # Use the embedded content as the real content
                            data["content"] = embedded_data["content"]
                            return json.dumps(data)
                    except json.JSONDecodeError:
                        pass

                # Remove analysis/assistant/channel/final/json prefixes
                # These are reasoning tokens that shouldn't be in the output
                content = re.sub(r'^(analysis|assistant|channel|final|json|constrain)\s*', '', content, flags=re.IGNORECASE).strip()

                data["content"] = content

            return json.dumps(data)
    except json.JSONDecodeError:
        pass

    # If not a tool call and not valid JSON, wrap in standard format
    # Remove special tokens
    cleaned = re.sub(r'<\|[^|]+\|>', '', response).strip()

    # If there's actual content, wrap it
    if cleaned:
        result = {
            "content": cleaned
        }
        return json.dumps(result)

    # Fallback
    return response


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
