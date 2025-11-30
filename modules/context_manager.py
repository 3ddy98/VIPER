"""
Context Manager Module

This module is responsible for managing the conversation context to keep it
within the AI model's token limit. It uses a summarization strategy to
compress the middle of a long conversation while preserving the system
prompt and recent messages.
"""

import json
from typing import List, Dict
from openai import OpenAI
from rich.console import Console

from modules.config import CLIENT_CONFIG, CONTEXT_CONFIG
from modules.token_manager import TokenManager

# Initialize console for printing messages
console = Console()


class ContextManager:
    """
    Manages the conversation context by summarizing older messages
    to stay within the token limit.
    """

    def __init__(self):
        """
        Initialize the ContextManager with settings from the main config.
        """
        self.client = OpenAI(
            base_url=CLIENT_CONFIG["base_url"],
            api_key=CLIENT_CONFIG["api_key"]
        )
        self.model = CLIENT_CONFIG["model"]
        self.token_manager = TokenManager(model_name=self.model)
        self.token_window = CLIENT_CONFIG["token_window_size"]
        self.compression_threshold = CONTEXT_CONFIG["compression_threshold"]
        
        # Number of recent messages to preserve during compression
        self.recent_messages_to_keep = CONTEXT_CONFIG.get("historical_messages_to_load", 10)

    def manage(self, messages: List[Dict]) -> List[Dict]:
        """
        Manages the context of a conversation. If the token count exceeds the
        compression threshold, it compresses the context.

        Args:
            messages: The list of message dictionaries from a conversation.

        Returns:
            The (potentially compressed) list of messages.
        """
        token_count = self.token_manager.get_conversation_token_count(messages)
        
        # Check if the current token count is over the threshold
        if token_count > (self.token_window * self.compression_threshold):
            console.print(f"\n[yellow]Context is large ({token_count} tokens). Compressing...[/yellow]")
            return self._compress_context(messages)
        
        # If not over threshold, return messages as is
        return messages

    def _compress_context(self, messages: List[Dict]) -> List[Dict]:
        """
        Compresses the conversation history by summarizing the middle part.

        This method preserves the first message (system prompt) and the most
        recent messages, while summarizing the block of messages in between.

        Args:
            messages: The full list of message dictionaries.

        Returns:
            A compressed list of messages.
        """
        # Ensure there are enough messages to compress
        # (system prompt + messages to summarize + recent messages)
        if len(messages) < self.recent_messages_to_keep + 2:
            return messages

        # 1. Preserve the system prompt
        system_prompt = messages[0]
        
        # 2. Preserve the most recent messages
        recent_messages = messages[-self.recent_messages_to_keep:]
        
        # 3. Identify the messages in the middle to be summarized
        messages_to_summarize = messages[1:-self.recent_messages_to_keep]

        if not messages_to_summarize:
            return messages  # Should not happen with the check above, but for safety

        # 4. Create a prompt to ask the AI to summarize the conversation
        summary_prompt_text = (
            "Please summarize the following conversation exchange concisely. "
            "This summary will be used as context for a continuing conversation, "
            "so it must preserve key facts, user requests, and AI decisions. "
            "The conversation is between a 'user' and an 'assistant'.\n\n"
            f"CONVERSATION:\n{json.dumps(messages_to_summarize, indent=2)}"
        )

        try:
            # 5. Call the AI to perform the summarization
            with console.status("[dim]Summarizing older context to save tokens...[/dim]"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": summary_prompt_text}],
                    temperature=0.2  # Lower temperature for more factual summary
                )
                summary = response.choices[0].message.content
        
        except Exception as e:
            console.print(f"[red]✗ Failed to summarize context: {e}[/red]")
            # Fallback: if summarization fails, simply truncate the oldest messages
            # to ensure the conversation can continue.
            return [system_prompt] + messages[-(self.recent_messages_to_keep + 4):]

        # 6. Create the new compressed message list
        summarized_message = {
            "role": "system",
            "content": f"Summary of earlier conversation: {summary}"
        }
        
        new_messages = [system_prompt, summarized_message] + recent_messages
        
        new_token_count = self.token_manager.get_conversation_token_count(new_messages)
        console.print(f"[green]✓ Context compressed. Tokens reduced to ~{new_token_count}.[/green]\n")
        
        return new_messages
