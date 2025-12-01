"""
Conversation Manager Module

This module handles all conversation-related operations including:
- Creating and deleting conversations
- Managing conversation messages
- Searching and listing conversations
- Streaming responses from the AI model
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from rich.console import Console
from rich.live import Live
from rich.prompt import Confirm

from modules.config import CLIENT_CONFIG, CONVERSATIONS_FILE, SYSTEM_PROMPT, TOOL_CONFIG, UI_CONFIG
from modules.renderer import render_json_response, render_plan, render_plan_step_result, render_plan_summary, render_diff
from modules.tool_manager import ToolManager
from modules.token_manager import TokenManager
from modules.context_manager import ContextManager
from modules.paths import get_tools_dir
from modules.response_preprocessor import preprocess_custom_model_response

# Initialize Rich console for output
console = Console()


class ConversationManager:
    """
    Manages conversations with save/load/delete/search functionality.
    
    This class handles:
    - Conversation CRUD operations (Create, Read, Update, Delete)
    - Message storage and retrieval
    - AI response streaming
    - JSON file persistence
    """
    
    def __init__(self):
        """Initialize the conversation manager with OpenAI client and load existing conversations."""
        # Initialize OpenAI client with custom configuration
        self.client = OpenAI(
            base_url=CLIENT_CONFIG["base_url"],
            api_key=CLIENT_CONFIG["api_key"]
        )
        
        # Initialize Tool Manager if tools are enabled
        if TOOL_CONFIG["tools_enabled"]:
            self.tool_manager = ToolManager(tools_dir=str(get_tools_dir()))
            # Build system prompt with tool specifications
            self.system_prompt = self._build_system_prompt()
        else:
            self.tool_manager = None
            self.system_prompt = SYSTEM_PROMPT.replace("{TOOLS_SPEC}", "No tools available")
        
        # Load existing conversations from disk
        self.conversations = self.load_conversations()
        
        # Track current conversation (not used in new flow, kept for compatibility)
        self.current_conversation_id = None
        
        # Initialize Token and Context Managers
        self.token_manager = TokenManager(model_name=CLIENT_CONFIG["model"])
        self.context_manager = ContextManager()

    def get_current_token_count(self, conv_id: str) -> int:
        """
        Gets the current token count for a specific conversation.

        Args:
            conv_id: The ID of the conversation.

        Returns:
            The total token count for the conversation, or 0 if not found.
        """
        conversation = self.get_conversation(conv_id)
        if not conversation:
            return 0
        return self.token_manager.get_conversation_token_count(conversation["messages"])

    def load_conversations(self) -> Dict:
        """
        Load conversations from JSON file.
        
        Returns:
            Dict: Dictionary of conversations with IDs as keys
        """
        if os.path.exists(CONVERSATIONS_FILE):
            try:
                with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # Return empty dict if file is corrupted or unreadable
                return {}
        return {}
    
    def save_conversations(self):
        """
        Save conversations to JSON file, ensuring the data directory exists.
        """
        try:
            # Ensure the 'data' directory exists before saving.
            dir_name = os.path.dirname(CONVERSATIONS_FILE)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            
            with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"[red]Error saving conversations to {CONVERSATIONS_FILE}: {e}[/red]")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt with tool specifications in OpenRouter format.

        Returns:
            str: System prompt with tool specs injected
        """
        if not self.tool_manager:
            return SYSTEM_PROMPT.replace("{TOOLS_SPEC}", "No tools available")

        # Get tool specifications
        tool_specs = self.tool_manager.get_all_tool_specs()

        # Format tool specs for the prompt in OpenRouter function format
        tools_text = ""
        for spec in tool_specs:
            tool_name = spec['tool_name']

            # Add tool-level description (includes agents list for AGENTS tool)
            tools_text += f"\n=== {tool_name} ===\n"
            tools_text += f"{spec.get('description', '')}\n"

            for method in spec.get("methods", []):
                # Build function name
                function_name = f"{tool_name}__{method['name']}"

                # Build parameters schema
                properties = {}
                required_params = []

                for param_name, param_spec in method.get('parameters', {}).items():
                    properties[param_name] = {
                        "type": param_spec.get("type", "string"),
                        "description": param_spec.get("description", "")
                    }
                    if param_spec.get("required", False):
                        required_params.append(param_name)

                # Format as OpenRouter function
                tools_text += f"\nFunction: {function_name}\n"
                tools_text += f"Description: {method['description']}\n"
                tools_text += f"Parameters:\n"
                tools_text += json.dumps({
                    "type": "object",
                    "properties": properties,
                    "required": required_params
                }, indent=2)
                tools_text += "\n"
                if method.get('destruct_flag', False):
                    tools_text += "⚠️  DESTRUCTIVE - This operation modifies or deletes data\n"

        return SYSTEM_PROMPT.replace("{TOOLS_SPEC}", tools_text)
    
    def create_conversation(self, title: str) -> str:
        """
        Create a new conversation with an auto-incrementing ID.
        
        Args:
            title: The title for the new conversation
            
        Returns:
            str: The ID of the newly created conversation
        """
        # Generate next ID by finding the max existing ID and incrementing
        if self.conversations:
            existing_ids = [int(k) for k in self.conversations.keys() if k.isdigit()]
            next_id = max(existing_ids) + 1 if existing_ids else 1
        else:
            next_id = 1
        
        conv_id = str(next_id)
        
        # Create conversation with system prompt
        self.conversations[conv_id] = {
            "title": title,
            "created": datetime.now().isoformat(),
            "messages": [
                {"role": "system", "content": self.system_prompt}
            ]
        }
        
        self.save_conversations()
        return conv_id
    
    def delete_conversation(self, conv_id: str) -> bool:
        """
        Delete a conversation by ID.
        
        Args:
            conv_id: The ID of the conversation to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            self.save_conversations()
            return True
        return False
    
    def list_conversations(self) -> List[Dict]:
        """
        List all conversations with metadata.
        
        Returns:
            List of conversation metadata sorted by creation date
        """
        result = [
            {
                "id": conv_id,
                "title": data["title"],
                "created": data["created"],
                "messages": len(data["messages"]) - 1
            } for conv_id, data in self.conversations.items()
        ]
        return sorted(result, key=lambda x: x["created"], reverse=True)
    
    def search_conversations(self, query: str) -> List[Dict]:
        """
        Search conversations by title or message content.
        
        Args:
            query: The search query
            
        Returns:
            List of matching conversations
        """
        results = []
        query_lower = query.lower()
        
        for conv_id, data in self.conversations.items():
            if query_lower in data["title"].lower():
                results.append({
                    "id": conv_id, "title": data["title"],
                    "created": data["created"], "match": "title"
                })
            else:
                for msg in data["messages"]:
                    if msg["role"] != "system" and query_lower in msg["content"].lower():
                        results.append({
                            "id": conv_id, "title": data["title"],
                            "created": data["created"], "match": "content"
                        })
                        break
        return results
    
    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """
        Get a specific conversation by ID.
        
        Args:
            conv_id: The ID of the conversation
            
        Returns:
            The conversation data, or None if not found
        """
        return self.conversations.get(conv_id)
    
    def add_message(self, conv_id: str, role: str, content: str):
        """
        Add a message to a conversation.
        
        Args:
            conv_id: The ID of the conversation
            role: The role of the message sender
            content: The message content
        """
        if conv_id in self.conversations:
            self.conversations[conv_id]["messages"].append({"role": role, "content": content})
            self.save_conversations()
    
    def _execute_openrouter_tool_call(self, tool_call: Dict) -> Dict:
        """
        Execute an OpenRouter format tool call.

        Args:
            tool_call: Tool call in OpenRouter format with function.name and function.arguments

        Returns:
            Dict with execution results
        """
        if not self.tool_manager:
            return {"success": False, "error": "Tools are not enabled"}

        try:
            # Parse OpenRouter format
            function = tool_call.get("function", {})
            function_name = function.get("name", "")
            arguments_str = function.get("arguments", "{}")

            # Parse function name (format: TOOL_NAME__method_name)
            if "__" not in function_name:
                return {"success": False, "error": f"Invalid function name format: {function_name}"}

            tool_name, method = function_name.split("__", 1)

            # Parse arguments
            params = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str

            # Check if destructive
            method_spec = self.tool_manager._get_method_spec(tool_name, method)
            is_destructive = method_spec.get("destruct_flag", False) if method_spec else False

            needs_confirmation = (is_destructive and not TOOL_CONFIG["auto_execute_destructive"]) or \
                                 (not is_destructive and not TOOL_CONFIG["auto_execute_non_destructive"])

            if needs_confirmation:
                console.print(f"\n[yellow]Tool Call Request:[/yellow]")
                console.print(f"  Function: [cyan]{function_name}[/cyan]")
                console.print(f"  Parameters: {json.dumps(params, indent=2)}")
                if not Confirm.ask("\n[yellow]Execute this tool?[/yellow]", default=True):
                    return {"success": False, "error": "Tool execution cancelled by user"}
            else:
                console.print(f"\n[dim]Auto-executing: {function_name}[/dim]")

            # Execute the tool
            result = self.tool_manager.execute_tool_method(tool_name, method, **params)
            result["function_called"] = function_name
            return result

        except Exception as e:
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}

    def _execute_tool_with_confirmation(self, tool_call: Dict) -> Dict:
        """Execute a tool call, confirming if destructive. (DEPRECATED - use OpenRouter format)"""
        if not self.tool_manager:
            return {"success": False, "error": "Tools are not enabled"}

        tool_name = tool_call.get("tool_name")
        method = tool_call.get("method")
        params = tool_call.get("params", {})

        method_spec = self.tool_manager._get_method_spec(tool_name, method)
        is_destructive = method_spec.get("destruct_flag", False) if method_spec else False

        needs_confirmation = (is_destructive and not TOOL_CONFIG["auto_execute_destructive"]) or \
                             (not is_destructive and not TOOL_CONFIG["auto_execute_non_destructive"])

        if needs_confirmation:
            console.print(f"\n[yellow]Tool Call Request:[/yellow]")
            console.print(f"  Tool: [cyan]{tool_name}.{method}[/cyan]")
            console.print(f"  Parameters: {json.dumps(params, indent=2)}")
            if not Confirm.ask("\n[yellow]Execute this tool?[/yellow]", default=True):
                return {"success": False, "error": "Tool execution cancelled by user"}
        else:
            console.print(f"\n[dim]Auto-executing: {tool_name}.{method}[/dim]")

        return self.tool_manager.execute_tool_method(tool_name, method, **params)
    
    def _execute_plan(self, plan: Dict, conv_id: str, allow_reevaluation: bool = True) -> Dict:
        """
        Execute a multi-step plan with optional reevaluation after each step.

        Plan structure:
        {
            "name": "Plan Name",
            "steps": [
                {
                    "step_number": 1,
                    "description": "Step description",
                    "tool": "TOOL_NAME__method",
                    "arguments": "{\"param\": \"value\"}"
                }
            ]
        }

        Args:
            plan: The plan dictionary
            conv_id: Conversation ID for agent reevaluation
            allow_reevaluation: If True, agent can reevaluate plan after each step

        Returns:
            Dict with execution results
        """
        plan_name = plan.get("name", "Unnamed Plan")
        steps = plan.get("steps", [])

        render_plan(plan)
        if not Confirm.ask("[yellow]Execute this plan?[/yellow]", default=True):
            return {"success": False, "error": "Plan execution cancelled by user"}

        console.print("\n[bold cyan]EXECUTING PLAN[/bold cyan]\n")
        results = []
        successful_steps = 0
        current_plan = plan
        step_index = 0

        while step_index < len(steps):
            step = steps[step_index]
            step_num = step.get("step_number", step_index + 1)
            description = step.get("description", "Unknown step")
            tool_full_name = step.get("tool", "")
            arguments_str = step.get("arguments", "{}")

            # Parse tool name: "TOOL_NAME__method" -> tool_name, method
            if "__" in tool_full_name:
                tool_name, method = tool_full_name.split("__", 1)
            else:
                console.print(f"[red]Invalid tool format: {tool_full_name}[/red]")
                results.append({"step": step_num, "description": description, "success": False, "error": "Invalid tool format"})
                break

            # Parse arguments JSON
            try:
                params = json.loads(arguments_str)
            except json.JSONDecodeError:
                console.print(f"[red]Invalid JSON arguments for step {step_num}[/red]")
                results.append({"step": step_num, "description": description, "success": False, "error": "Invalid JSON arguments"})
                break

            # Execute the tool
            console.print(f"\n[cyan]Step {step_num}:[/cyan] {description}")
            result = self.tool_manager.execute_tool_method(tool_name, method, **params)
            result["description"] = description
            result["step_number"] = step_num

            render_plan_step_result(step_num, description, result.get("success", False), result)
            results.append({"step": step_num, **result})

            if result.get("success", False):
                successful_steps += 1

                # Allow agent to reevaluate plan after successful step
                if allow_reevaluation and step_index < len(steps) - 1:
                    reevaluation_result = self._reevaluate_plan(
                        conv_id, current_plan, step_num, result, results, steps[step_index + 1:]
                    )

                    if reevaluation_result.get("action") == "continue":
                        # Continue with existing plan
                        step_index += 1
                    elif reevaluation_result.get("action") == "update_plan":
                        # Agent provided updated plan
                        updated_plan = reevaluation_result.get("plan")
                        if updated_plan:
                            console.print("\n[yellow]⚠️  Agent updated the plan based on step results[/yellow]\n")
                            from modules.renderer import render_plan_update
                            render_plan_update(current_plan, updated_plan)

                            # Ask user to confirm updated plan
                            if Confirm.ask("[yellow]Continue with updated plan?[/yellow]", default=True):
                                current_plan = updated_plan
                                steps = updated_plan.get("steps", [])
                                plan_name = updated_plan.get("name", plan_name)
                                step_index += 1
                            else:
                                console.print("[yellow]Plan execution cancelled by user[/yellow]")
                                break
                        else:
                            step_index += 1
                    elif reevaluation_result.get("action") == "complete":
                        # Agent determined plan is complete
                        console.print("\n[green]✓ Agent determined plan goals achieved[/green]\n")
                        break
                    elif reevaluation_result.get("action") == "abort":
                        # Agent determined plan should be aborted
                        console.print("\n[red]✗ Agent aborted plan execution[/red]")
                        reason = reevaluation_result.get("reason", "Unknown reason")
                        console.print(f"[dim]Reason: {reason}[/dim]\n")
                        break
                    else:
                        step_index += 1
                else:
                    step_index += 1
            else:
                # Step failed - allow agent to reevaluate
                if allow_reevaluation:
                    console.print(f"\n[yellow]Step {step_num} failed. Asking agent to reevaluate...[/yellow]\n")
                    reevaluation_result = self._reevaluate_plan(
                        conv_id, current_plan, step_num, result, results, steps[step_index:]
                    )

                    if reevaluation_result.get("action") == "update_plan":
                        # Agent provided recovery plan
                        updated_plan = reevaluation_result.get("plan")
                        if updated_plan:
                            console.print("\n[yellow]⚠️  Agent proposed recovery plan[/yellow]\n")
                            from modules.renderer import render_plan_update
                            render_plan_update(current_plan, updated_plan)

                            if Confirm.ask("[yellow]Execute recovery plan?[/yellow]", default=True):
                                current_plan = updated_plan
                                steps = updated_plan.get("steps", [])
                                plan_name = updated_plan.get("name", plan_name)
                                step_index = 0  # Restart with recovery plan
                                results = []  # Reset results
                                successful_steps = 0
                            else:
                                console.print("[yellow]Recovery cancelled, stopping execution[/yellow]")
                                break
                        else:
                            break
                    else:
                        console.print(f"\n[red]Plan execution stopped at step {step_num} due to failure.[/red]\n")
                        break
                else:
                    console.print(f"\n[red]Plan execution stopped at step {step_num} due to failure.[/red]\n")
                    break

        render_plan_summary(plan_name, len(steps), successful_steps, results)
        return {
            "success": successful_steps == len(steps), "plan_name": plan_name,
            "total_steps": len(steps), "successful_steps": successful_steps, "results": results
        }

    def _reevaluate_plan(self, conv_id: str, current_plan: Dict, last_step_num: int,
                         last_result: Dict, all_results: List[Dict], remaining_steps: List[Dict]) -> Dict:
        """
        Ask the agent to reevaluate the plan based on step execution results.

        Args:
            conv_id: Conversation ID
            current_plan: The current plan being executed
            last_step_num: The step number that just completed
            last_result: Result of the last step execution
            all_results: All step results so far
            remaining_steps: Steps that haven't been executed yet

        Returns:
            Dict with:
            - action: "continue" | "update_plan" | "complete" | "abort"
            - plan: Updated plan (if action is "update_plan")
            - reason: Reason for action
        """
        # Prepare feedback for the agent
        feedback_msg = f"""PLAN REEVALUATION REQUEST

Current Plan: {current_plan.get('name', 'Unnamed Plan')}

Step {last_step_num} just completed:
- Description: {last_result.get('description', 'Unknown')}
- Status: {"SUCCESS" if last_result.get('success') else "FAILED"}
- Result: {json.dumps(last_result.get('result', {}), indent=2)}

All executed steps so far:
{json.dumps(all_results, indent=2)}

Remaining steps in current plan:
{json.dumps(remaining_steps, indent=2)}

Based on the step results, please decide:
1. CONTINUE - Continue with the existing plan as-is
2. UPDATE_PLAN - Provide an updated/modified plan
3. COMPLETE - The plan goals are already achieved, no more steps needed
4. ABORT - The plan should be aborted (e.g., insurmountable error)

Respond with your decision and reasoning using this format:

THOUGHT: <analyze the step results and determine next action>
DECISION: <CONTINUE | UPDATE_PLAN | COMPLETE | ABORT>
REASON: <brief explanation of your decision>

If DECISION is UPDATE_PLAN, also provide:
PLAN: <updated plan name>
STEP: <step description>
TOOL: <TOOL_NAME>__<method_name>
ARGS: <valid JSON object>
... (additional steps as needed)
"""

        # Add feedback to conversation
        self.add_message(conv_id, "system", feedback_msg)

        # Get agent's response
        console.print("\n[dim]Requesting plan reevaluation from agent...[/dim]")

        # Get response without streaming UI
        conversation = self.get_conversation(conv_id)
        managed_messages = self.context_manager.manage(conversation["messages"])

        response = self.client.chat.completions.create(
            model=CLIENT_CONFIG["model"],
            messages=managed_messages,
            stream=True
        )

        full_response = ""
        with console.status("[bold green]Agent thinking...") as status:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content

        # Parse the agent's decision
        decision_match = re.search(r'DECISION:\s*(CONTINUE|UPDATE_PLAN|COMPLETE|ABORT)', full_response, re.IGNORECASE)
        reason_match = re.search(r'REASON:\s*([^\n]+)', full_response, re.IGNORECASE)

        decision = decision_match.group(1).upper() if decision_match else "CONTINUE"
        reason = reason_match.group(1).strip() if reason_match else "No reason provided"

        console.print(f"[dim]Agent decision: {decision}[/dim]")
        console.print(f"[dim]Reason: {reason}[/dim]")

        result = {
            "action": decision.lower(),
            "reason": reason
        }

        # If agent provided an updated plan, parse it
        if decision == "UPDATE_PLAN":
            preprocessed = preprocess_custom_model_response(full_response)
            try:
                parsed = json.loads(preprocessed)
                if "plan" in parsed:
                    result["plan"] = parsed["plan"]
            except json.JSONDecodeError:
                console.print("[yellow]Failed to parse updated plan from agent[/yellow]")

        # Add agent's response to conversation
        self.add_message(conv_id, "assistant", full_response)

        return result
    
    def stream_response(self, conv_id: str, user_message: str, retry_count: int = 0, max_retries: int = 3) -> str:
        """
        Send a message and stream the AI response, managing context.

        Args:
            conv_id: Conversation ID
            user_message: User's message
            retry_count: Current retry attempt (for tool failures)
            max_retries: Maximum number of retries allowed for tool failures

        Returns:
            The assistant's response
        """
        conversation = self.get_conversation(conv_id)
        if not conversation:
            return ""

        self.add_message(conv_id, "user", user_message)

        # Manage context before sending to AI
        managed_messages = self.context_manager.manage(conversation["messages"])
        self.conversations[conv_id]["messages"] = managed_messages

        response = self.client.chat.completions.create(
            model=CLIENT_CONFIG["model"],
            messages=managed_messages,
            stream=True
        )

        full_response = ""
        console.print("\n[bold cyan]Assistant:[/bold cyan]")

        display_method = Live if UI_CONFIG["show_streaming"] else lambda: console.status("[bold green]Thinking...")

        with display_method() as live:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    if UI_CONFIG["show_streaming"]:
                        live.update(f"[dim]{full_response}[/dim]")

        console.print("\r" + " " * 80 + "\r", end="")

        # Preprocess the response to handle custom model formats
        preprocessed_response = preprocess_custom_model_response(full_response)

        if self.tool_manager and TOOL_CONFIG["tools_enabled"]:
            try:
                # Parse preprocessed response as JSON
                json_match = json.loads(preprocessed_response)

                # Check for PLAN format (multi-step execution)
                if "plan" in json_match and json_match["plan"]:
                    plan = json_match["plan"]

                    # Execute the plan with reevaluation enabled
                    plan_result = self._execute_plan(plan, conv_id, allow_reevaluation=True)

                    if plan_result.get("success"):
                        console.print("[green]Plan execution successful. Getting final response...[/green]\n")
                        # Add plan results to conversation
                        results_msg = f"Plan execution results:\n{json.dumps(plan_result, indent=2)}"
                        self.add_message(conv_id, "system", results_msg)
                        # Get final response from agent
                        return self.stream_response(conv_id, "Please provide your response based on the plan execution results.", retry_count=0)
                    else:
                        # Plan execution failed
                        console.print(f"[red]Plan execution failed: {plan_result.get('error', 'Unknown error')}[/red]\n")
                        # Fall through to render the original response

                # Check for OpenRouter format tool_calls
                elif "tool_calls" in json_match and json_match["tool_calls"]:
                    tool_calls = json_match["tool_calls"]

                    # Execute all tool calls
                    all_results = []
                    for tool_call in tool_calls:
                        result = self._execute_openrouter_tool_call(tool_call)
                        all_results.append(result)

                        # Render diff if this is an EDIT_FILE tool result
                        if result.get("success") and result.get("diff"):
                            # Extract file path from tool call if available
                            try:
                                function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                                file_path = function_args.get("file_path", "file")
                                dry_run = result.get("dry_run", False)
                                render_diff(result["diff"], file_path, dry_run)
                            except:
                                # Fallback if we can't extract file path
                                render_diff(result["diff"], "file", result.get("dry_run", False))

                    # Check if all successful
                    all_success = all(r.get("success") for r in all_results)

                    if all_success:
                        console.print("[green]Tool execution successful. Getting final response...[/green]\n")
                        # Add tool results to conversation
                        results_msg = f"Tool execution results:\n{json.dumps(all_results, indent=2)}"
                        self.add_message(conv_id, "system", results_msg)
                        # Recursively call stream_response to get the final response
                        # The recursive call will handle its own rendering
                        return self.stream_response(conv_id, "Please provide your response based on the tool execution results.", retry_count=0)
                    else:
                        # Tool execution failed - check if we can retry
                        failed = [r for r in all_results if not r.get("success")]
                        console.print(f"[red]Tool execution failed: {json.dumps(failed, indent=2)}[/red]\n")

                        if retry_count < max_retries:
                            console.print(f"[yellow]Retry {retry_count + 1}/{max_retries}: Asking agent to reevaluate...[/yellow]\n")

                            # Build error message for the agent
                            error_details = []
                            for i, result in enumerate(all_results):
                                if not result.get("success"):
                                    tool_name = result.get("function_called", f"Tool {i+1}")
                                    error_msg = result.get("error", "Unknown error")
                                    error_details.append(f"- {tool_name}: {error_msg}")

                            retry_message = (
                                f"TOOL EXECUTION FAILED:\n" +
                                "\n".join(error_details) +
                                f"\n\nPlease reevaluate your approach and try again with corrected parameters or a different method."
                            )

                            # Add error to conversation and retry
                            self.add_message(conv_id, "system", retry_message)
                            return self.stream_response(conv_id, "Retry with corrected approach", retry_count=retry_count + 1, max_retries=max_retries)
                        else:
                            console.print(f"[red]Max retries ({max_retries}) reached. Tool execution permanently failed.[/red]\n")
                            # Add final failure to conversation
                            failure_msg = f"Tool execution failed after {max_retries} retries:\n{json.dumps(failed, indent=2)}"
                            self.add_message(conv_id, "system", failure_msg)
                            # Fall through to render the original response

            except (json.JSONDecodeError, AttributeError):
                # Not a valid tool call, treat as regular message
                pass
            except Exception as e:
                console.print(f"[yellow]⚠ Could not parse tool call: {e}[/yellow]\n")

        # Render the preprocessed response for clean display
        render_json_response(preprocessed_response)
        # But save the original full response to conversation history
        self.add_message(conv_id, "assistant", preprocessed_response)
        return preprocessed_response

    def list_tool_details(self) -> List[Dict[str, str]]:
        """Retrieves a list of available tools with their names and descriptions."""
        if not self.tool_manager:
            return []
        return [
            {"name": spec.get("tool_name", "Unknown"), "description": spec.get("description", "N/A")}
            for spec in self.tool_manager.get_all_tool_specs()
        ]
