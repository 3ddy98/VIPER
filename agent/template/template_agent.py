# agent/template/template_agent.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TemplateAgent:
    """
    A template for creating new agents that interact with the OpenRouter API.
    """

    def __init__(self, api_key=None, site_url=None, site_name=None):
        """
        Initializes the agent with the necessary credentials and configuration.

        Args:
            api_key (str, optional): The OpenRouter API key. Defaults to the OPENROUTER_API_KEY environment variable.
            site_url (str, optional): The URL of your site for rankings on openrouter.ai. Defaults to None.
            site_name (str, optional): The name of your site for rankings on openrouter.ai. Defaults to None.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")

        default_headers = {}
        if site_url:
            default_headers["HTTP-Referer"] = site_url
        if site_name:
            default_headers["X-Title"] = site_name
        
        self.client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=self.api_key,
            default_headers=default_headers if default_headers else None,
        )

    def chat(self, model, messages):
        """
        Sends a chat completion request to the specified model.

        Args:
            model (str): The model to use for the completion (e.g., 'openai/gpt-4o').
            messages (list): A list of message objects to send to the model.

        Returns:
            The chat completion object.
        """
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion

if __name__ == '__main__':
    # Example usage:
    try:
        # It's recommended to set your API key in a .env file
        # OPENROUTER_API_KEY="your-key-here"
        agent = TemplateAgent(site_url="http://localhost:8000", site_name="VIPER Test")

        completion = agent.chat(
            model='openai/gpt-3.5-turbo',
            messages=[
                {
                    'role': 'user',
                    'content': 'What is the meaning of life?',
                },
            ],
        )

        print(completion.choices[0].message.content)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
