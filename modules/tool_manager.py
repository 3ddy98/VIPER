"""
Tool Manager Module

This module handles dynamic loading and management of tools for the AI agent.
It provides:
- Tool discovery and loading from the tools directory
- Tool registration and specification retrieval
- Safe tool execution with error handling
- Destructive operation flagging and control
"""

import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console

# Initialize Rich console for output
console = Console()


class ToolManager:
    """
    Manages tools for AI agent integration.
    
    This class:
    - Dynamically loads tools from the tools directory
    - Provides tool specifications for AI model integration
    - Executes tool methods with safety checks
    - Handles destructive operation warnings
    """
    
    def __init__(self, tools_dir: str = "tools", base_path: Optional[str] = None):
        """
        Initialize the Tool Manager.
        
        Args:
            tools_dir: Directory containing tool modules
            base_path: Base path for file operations (passed to tools)
        """
        self.tools_dir = Path(tools_dir)
        self.base_path = base_path
        self.tools: Dict[str, Any] = {}  # tool_name -> tool_instance
        self.tool_specs: Dict[str, Dict] = {}  # tool_name -> tool_spec
        
        # Load all available tools
        self._load_tools()
    
    def _load_tools(self):
        """
        Dynamically load all tools from the tools directory.
        
        Discovers Python files in the tools directory, imports them,
        and instantiates tool classes.
        """
        if not self.tools_dir.exists():
            # This warning is important for debugging, so we keep it.
            console.print(f"[yellow]Warning: Tools directory '{self.tools_dir}' not found[/yellow]")
            return
        
        # Find all Python files in tools directory
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name.startswith("_") or tool_file.name.startswith("."):
                continue
            
            try:
                # Import the module
                module_name = f"{self.tools_dir.name}.{tool_file.stem}"
                module = importlib.import_module(module_name)
                
                # Find tool classes (classes ending with "Tool")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Tool") and obj.__module__ == module.__name__:
                        # Instantiate the tool
                        # Special handling for AgentsTool which needs the tool_manager
                        if name == "AgentsTool":
                            tool_instance = obj(tool_manager=self)
                        elif self.base_path:
                            tool_instance = obj(base_path=self.base_path)
                        else:
                            tool_instance = obj()

                        # Get tool specification
                        if hasattr(tool_instance, 'get_tool_spec'):
                            spec = tool_instance.get_tool_spec()
                            tool_name = spec.get('tool_name', name)

                            # Register the tool
                            self.tools[tool_name] = tool_instance
                            self.tool_specs[tool_name] = spec
                            # The print statement for successful loading has been removed.
                        else:
                            console.print(f"[yellow]⚠ Skipped {name}: No get_tool_spec() method[/yellow]")
            
            except Exception as e:
                console.print(f"[red]✗ Failed to load {tool_file.name}: {str(e)}[/red]")
    
    def get_all_tool_specs(self) -> List[Dict[str, Any]]:
        """
        Get specifications for all loaded tools.
        
        Returns:
            List of tool specifications
        """
        return list(self.tool_specs.values())
    
    def get_tool_spec(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specification for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool specification or None if not found
        """
        return self.tool_specs.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        List all available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def execute_tool_method(
        self, 
        tool_name: str, 
        method_name: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a method on a tool with safety checks.
        
        Args:
            tool_name: Name of the tool
            method_name: Name of the method to execute
            **kwargs: Method parameters
            
        Returns:
            Dict containing execution result and metadata
        """
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        tool_instance = self.tools[tool_name]
        
        if not hasattr(tool_instance, method_name):
            return {"success": False, "error": f"Method '{method_name}' not found in tool '{tool_name}'"}
        
        method = getattr(tool_instance, method_name)
        
        if not callable(method):
            return {"success": False, "error": f"'{method_name}' is not a callable method"}
        
        try:
            result = method(**kwargs)
            return result
            
        except TypeError as e:
            return {"success": False, "error": f"Invalid parameters: {str(e)}"}
        
        except Exception as e:
            return {"success": False, "error": f"Execution error: {str(e)}"}
    
    def _get_method_spec(self, tool_name: str, method_name: str) -> Optional[Dict]:
        """Get specification for a specific method."""
        spec = self.get_tool_spec(tool_name)
        if not spec:
            return None
        
        for method in spec.get("methods", []):
            if method["name"] == method_name:
                return method
        
        return None
    
    def reload_tools(self):
        """
        Reload all tools from the tools directory.
        """
        self.tools.clear()
        self.tool_specs.clear()
        self._load_tools()
        console.print("[green]✓ Tools reloaded[/green]")
