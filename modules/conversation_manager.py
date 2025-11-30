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
from modules.renderer import render_json_response, render_plan, render_plan_step_result, render_plan_summary
from modules.tool_manager import ToolManager
from modules.token_manager import TokenManager
from modules.context_manager import ContextManager

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
            self.tool_manager = ToolManager()
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
        Build the system prompt with tool specifications.
        
        Returns:
            str: System prompt with tool specs injected
        """
        if not self.tool_manager:
            return SYSTEM_PROMPT.replace("{TOOLS_SPEC}", "No tools available")
        
        # Get tool specifications
        tool_specs = self.tool_manager.get_all_tool_specs()
        
        # Format tool specs for the prompt
        tools_text = ""
        for spec in tool_specs:
            tools_text += f"\n\nTool: {spec['tool_name']}\n"
            tools_text += f"Description: {spec['description']}\n"
            tools_text += f"Methods:\n"
            
            for method in spec.get("methods", []):
                tools_text += f"  - {method['name']}: {method['description']}\n"
                tools_text += f"    Parameters: {json.dumps(method.get('parameters', {}), indent=6)}\n"
                tools_text += f"    Destructive: {method.get('destruct_flag', False)}\n"
        
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
    
    def _execute_tool_with_confirmation(self, tool_call: Dict) -> Dict:
        """Execute a tool call, confirming if destructive."""
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
    
    def _execute_plan(self, plan: Dict) -> Dict:
        """Execute a multi-step plan."""
        plan_name = plan.get("name", "Unnamed Plan")
        steps = plan.get("steps", [])
        
        render_plan(plan)
        if not Confirm.ask("[yellow]Execute this plan?[/yellow]", default=True):
            return {"success": False, "error": "Plan execution cancelled by user"}
        
        console.print("\n[bold cyan]EXECUTING PLAN[/bold cyan]\n")
        results = []
        successful_steps = 0
        
        for idx, step in enumerate(steps, 1):
            result = self._execute_tool_with_confirmation(step.get("tool", {}))
            render_plan_step_result(idx, step.get("name"), result.get("success", False), result)
            results.append({"step": idx, "name": step.get("name"), **result})
            
            if result.get("success", False):
                successful_steps += 1
            else:
                console.print(f"\n[red]Plan execution stopped at step {idx} due to failure.[/red]\n")
                break
        
        render_plan_summary(plan_name, len(steps), successful_steps, results)
        return {
            "success": successful_steps == len(steps), "plan_name": plan_name,
            "total_steps": len(steps), "successful_steps": successful_steps, "results": results
        }
    
    def stream_response(self, conv_id: str, user_message: str) -> str:
        """
        Send a message and stream the AI response, managing context.
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
        
        if self.tool_manager and TOOL_CONFIG["tools_enabled"]:
            try:
                json_match = json.loads(re.search(r'\{.*\}', re.sub(r'<\|[^|]+\|>', '', full_response), re.DOTALL).group(0))
                
                handler = None
                if "plan" in json_match and json_match["plan"]:
                    handler = lambda: self._execute_plan(json_match["plan"])
                elif "tool" in json_match and json_match["tool"]:
                    handler = lambda: self._execute_tool_with_confirmation(json_match["tool"])

                if handler:
                    result = handler()
                    if result.get("success"):
                        console.print("[green]Operation successful. Getting final response...[/green]\n")
                        result_msg = f"Operation result: {json.dumps(result, indent=2)}"
                        self.add_message(conv_id, "system", result_msg)
                        return self.stream_response(conv_id, "Please provide your response based on the operation results.")
                    else:
                        console.print(f"[red]Operation failed: {result.get('error')}[/red]\n")

            except (json.JSONDecodeError, AttributeError):
                # Not a valid tool/plan call, treat as regular message
                pass
            except Exception as e:
                console.print(f"[yellow]⚠ Could not parse tool/plan call: {e}[/yellow]\n")

        render_json_response(full_response)
        self.add_message(conv_id, "assistant", full_response)
        return full_response

    def list_tool_details(self) -> List[Dict[str, str]]:
        """Retrieves a list of available tools with their names and descriptions."""
        if not self.tool_manager:
            return []
        return [
            {"name": spec.get("tool_name", "Unknown"), "description": spec.get("description", "N/A")}
            for spec in self.tool_manager.get_all_tool_specs()
        ]
