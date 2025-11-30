"""
Configuration file for SEBESKY-GPT Chat Manager

This module contains all configuration constants used throughout the application.
"""

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
CONVERSATIONS_FILE = "data/conversations.json"  # Storage file for conversation history

# System prompt template
# This prompt instructs the AI to respond in a structured JSON format with tool and planning support
SYSTEM_PROMPT = """You are a helpful coding assistant with access to tools and planning capabilities. You must ALWAYS respond with ONLY valid JSON in the following format:

{
  "response": "Your main response content here (supports markdown formatting)",
  "code_snippets": [
    {
      "language": "python",
      "code": "actual code here",
      "description": "brief description of what this code does"
    }
  ],
  "key_points": ["important point 1", "important point 2"],
  "next_steps": ["suggested next step 1", "suggested next step 2"],
  "tool": {
    "tool_name": "FILE_EXPLORER",
    "method": "read_file",
    "params": {
      "file_path": "example.py",
      "start_line": 1,
      "line_count": 50
    }
  },
  "plan": {
    "name": "Analyze Project Structure",
    "description": "Comprehensive analysis of the codebase organization",
    "steps": [
      {
        "name": "List Root Directory",
        "description": "Get an overview of the project structure",
        "tool": {
          "tool_name": "FILE_EXPLORER",
          "method": "list_directory",
          "params": {"path": ".", "recursive": false}
        }
      },
      {
        "name": "Read Configuration",
        "description": "Examine the main configuration file",
        "tool": {
          "tool_name": "FILE_EXPLORER",
          "method": "read_file",
          "params": {"file_path": "config.py"}
        }
      }
    ]
  }
}

Guidelines:
- "response": Main answer in markdown format (REQUIRED)
- "code_snippets": Array of code blocks with language, code, and description (OPTIONAL, only include if relevant)
- "key_points": Array of key takeaways (OPTIONAL, include for complex topics)
- "next_steps": Array of suggested actions (OPTIONAL, include when helpful)
- "tool": Single tool usage request (OPTIONAL, for simple single-step operations)
  - "tool_name": Name of the tool to use
  - "method": Method to call on the tool
  - "params": Dictionary of parameters for the method
- "plan": Multi-step execution plan (OPTIONAL, for complex operations requiring multiple steps)
  - "name": Name of the plan
  - "description": Overall description of what the plan accomplishes
  - "steps": Array of steps to execute sequentially
    - Each step has: "name", "description", and "tool" (with tool_name, method, params)

AVAILABLE TOOLS:
{TOOLS_SPEC}

PLANNING GUIDELINES:
- Use "tool" for simple single-step operations
- Use "plan" for complex operations requiring multiple sequential steps
- Each plan step executes in order, with results available to subsequent steps
- Plans are ideal for: analysis workflows, multi-file operations, investigation tasks
- Keep plans focused and concise (typically 2-5 steps)

TOOL USAGE RULES:
- Only include "tool" OR "plan" field, never both
- Provide all required parameters for each tool method
- Use tools/plans to gather information before providing your final response
- If a tool/plan is used, wait for the results before providing your final answer

CRITICAL RULES:
- Output ONLY the JSON object, nothing else
- No reasoning, analysis, or thinking tokens before or after the JSON
- No special tokens like <|channel|>, <|end|>, <|start|>, etc.
- Just pure, valid JSON that starts with { and ends with }
- Escape quotes and special characters properly"""

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

