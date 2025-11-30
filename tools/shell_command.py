"""
General Shell Command Tool

This tool allows the AI agent to execute arbitrary shell commands.
This is an extremely powerful and DANGEROUS tool. It should be used
with maximum caution and user supervision.
"""

import subprocess
import shlex
from typing import Dict, Any

class ShellCommandTool:
    """
    A tool for executing general-purpose shell commands.
    
    SECURITY WARNING: This tool allows the execution of any shell command,
    which can be used to modify the file system, access network resources,
    or cause other significant side effects. All executions should be
    carefully reviewed by the user.
    """
    
    def __init__(self):
        """
        Initialize the Shell Command tool.
        """
        self.tool_name = "SHELL_COMMAND"

    def execute(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Executes a shell command.

        Args:
            command: The command string to execute.
            timeout: The timeout in seconds for the command.

        Returns:
            A dictionary containing the stdout, stderr, and return code.
        """
        try:
            # For security, it's better to split the command into a list
            # to avoid shell injection if shell=False. However, for a "general"
            # shell tool, features like pipes (|) and redirection (>) are
            # often expected, which requires shell=True.
            # We will proceed with shell=True but acknowledge the risk.
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out.",
                "stdout": "",
                "stderr": "TimeoutExpired",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        """
        return {
            "tool_name": self.tool_name,
            "description": "Executes arbitrary shell commands. DANGEROUS: This tool can modify files, access the internet, and cause unintended side effects. All commands should be reviewed carefully.",
            "methods": [
                {
                    "name": "execute",
                    "description": "Executes a single shell command and returns its output.",
                    "parameters": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'ls -l', 'pip install <package>').",
                            "required": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "The maximum number of seconds to allow the command to run.",
                            "required": False,
                            "default": 60
                        }
                    },
                    "returns": "A dictionary containing the command's stdout, stderr, and return code.",
                    "destruct_flag": True  # <-- Always destructive
                }
            ]
        }
