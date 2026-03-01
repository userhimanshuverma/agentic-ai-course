#!/usr/bin/env python3
"""
Day 10: Plug-and-Play MCP Server
================================

This server automatically discovers tools from the tools/ directory.
Adding a new tool is as simple as creating a new file!
"""

import json
import sys
import os
from typing import Dict, Any, Callable


# ============================================================
# TOOL REGISTRY (Global)
# ============================================================

TOOLS: Dict[str, Dict] = {}

def register_tool(name: str, description: str):
    """
    Decorator to register a tool.
    
    Usage:
        @register_tool("my_tool", "Does something")
        def my_tool():
            return "result"
    """
    def decorator(func: Callable):
        TOOLS[name] = {
            "name": name,
            "description": description,
            "handler": func
        }
        return func
    return decorator


# ============================================================
# TOOL MODULES (Auto-imported)
# ============================================================

# Calculator Tools
@register_tool("add", "Add two numbers")
def add(a: float, b: float):
    return a + b

@register_tool("subtract", "Subtract two numbers")
def subtract(a: float, b: float):
    return a - b

@register_tool("multiply", "Multiply two numbers")
def multiply(a: float, b: float):
    return a * b

@register_tool("divide", "Divide two numbers")
def divide(a: float, b: float):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@register_tool("power", "Calculate power (a^b)")
def power(a: float, b: float):
    return a ** b


# String Tools
@register_tool("uppercase", "Convert text to uppercase")
def uppercase(text: str):
    return text.upper()

@register_tool("lowercase", "Convert text to lowercase")
def lowercase(text: str):
    return text.lower()

@register_tool("title_case", "Convert text to title case")
def title_case(text: str):
    return text.title()

@register_tool("count_chars", "Count characters in text")
def count_chars(text: str):
    return {"characters": len(text), "words": len(text.split())}


# List Tools
@register_tool("sort_list", "Sort a list of items")
def sort_list(items: list, reverse: bool = False):
    return sorted(items, reverse=reverse)

@register_tool("unique_items", "Get unique items from a list")
def unique_items(items: list):
    return list(set(items))


# Info Tools
@register_tool("get_timestamp", "Get current timestamp")
def get_timestamp():
    from datetime import datetime
    return datetime.now().isoformat()

@register_tool("get_date", "Get current date")
def get_date():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

@register_tool("get_time", "Get current time")
def get_time():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


# ============================================================
# MCP SERVER
# ============================================================

class PlugAndPlayMCPServer:
    """
    MCP server with dynamic tool discovery.
    
    To add a new tool:
    1. Create a function above with @register_tool decorator
    2. Restart the server
    3. Client automatically discovers it!
    """
    
    def __init__(self):
        self.tools = TOOLS
        print(f"Server initialized with {len(self.tools)} tools", file=sys.stderr)
    
    def run(self):
        """Main server loop."""
        print("Server running. Waiting for requests...", file=sys.stderr)
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                self.send_error(None, -32700, f"Parse error: {e}")
            except Exception as e:
                self.send_error(None, -32603, f"Internal error: {e}")
    
    def handle_request(self, request: Dict) -> Dict:
        """Route request to handler."""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, request.get("params", {}))
        else:
            return self.send_error(request_id, -32601, f"Method not found: {method}")
    
    def handle_initialize(self, request_id) -> Dict:
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}}
            },
            "id": request_id
        }
    
    def handle_list_tools(self, request_id) -> Dict:
        """Return all registered tools."""
        tools_list = [
            {"name": tool["name"], "description": tool["description"]}
            for tool in self.tools.values()
        ]
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": request_id
        }
    
    def handle_call_tool(self, request_id: str, params: Dict) -> Dict:
        """Execute a tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
        
        try:
            handler = self.tools[tool_name]["handler"]
            result = handler(**arguments)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False
                },
                "id": request_id
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True
                },
                "id": request_id
            }
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id
        }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    server = PlugAndPlayMCPServer()
    server.run()
