# modules/agent_manager.py
import os
import json
import shutil
from modules.renderer import render_agent_list, render_agent_details

class AgentManager:
    """
    Manages the creation, deletion, and modification of agents.
    """

    def __init__(self, agent_dir="agents"):
        self.agent_dir = agent_dir
        if not os.path.exists(self.agent_dir):
            os.makedirs(self.agent_dir)

    def create_agent(self, agent_name, agent_details):
        """
        Creates a new agent.

        Args:
            agent_name (str): The name of the agent.
            agent_details (dict): A dictionary of agent details.

        Returns:
            bool: True if the agent was created successfully, False otherwise.
        """
        agent_path = os.path.join(self.agent_dir, agent_name)
        if os.path.exists(agent_path):
            return False  # Agent already exists

        os.makedirs(agent_path)

        # Create the agent's JSON file
        json_path = os.path.join(agent_path, f"{agent_name}.json")
        with open(json_path, 'w') as f:
            json.dump(agent_details, f, indent=4)

        # Copy the template agent file
        template_path = "agent/template/template_agent.py"
        new_agent_path = os.path.join(agent_path, f"{agent_name}_agent.py")
        shutil.copy(template_path, new_agent_path)

        return True

    def list_agents(self):
        """
        Lists all available agents.

        Returns:
            list: A list of agent names.
        """
        agents = [d for d in os.listdir(self.agent_dir) if os.path.isdir(os.path.join(self.agent_dir, d))]
        return agents

    def get_agent_details(self, agent_name):
        """
        Gets the details of a specific agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            dict: The agent's details, or None if the agent doesn't exist.
        """
        json_path = os.path.join(self.agent_dir, agent_name, f"{agent_name}.json")
        if not os.path.exists(json_path):
            return None

        with open(json_path, 'r') as f:
            return json.load(f)

    def delete_agent(self, agent_name):
        """
        Deletes an agent.

        Args:
            agent_name (str): The name of the agent to delete.

        Returns:
            bool: True if the agent was deleted successfully, False otherwise.
        """
        agent_path = os.path.join(self.agent_dir, agent_name)
        if not os.path.exists(agent_path):
            return False

        shutil.rmtree(agent_path)
        return True

    def modify_agent(self, agent_name, new_details):
        """
        Modifies an agent's details.

        Args:
            agent_name (str): The name of the agent to modify.
            new_details (dict): The new details for the agent.

        Returns:
            bool: True if the agent was modified successfully, False otherwise.
        """
        json_path = os.path.join(self.agent_dir, agent_name, f"{agent_name}.json")
        if not os.path.exists(json_path):
            return False

        with open(json_path, 'w') as f:
            json.dump(new_details, f, indent=4)

        return True
