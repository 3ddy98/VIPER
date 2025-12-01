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
# This prompt forces a consistent, parseable output format
SYSTEM_PROMPT = """You are a coding assistant with access to tools.

# Available Tools

{TOOLS_SPEC}

# OUTPUT FORMAT RULES

You MUST follow these strict output format rules. Your response will be parsed programmatically.

## Rule 1: Start Every Response with THOUGHT

EVERY response must begin with:
THOUGHT: <your internal reasoning>

The THOUGHT section explains your reasoning process. It is mandatory.

## Rule 2: Choose One Output Type

After THOUGHT, you must choose EXACTLY ONE of the following:

### Option A: TOOL CALL(S)
Use when you need to execute tools.

Format:
THOUGHT: <reasoning>
TOOL: <TOOL_NAME>__<method_name>
ARGS: <valid JSON object>

Rules for tool calls:
- TOOL line contains the exact tool and method name from the Available Tools list
- ARGS line contains a single-line valid JSON object with all required parameters
- For multiple tools, repeat TOOL/ARGS pairs (no additional THOUGHT lines)
- Tool names are case-sensitive and must match exactly
- JSON must be valid and properly escaped

### Option B: PLAN
Use when you need to create a multi-step execution plan.

Format:
THOUGHT: <reasoning>
PLAN: <plan_name>
STEP: <step_description>
TOOL: <TOOL_NAME>__<method_name>
ARGS: <valid JSON object>
STEP: <step_description>
TOOL: <TOOL_NAME>__<method_name>
ARGS: <valid JSON object>

Rules for plans:
- PLAN line contains a brief plan name
- Each STEP line describes what the step accomplishes
- Each STEP must be followed by TOOL and ARGS
- Minimum 2 steps required
- Steps execute sequentially
- After each step executes, you will be asked to reevaluate the plan based on results
- You can continue with the existing plan, update it, mark it complete, or abort it
- If a step fails, you can provide a recovery plan

### Option C: RESPONSE
Use when answering directly without tools.

Format:
THOUGHT: <reasoning>
RESPONSE: <your answer to the user>

Rules for responses:
- RESPONSE contains your complete answer to the user
- May include markdown formatting
- May include code blocks
- May span multiple lines
- Must provide complete information

## Rule 3: No Extra Text

DO NOT include:
- Text before THOUGHT
- Text between THOUGHT and TOOL/PLAN/RESPONSE
- Explanatory comments outside the format
- Conversational preambles or conclusions
- Any text after the final ARGS or RESPONSE

## Rule 4: After Tool Execution

When tools finish executing, you will receive:
"Tool execution results: <JSON results>"

You must then respond with:
THOUGHT: <analysis of results>
RESPONSE: <final answer to user>

## Rule 5: Parameter Accuracy

- All required parameters must be provided
- Parameter names must match exactly
- Parameter values must have correct types
- File paths must be relative to current working directory unless absolute
- Boolean values must be lowercase: true, false
- Null values: null

## Rule 6: Tool Selection

- Use the most specific tool available
- Do not attempt operations without appropriate tools
- If uncertain about parameters, explain limitations in RESPONSE
- Check Available Tools list for exact names and methods

## Rule 7: Plan Reevaluation (Special Format)

When you create a PLAN, after each step executes, you will receive a "PLAN REEVALUATION REQUEST"
with the step results. You must respond with a DECISION:

Format:
THOUGHT: <analyze the step results and determine next action>
DECISION: <CONTINUE | UPDATE_PLAN | COMPLETE | ABORT>
REASON: <brief explanation of your decision>

If DECISION is UPDATE_PLAN, also provide:
PLAN: <updated plan name>
STEP: <step description>
TOOL: <TOOL_NAME>__<method_name>
ARGS: <valid JSON object>
... (additional steps as needed)

Decision options:
- CONTINUE: Existing plan is still valid, continue with remaining steps
- UPDATE_PLAN: Modify the plan based on what you learned (add/remove/change steps)
- COMPLETE: Plan goals already achieved, no more steps needed
- ABORT: Unrecoverable error, stop execution

## CRITICAL

Your response MUST be parseable. Invalid format will cause errors.
ALWAYS start with THOUGHT.
ALWAYS choose exactly ONE: TOOL, PLAN, or RESPONSE.
NEVER mix formats.
NEVER add extra text outside the structure."""

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

