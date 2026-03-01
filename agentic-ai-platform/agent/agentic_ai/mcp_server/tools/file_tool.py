"""
File read/write tool for MCP server.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from ...utils.config import config


class FileTool:
    """Safe file operations tool."""
    
    name = "file_tool"
    description = "Read and write files in a safe directory"
    
    input_schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["read", "write", "list", "delete"],
                "description": "File operation to perform"
            },
            "filename": {
                "type": "string",
                "description": "Name of the file"
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operation)"
            }
        },
        "required": ["operation", "filename"]
    }
    
    def __init__(self):
        self.safe_dir = Path(config.SAFE_DIRECTORY).resolve()
        self.safe_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operation."""
        operation = arguments.get("operation")
        filename = arguments.get("filename", "")
        
        if not filename:
            return {
                "content": [{"type": "text", "text": "Error: Filename required"}],
                "isError": True
            }
        
        # Validate filename
        if not self._is_valid_filename(filename):
            return {
                "content": [{"type": "text", "text": "Error: Invalid filename"}],
                "isError": True
            }
        
        # Get full path
        file_path = self._get_safe_path(filename)
        
        try:
            if operation == "read":
                return self._read_file(file_path)
            elif operation == "write":
                content = arguments.get("content", "")
                return self._write_file(file_path, content)
            elif operation == "list":
                return self._list_files()
            elif operation == "delete":
                return self._delete_file(file_path)
            else:
                return {
                    "content": [{"type": "text", "text": f"Error: Unknown operation: {operation}"}],
                    "isError": True
                }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is valid and safe."""
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in config.ALLOWED_FILE_EXTENSIONS:
            return False
        
        return True
    
    def _get_safe_path(self, filename: str) -> Path:
        """Get safe path within allowed directory."""
        file_path = (self.safe_dir / filename).resolve()
        
        # Ensure path is within safe directory
        if not str(file_path).startswith(str(self.safe_dir)):
            raise ValueError("Path traversal detected")
        
        return file_path
    
    def _read_file(self, file_path: Path) -> Dict[str, Any]:
        """Read file contents."""
        if not file_path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {file_path.name}"}],
                "isError": True
            }
        
        content = file_path.read_text(encoding="utf-8")
        return {
            "content": [{"type": "text", "text": content}],
            "isError": False
        }
    
    def _write_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Write content to file."""
        file_path.write_text(content, encoding="utf-8")
        return {
            "content": [{"type": "text", "text": f"File written: {file_path.name}"}],
            "isError": False
        }
    
    def _list_files(self) -> Dict[str, Any]:
        """List all files in safe directory."""
        files = [f.name for f in self.safe_dir.iterdir() if f.is_file()]
        return {
            "content": [{"type": "text", "text": f"Files: {', '.join(files) if files else 'No files'}"}],
            "isError": False
        }
    
    def _delete_file(self, file_path: Path) -> Dict[str, Any]:
        """Delete a file."""
        if not file_path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {file_path.name}"}],
                "isError": True
            }
        
        file_path.unlink()
        return {
            "content": [{"type": "text", "text": f"File deleted: {file_path.name}"}],
            "isError": False
        }


# Tool instance
file_tool = FileTool()
