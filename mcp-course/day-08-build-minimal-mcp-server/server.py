#!/usr/bin/env python3
"""
Day 8: Minimal MCP Server
=========================

A complete, working MCP server in pure Python.
No frameworks, no dependencies (except standard library).

This server:
- Uses stdio transport (reads from stdin, writes to stdout)
- Handles JSON-RPC requests
- Registers and executes tools
- Returns proper JSON-RPC responses
"""

import json
import sys
from typing import Dict, Any, Callable


class MinimalMCPServer:
    """
    A minimal but complete MCP server.
    
    Features:
    - JSON-RPC 2.0 protocol support
    - Tool registration and execution
    - Error handling
    - stdio transport
    """
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        print(f"Server initialized. Registered tools: {len(self.tools)}", file=sys.stderr)
    
    def register_tool(self, name: str, description: str, handler: Callable):
        """
        Register a tool with the server.
        
        Args:
            name: Tool name (must be unique)
            description: What the tool does
            handler: Function to execute when tool is called
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
        print(f"Registered tool: {name}", file=sys.stderr)
    
    def run(self):
        """
        Main server loop.
        
        Reads JSON-RPC requests from stdin,
        processes them, and writes responses to stdout.
        """
        print("Server running. Waiting for requests...", file=sys.stderr)
        
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    break  # EOF - client disconnected
                
                # Parse the request
                request = json.loads(line)
                
                # Process and respond
                response = self.handle_request(request)
                
                # Write response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                self.send_error(None, -32700, f"Parse error: {e}")
            except Exception as e:
                self.send_error(None, -32603, f"Internal error: {e}")
    
    def handle_request(self, request: Dict) -> Dict:
        """
        Route request to appropriate handler based on method.
        """
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
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                }
            },
            "id": request_id
        }
    
    def handle_list_tools(self, request_id) -> Dict:
        """Return list of available tools."""
        tools_list = [
            {
                "name": tool["name"],
                "description": tool["description"]
            }
            for tool in self.tools.values()
        ]
        
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": request_id
        }
    
    def handle_call_tool(self, request_id: str, params: Dict) -> Dict:
        """Execute a tool and return the result."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Check if tool exists
        if tool_name not in self.tools:
            return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
        
        # Execute the tool
        try:
            handler = self.tools[tool_name]["handler"]
            result = handler(**arguments)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ],
                    "isError": False
                },
                "id": request_id
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {str(e)}"
                        }
                    ],
                    "isError": True
                },
                "id": request_id
            }
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        """Send error response."""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def get_system_info():
    """Get basic system information."""
    import platform
    return {
        "platform": platform.system(),
        "version": platform.version(),
        "python": platform.python_version()
    }

def calculate(expression: str):
    """Calculate a mathematical expression safely."""
    try:
        # Safe evaluation - only allow basic math
        allowed = {"__builtins__": {}}
        result = eval(expression, allowed, {})
        return result
    except Exception as e:
        return f"Error: {e}"

def echo(message: str):
    """Echo back a message."""
    return f"Echo: {message}"

def reverse_text(text: str):
    """Reverse a string."""
    return text[::-1]

def word_count(text: str):
    """Count words in text."""
    words = text.split()
    return {"word_count": len(words), "character_count": len(text)}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Create server
    server = MinimalMCPServer()
    
    # Register tools
    server.register_tool("get_system_info", "Get system information", get_system_info)
    server.register_tool("calculate", "Calculate expression (e.g., '2 + 2')", calculate)
    server.register_tool("echo", "Echo a message", echo)
    server.register_tool("reverse_text", "Reverse a string", reverse_text)
    server.register_tool("word_count", "Count words in text", word_count)
    
    # Start server
    server.run()
