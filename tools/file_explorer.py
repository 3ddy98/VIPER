"""
File Explorer Tool

This tool allows the AI agent to explore the host file system safely.
All operations are read-only to prevent destructive actions.

The tool provides:
- Directory listing
- File reading
- File information retrieval
- File searching capabilities
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class FileExplorerTool:
    """
    File system exploration tool for AI agents.
    
    This tool provides read-only access to the file system, allowing
    the agent to navigate directories, read files, and search for content.
    All operations are non-destructive.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the File Explorer tool.
        
        Args:
            base_path: Optional base path to restrict access (default: current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.tool_name = "FILE_EXPLORER"
    
    def list_directory(self, path: str = ".", recursive: bool = False, max_depth: int = 3) -> Dict[str, Any]:
        """
        List files and directories in the specified path.
        
        Args:
            path: Directory path to list (relative to base_path)
            recursive: Whether to list recursively
            max_depth: Maximum depth for recursive listing
            
        Returns:
            Dict containing directory listing and metadata
        """
        try:
            target_path = self.base_path / path
            
            # Security check: ensure we're not escaping base_path
            if not self._is_safe_path(target_path):
                return {
                    "success": False,
                    "error": "Access denied: Path is outside allowed directory"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}"
                }
            
            if not target_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            # List directory contents
            items = []
            
            if recursive:
                items = self._list_recursive(target_path, max_depth)
            else:
                for item in sorted(target_path.iterdir()):
                    items.append(self._get_item_info(item))
            
            return {
                "success": True,
                "path": str(target_path.relative_to(self.base_path)),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}"
            }
    
    def read_file(self, file_path: str, max_size: int = 1024 * 1024,
                 start_line: Optional[int] = None, line_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Read the contents of a text file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            max_size: Maximum file size to read in bytes (default: 1MB)
            start_line: Starting line number (1-indexed). If None, reads from beginning
            line_count: Number of lines to read. If None, reads to end of file
            
        Returns:
            Dict containing file contents and metadata
        """
        try:
            target_path = self.base_path / file_path
            
            # Security check
            if not self._is_safe_path(target_path):
                return {
                    "success": False,
                    "error": "Access denied: Path is outside allowed directory"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                }
            
            if not target_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Check file size (only if reading entire file)
            file_size = target_path.stat().st_size
            if start_line is None and line_count is None and file_size > max_size:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max: {max_size} bytes). Use start_line and line_count to read specific portions."
                }
            
            # Read file contents
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": "File is not a text file or uses unsupported encoding"
                }
            
            total_lines = len(lines)
            
            # Handle line range selection
            if start_line is not None:
                # Convert to 0-indexed
                start_idx = max(0, start_line - 1)
                
                if start_idx >= total_lines:
                    return {
                        "success": False,
                        "error": f"start_line {start_line} exceeds file length ({total_lines} lines)"
                    }
                
                # Calculate end index
                if line_count is not None:
                    end_idx = min(start_idx + line_count, total_lines)
                else:
                    end_idx = total_lines
                
                # Extract the requested lines
                selected_lines = lines[start_idx:end_idx]
                content = ''.join(selected_lines)
                
                return {
                    "success": True,
                    "path": str(target_path.relative_to(self.base_path)),
                    "content": content,
                    "total_lines": total_lines,
                    "start_line": start_line,
                    "end_line": start_idx + len(selected_lines),
                    "lines_read": len(selected_lines),
                    "size": file_size,
                    "partial_read": True
                }
            else:
                # Read entire file
                content = ''.join(lines)
                
                return {
                    "success": True,
                    "path": str(target_path.relative_to(self.base_path)),
                    "content": content,
                    "total_lines": total_lines,
                    "lines_read": total_lines,
                    "size": file_size,
                    "partial_read": False
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Args:
            file_path: Path to the file/directory (relative to base_path)
            
        Returns:
            Dict containing file metadata
        """
        try:
            target_path = self.base_path / file_path
            
            # Security check
            if not self._is_safe_path(target_path):
                return {
                    "success": False,
                    "error": "Access denied: Path is outside allowed directory"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {file_path}"
                }
            
            stat = target_path.stat()
            
            return {
                "success": True,
                "path": str(target_path.relative_to(self.base_path)),
                "name": target_path.name,
                "type": "directory" if target_path.is_dir() else "file",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": target_path.suffix if target_path.is_file() else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting file info: {str(e)}"
            }
    
    def search_files(self, pattern: str, search_path: str = ".", 
                    max_results: int = 100) -> Dict[str, Any]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: File name pattern (supports wildcards like *.py)
            search_path: Directory to search in (relative to base_path)
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        try:
            target_path = self.base_path / search_path
            
            # Security check
            if not self._is_safe_path(target_path):
                return {
                    "success": False,
                    "error": "Access denied: Path is outside allowed directory"
                }
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {search_path}"
                }
            
            # Search for files
            results = []
            for file_path in target_path.rglob(pattern):
                if len(results) >= max_results:
                    break
                
                results.append({
                    "path": str(file_path.relative_to(self.base_path)),
                    "name": file_path.name,
                    "type": "directory" if file_path.is_dir() else "file",
                    "size": file_path.stat().st_size if file_path.is_file() else None
                })
            
            return {
                "success": True,
                "pattern": pattern,
                "search_path": str(target_path.relative_to(self.base_path)),
                "results": results,
                "count": len(results),
                "truncated": len(results) >= max_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching files: {str(e)}"
            }
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        
        Returns:
            Dict containing tool name, methods, parameters, and metadata
        """
        return {
            "tool_name": self.tool_name,
            "description": "File system exploration tool for reading and navigating directories",
            "version": "1.0.0",
            "methods": [
                {
                    "name": "list_directory",
                    "description": "List files and directories in a specified path",
                    "parameters": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list (relative)",
                            "required": False,
                            "default": "."
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list recursively",
                            "required": False,
                            "default": False
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum depth for recursive listing",
                            "required": False,
                            "default": 3
                        }
                    },
                    "returns": "Dictionary with directory listing and metadata",
                    "destruct_flag": False
                },
                {
                    "name": "read_file",
                    "description": "Read the contents of a text file, with optional line range selection to avoid context overflow",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read",
                            "required": True
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Maximum file size in bytes (only enforced when reading entire file)",
                            "required": False,
                            "default": 1048576
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Starting line number (1-indexed). If specified, reads from this line. If None, reads from beginning.",
                            "required": False,
                            "default": None
                        },
                        "line_count": {
                            "type": "integer",
                            "description": "Number of lines to read starting from start_line. If None, reads to end of file.",
                            "required": False,
                            "default": None
                        }
                    },
                    "returns": "Dictionary with file contents, metadata, and line range information",
                    "destruct_flag": False
                },
                {
                    "name": "get_file_info",
                    "description": "Get detailed information about a file or directory",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file/directory",
                            "required": True
                        }
                    },
                    "returns": "Dictionary with file metadata",
                    "destruct_flag": False
                },
                {
                    "name": "search_files",
                    "description": "Search for files matching a pattern",
                    "parameters": {
                        "pattern": {
                            "type": "string",
                            "description": "File name pattern (supports wildcards)",
                            "required": True
                        },
                        "search_path": {
                            "type": "string",
                            "description": "Directory to search in",
                            "required": False,
                            "default": "."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "required": False,
                            "default": 100
                        }
                    },
                    "returns": "Dictionary with search results",
                    "destruct_flag": False
                }
            ]
        }
    
    # Private helper methods
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within allowed directory."""
        try:
            path.resolve().relative_to(self.base_path.resolve())
            return True
        except ValueError:
            return False
    
    def _get_item_info(self, path: Path) -> Dict[str, Any]:
        """Get basic info about a file/directory item."""
        try:
            stat = path.stat()
            return {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "size": stat.st_size if path.is_file() else None,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception:
            return {
                "name": path.name,
                "type": "unknown",
                "error": "Could not read file information"
            }
    
    def _list_recursive(self, path: Path, max_depth: int, current_depth: int = 0) -> List[Dict[str, Any]]:
        """Recursively list directory contents."""
        items = []
        
        if current_depth >= max_depth:
            return items
        
        try:
            for item in sorted(path.iterdir()):
                item_info = self._get_item_info(item)
                item_info["depth"] = current_depth
                items.append(item_info)
                
                # Recurse into directories
                if item.is_dir():
                    sub_items = self._list_recursive(item, max_depth, current_depth + 1)
                    items.extend(sub_items)
        except PermissionError:
            pass  # Skip directories we can't access
        
        return items
