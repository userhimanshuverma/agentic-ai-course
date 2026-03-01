"""
MCP Tool Registry - Manages tool registration and discovery.
"""

from typing import Dict, List, Any, Optional
from .tools.calculator import calculator_tool
from .tools.code_executor import code_executor_tool
from .tools.file_tool import file_tool
from .tools.web_search import web_search_tool
from .tools.system_tool import system_tool


class ToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        self.register(calculator_tool)
        self.register(code_executor_tool)
        self.register(file_tool)
        self.register(web_search_tool)
        self.register(system_tool)
    
    def register(self, tool: Any) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self._tools:
            del self._tools[tool_name]
    
    def get(self, tool_name: str) -> Optional[Any]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools with their schemas."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self._tools.values()
        ]
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        tool = self.get(tool_name)
        if tool is None:
            return {
                "content": [{"type": "text", "text": f"Tool not found: {tool_name}"}],
                "isError": True
            }
        
        return tool.execute(arguments)
    
    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for LLM prompting."""
        descriptions = []
        for tool in self._tools.values():
            desc = f"- {tool.name}: {tool.description}"
            descriptions.append(desc)
        return "\n".join(descriptions)


# Global registry instance
registry = ToolRegistry()
