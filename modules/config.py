"""
Configuration file for VIPER

This module contains all configuration constants used throughout the application.
"""

from pathlib import Path
from modules.paths import get_data_dir

# OpenAI API Configuration
# These settings configure the connection to the AI model
CLIENT_CONFIG = {
    "base_url": "http://100.111.249.91:8000/v1",  # Custom API endpoint
    "api_key": "",                                 # Populated from config.json at runtime
    "model": "gpt-oss-120B",                        # Model identifier
    "token_window_size": 4096                      # Maximum number of tokens for the conversation context
}

# Tool execution configuration
# Controls automatic execution of tool methods
TOOL_CONFIG = {
    "auto_execute_non_destructive": True,   # Auto-execute read-only operations
    "auto_execute_destructive": False,      # Require confirmation for destructive operations
    "tools_enabled": True                   # Master switch for tool usage
}

# UI Configuration
# Controls the user interface appearance and behavior
UI_CONFIG = {
    "show_streaming": True  # If False, shows a spinner instead of live text
}

# Context Management Configuration
CONTEXT_CONFIG = {
    "compression_threshold": 0.8,      # Compress context when it reaches 80% of the token window
    "historical_messages_to_load": 10  # Number of recent messages to load when switching conversations
}


# File paths
CONVERSATIONS_FILE = get_data_dir() / "conversations.json"  # Storage file for conversation history in VIPER installation

# System prompt template
# This prompt instructs the AI to respond using OpenRouter's standard tool calling format
SYSTEM_PROMPT = """You are a helpful coding assistant with access to tools.

AVAILABLE TOOLS:
{TOOLS_SPEC}

HOW TO USE TOOLS:

When you need to use a tool, respond in standard OpenRouter format with tool_calls:

{
  "content": "I'll help you with that. Let me check the file contents.",
  "tool_calls": [
    {
      "id": "call_1",
      "type": "function",
      "function": {
        "name": "FILE_EXPLORER__read_file",
        "arguments": "{\\"file_path\\": \\"example.py\\", \\"start_line\\": 1, \\"line_count\\": 50}"
      }
    }
  ]
}

For multiple tools, add more objects to the tool_calls array:

{
  "content": "I'll analyze the project structure by listing files and reading the config.",
  "tool_calls": [
    {
      "id": "call_1",
      "type": "function",
      "function": {
        "name": "FILE_EXPLORER__list_directory",
        "arguments": "{\\"path\\": \\".\\", \\"recursive\\": false}"
      }
    },
    {
      "id": "call_2",
      "type": "function",
      "function": {
        "name": "FILE_EXPLORER__read_file",
        "arguments": "{\\"file_path\\": \\"config.py\\"}"
      }
    }
  ]
}

When responding without tools:

{
  "content": "Your response here in markdown format. You can include code blocks, explanations, etc."
}

TOOL NAMING FORMAT:
- Tools are named as: TOOL_NAME__method_name
- Example: FILE_EXPLORER__read_file, EDIT_FILE__replace_text
- See available tools list above for all available functions

TOOL USAGE GUIDELINES:
- Use tools to gather information before providing final answers
- Multiple tools can be called in one response (parallel execution)
- After tool results are returned, provide your final response with the information
- Always provide clear "content" explaining what you're doing

RESPONSE FORMAT RULES:
- Output ONLY valid JSON
- No reasoning or thinking tokens before/after the JSON
- No special tokens like <|channel|>, <|end|>, <|start|>
- Just pure JSON starting with { and ending with }
- Properly escape quotes in JSON strings (use \\")
- The "arguments" field must be a JSON string, not an object"""

# Google Custom Search API Configuration
# This is for the WebSearchTool to use the official Google API
GOOGLE_SEARCH_CONFIG = {
    "api_key": "",          # Populated from config.json at runtime
    "search_engine_id": ""    # Populated from config.json at runtime
}

# OpenRouter API Configuration
OPENROUTER_CONFIG = {
    "api_key": ""  # Populated from config.json at runtime
}

