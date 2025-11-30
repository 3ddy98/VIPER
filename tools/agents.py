"""
Agents Tool

This tool allows the primary AI agent to delegate tasks to specialized agents.
Each agent has its own model configuration and can use tools via OpenRouter's tool calling.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from openai import OpenAI
from rich.console import Console

console = Console()

# Import config to access OpenRouter API key loaded from .env
from modules.config import OPENROUTER_CONFIG


class AgentsTool:
    """
    A tool that enables the primary agent to invoke other specialized agents with tool calling support.
    """

    def __init__(self, agent_dir: str = "agents", tool_manager=None):
        """
        Initialize the Agents tool.

        Args:
            agent_dir: Directory where agent configurations are stored
            tool_manager: Optional ToolManager instance for executing tools
        """
        self.tool_name = "AGENTS"
        self.agent_dir = agent_dir
        self.tool_manager = tool_manager
        self.available_agents = self._load_available_agents()
        self._model_capabilities_cache = {}  # Cache model capabilities

    def _load_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all available agents from the agents directory.

        Returns:
            Dictionary mapping agent names to their configurations
        """
        agents = {}

        if not os.path.exists(self.agent_dir):
            return agents

        # Scan agent directories
        for agent_name in os.listdir(self.agent_dir):
            agent_path = os.path.join(self.agent_dir, agent_name)

            if not os.path.isdir(agent_path):
                continue

            # Load agent configuration
            config_path = os.path.join(agent_path, f"{agent_name}.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        agents[agent_name] = config
                except Exception as e:
                    # Skip agents with invalid configurations
                    continue

        return agents

    def _check_model_supports_tools(self, model_id: str) -> bool:
        """
        Query OpenRouter API to check if a model supports tool calling.

        Args:
            model_id: The OpenRouter model ID (e.g., "qwen/qwen2.5-vl-32b-instruct")

        Returns:
            True if the model supports tools, False otherwise
        """
        # Check cache first
        if model_id in self._model_capabilities_cache:
            return self._model_capabilities_cache[model_id]

        try:
            # Query OpenRouter models API
            response = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
            response.raise_for_status()
            models_data = response.json()

            # Find the specific model
            model_info = next(
                (m for m in models_data.get("data", []) if m.get("id") == model_id),
                None
            )

            if model_info:
                # Check if "tools" and "tool_choice" are in supported_parameters
                supported_params = model_info.get("supported_parameters", [])
                supports_tools = "tools" in supported_params and "tool_choice" in supported_params

                # Cache the result
                self._model_capabilities_cache[model_id] = supports_tools
                return supports_tools
            else:
                console.print(f"[yellow]Warning: Model {model_id} not found in OpenRouter API[/yellow]")
                # Default to False if model not found
                self._model_capabilities_cache[model_id] = False
                return False

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to check model capabilities: {str(e)}[/yellow]")
            # Default to False on error
            return False

    def _convert_viper_tools_to_openrouter_schema(self) -> List[Dict[str, Any]]:
        """
        Convert VIPER tool specs to OpenRouter function calling schema for the tools parameter.

        Note: VIPER now uses OpenRouter format natively, but we still need to build
        the tools parameter array for the OpenRouter API call.

        Returns:
            List of tool schemas in OpenRouter format
        """
        if not self.tool_manager:
            return []

        openrouter_tools = []
        tool_specs = self.tool_manager.get_all_tool_specs()

        for spec in tool_specs:
            tool_name = spec.get("tool_name")

            # Skip the AGENTS tool to avoid recursion
            if tool_name == "AGENTS":
                continue

            for method in spec.get("methods", []):
                # Build parameters schema
                properties = {}
                required_params = []

                for param_name, param_spec in method.get("parameters", {}).items():
                    properties[param_name] = {
                        "type": param_spec.get("type", "string"),
                        "description": param_spec.get("description", "")
                    }

                    # Handle array types
                    if param_spec.get("type") == "array":
                        properties[param_name]["items"] = {"type": "string"}

                    if param_spec.get("required", False):
                        required_params.append(param_name)

                # Create function schema
                function_schema = {
                    "type": "function",
                    "function": {
                        "name": f"{tool_name}__{method['name']}",
                        "description": f"{spec.get('description', '')} - {method.get('description', '')}",
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required_params
                        }
                    }
                }

                openrouter_tools.append(function_schema)

        return openrouter_tools

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """
        Execute a tool call from the agent.

        Args:
            tool_call: The tool call object from OpenRouter

        Returns:
            JSON string with the tool execution result
        """
        if not self.tool_manager:
            return json.dumps({"success": False, "error": "Tool manager not available"})

        try:
            # Parse function name (format: TOOL_NAME__method_name)
            function_name = tool_call.function.name
            if "__" not in function_name:
                return json.dumps({"success": False, "error": f"Invalid function name format: {function_name}"})

            tool_name, method_name = function_name.split("__", 1)

            # Parse arguments
            arguments = json.loads(tool_call.function.arguments)

            # Execute the tool
            console.print(f"[dim]Agent executing: {tool_name}.{method_name}[/dim]")
            result = self.tool_manager.execute_tool_method(tool_name, method_name, **arguments)

            return json.dumps(result)

        except Exception as e:
            return json.dumps({"success": False, "error": f"Tool execution failed: {str(e)}"})

    def invoke_agent(
        self,
        agent_name: str,
        prompt: str,
        enable_tools: bool = True,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_tool_rounds: int = 10
    ) -> Dict[str, Any]:
        """
        Invoke a specialized agent with a given prompt.

        Args:
            agent_name: The name of the agent to invoke
            prompt: The prompt/task to send to the agent
            enable_tools: Whether to enable tool calling for this agent
            conversation_history: Optional list of previous messages for context
            temperature: Optional temperature parameter (0.0 to 2.0)
            max_tokens: Optional maximum tokens for the response
            max_tool_rounds: Maximum number of tool calling rounds to prevent infinite loops

        Returns:
            A dictionary containing the agent's response or an error message
        """
        try:
            # Validate agent exists
            if agent_name not in self.available_agents:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' not found. Available agents: {', '.join(self.available_agents.keys())}"
                }

            agent_config = self.available_agents[agent_name]

            # Get API key from OPENROUTER_CONFIG (loaded from .env)
            # Agent configs no longer store API keys for security
            api_key = OPENROUTER_CONFIG.get("api_key")
            if not api_key:
                return {
                    "success": False,
                    "error": "No OpenRouter API key found. Add OPEN_ROUTER_API_KEY to .env file."
                }

            # Set up headers for OpenRouter
            default_headers = {}
            if agent_config.get("site_url"):
                default_headers["HTTP-Referer"] = agent_config["site_url"]
            if agent_config.get("site_name"):
                default_headers["X-Title"] = agent_config["site_name"]

            # Initialize OpenRouter client
            client = OpenAI(
                base_url='https://openrouter.ai/api/v1',
                api_key=api_key,
                default_headers=default_headers if default_headers else None,
            )

            # Build messages list
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add the current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Check if model supports tools
            model_id = agent_config.get("model", "openai/gpt-3.5-turbo")
            model_supports_tools = self._check_model_supports_tools(model_id)

            # Get tools schema if enabled and model supports tools
            tools = None
            if enable_tools and self.tool_manager and model_supports_tools:
                tools = self._convert_viper_tools_to_openrouter_schema()
                if not tools:
                    console.print("[dim]No tools available for agent[/dim]")
            elif enable_tools and not model_supports_tools:
                console.print(f"[dim]Model {model_id} does not support tool calling. Proceeding without tools.[/dim]")

            # Prepare completion parameters
            completion_params = {
                "model": model_id,
                "messages": messages
            }

            # Add tools if available and model supports them
            if tools:
                completion_params["tools"] = tools

            # Add optional parameters
            if temperature is not None:
                completion_params["temperature"] = temperature
            if max_tokens is not None:
                completion_params["max_tokens"] = max_tokens

            # Tool calling loop
            tool_call_count = 0
            total_tokens_used = {"prompt": 0, "completion": 0, "total": 0}

            while tool_call_count < max_tool_rounds:
                # Make the API call
                completion = client.chat.completions.create(**completion_params)

                # Track token usage
                if hasattr(completion, 'usage'):
                    total_tokens_used["prompt"] += completion.usage.prompt_tokens
                    total_tokens_used["completion"] += completion.usage.completion_tokens
                    total_tokens_used["total"] += completion.usage.total_tokens

                # Check if the model wants to call tools
                finish_reason = completion.choices[0].finish_reason
                message = completion.choices[0].message

                if finish_reason == "tool_calls" and hasattr(message, 'tool_calls') and message.tool_calls:
                    # Add assistant's message to conversation
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            } for tc in message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        result = self._execute_tool_call(tool_call)

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })

                    # Update completion params for next round
                    completion_params["messages"] = messages
                    tool_call_count += 1

                else:
                    # No more tool calls, return final response
                    response_content = message.content or ""

                    return {
                        "success": True,
                        "agent_name": agent_name,
                        "response": response_content,
                        "model_used": agent_config.get("model"),
                        "tool_calls_made": tool_call_count,
                        "usage": total_tokens_used,
                        "conversation": messages
                    }

            # Max rounds reached
            return {
                "success": False,
                "error": f"Maximum tool calling rounds ({max_tool_rounds}) reached. Agent may be in an infinite loop.",
                "tool_calls_made": tool_call_count,
                "usage": total_tokens_used
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to invoke agent '{agent_name}': {str(e)}"
            }

    def list_agents(self) -> Dict[str, Any]:
        """
        List all available agents and their descriptions.

        Returns:
            A dictionary containing information about all available agents
        """
        try:
            agents_info = {}

            for agent_name, config in self.available_agents.items():
                agents_info[agent_name] = {
                    "description": config.get("description", "No description available"),
                    "model": config.get("model", "Unknown")
                }

            return {
                "success": True,
                "agents": agents_info,
                "count": len(agents_info)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list agents: {str(e)}"
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.

        Returns:
            A dictionary containing the complete tool specification
        """
        # Build the agents list for the description
        agents_description = ""
        if self.available_agents:
            agents_list = []
            for agent_name, config in self.available_agents.items():
                desc = config.get("description", "No description")
                model = config.get("model", "Unknown model")
                agents_list.append(f"  - {agent_name}: {desc} (using {model})")
            agents_description = "\n\nAvailable agents:\n" + "\n".join(agents_list)
        else:
            agents_description = "\n\nNo agents currently available."

        # Build tools available message
        tools_message = ""
        if self.tool_manager:
            tool_count = len(self.tool_manager.get_all_tool_specs())
            tools_message = f" Agents can use {tool_count} available tools."

        return {
            "tool_name": self.tool_name,
            "description": f"Invoke specialized AI agents to handle specific tasks. Each agent has its own model and expertise.{tools_message}{agents_description}",
            "version": "1.0.0",
            "methods": [
                {
                    "name": "invoke_agent",
                    "description": "Invoke a specialized agent to handle a specific task. The agent can use available tools to complete the task.",
                    "parameters": {
                        "agent_name": {
                            "type": "string",
                            "description": f"The name of the agent to invoke. Available: {', '.join(self.available_agents.keys()) if self.available_agents else 'None'}",
                            "required": True
                        },
                        "prompt": {
                            "type": "string",
                            "description": "The task or question to send to the agent. Be clear and specific about what you want the agent to do.",
                            "required": True
                        },
                        "enable_tools": {
                            "type": "boolean",
                            "description": "Whether to enable tool calling for this agent. Default is True.",
                            "required": False,
                            "default": True
                        },
                        "conversation_history": {
                            "type": "array",
                            "description": "Optional conversation history to provide context. Each item should be a dict with 'role' and 'content' keys.",
                            "required": False
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Optional temperature parameter for response creativity (0.0 = deterministic, 2.0 = very creative). Defaults to model default.",
                            "required": False
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Optional maximum number of tokens in the agent's response.",
                            "required": False
                        }
                    },
                    "returns": "A dictionary containing the agent's response, tools used, model used, and token usage information.",
                    "destruct_flag": False
                },
                {
                    "name": "list_agents",
                    "description": "List all available agents, their descriptions, and configured models.",
                    "parameters": {},
                    "returns": "A dictionary containing information about all available agents.",
                    "destruct_flag": False
                }
            ]
        }
