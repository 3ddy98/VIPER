"""
Token Manager Module

This module handles token counting for conversations to ensure they
fit within the AI model's context window.
"""

import tiktoken
import re
from typing import List, Dict

class TokenManager:
    """
    A class to manage token counting for different models.
    """
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the TokenManager.
        
        Args:
            model_name: The name of the model to use for token encoding.
                        Defaults to "gpt-4" as a common reference.
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback for models not in tiktoken's registry
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a single string.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        return len(self.encoding.encode(text))

    def get_conversation_token_count(self, messages: List[Dict]) -> int:
        """
        Counts the total number of tokens in a list of message objects.

        This method approximates the token consumption as per OpenAI's guidelines,
        adding a small overhead for each message.

        Args:
            messages: A list of message dictionaries.

        Returns:
            The total token count for the conversation.
        """
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                # Strip special tokens before counting
                cleaned_value = re.sub(r'<\|[^|]+\|>', '', value)
                num_tokens += self.count_tokens(cleaned_value)
                if key == "name":  # If there's a name, the role is omitted
                    num_tokens -= 1  # Role is always required and always 1 token
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        return num_tokens
