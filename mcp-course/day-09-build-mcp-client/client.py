#!/usr/bin/env python3
"""
Day 9: MCP Client
=================

A client that connects to MCP servers and uses their tools.
"""

import json
import subprocess
from typing import Dict, Any, List


class MCPClient:
    """
    A minimal but complete MCP client.
    
    Features:
    - Connects to MCP servers via stdio
    - Discovers available tools
    - Calls tools with arguments
    - Handles responses and errors
    """
    
    def __init__(self, server_command: List[str]):
        """
        Initialize client with server command.
        
        Args:
            server_command: Command to start server (e.g., ["python", "server.py"])
        """
        self.server_command = server_command
        self.process = None
        self.request_counter = 0
        self.tools = []
    
    def connect(self):
        """
        Start the server and connect to it.
        Discovers available tools.
        """
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Initialize connection
        self._send_request("initialize", {})
        
        # Discover available tools
        response = self._send_request("tools/list", {})
        self.tools = response.get("result", {}).get("tools", [])
        
        print(f"Connected! Found {len(self.tools)} tools:")
        for tool in self.tools:
            print(f"  • {tool['name']}: {tool['description']}")
    
    def disconnect(self):
        """Close connection to server."""
        if self.process:
            self.process.terminate()
            self.process = None
            print("Disconnected from server.")
    
    def list_tools(self) -> List[Dict]:
        """Return list of available tools."""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict = None) -> Any:
        """
        Call a tool by name.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool result
        
        Raises:
            Exception: If tool execution fails
        """
        if arguments is None:
            arguments = {}
        
        response = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        result = response.get("result", {})
        
        if result.get("isError"):
            content = result.get("content", [{}])[0]
            raise Exception(f"Tool error: {content.get('text', 'Unknown error')}")
        
        content = result.get("content", [{}])[0]
        return content.get("text")
    
    def _send_request(self, method: str, params: Dict) -> Dict:
        """
        Send a JSON-RPC request to the server.
        
        Args:
            method: JSON-RPC method
            params: Method parameters
        
        Returns:
            JSON-RPC response
        """
        self.request_counter += 1
        request_id = f"req_{self.request_counter}"
        
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id
        }
        
        # Send request
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        
        if not response_line:
            raise Exception("Server closed connection")
        
        response = json.loads(response_line)
        
        # Check for JSON-RPC error
        if "error" in response:
            raise Exception(f"Server error: {response['error']['message']}")
        
        return response


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import os
    
    # Path to server from Day 8
    server_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "day-08-build-minimal-mcp-server", 
        "server.py"
    )
    
    # Create client
    client = MCPClient(["python", server_path])
    
    try:
        # Connect to server
        print("=" * 60)
        print("MCP CLIENT EXAMPLE")
        print("=" * 60)
        client.connect()
        
        # Use tools
        print("\n" + "-" * 60)
        print("Using tools:")
        print("-" * 60)
        
        # Call echo
        result = client.call_tool("echo", {"message": "Hello from client!"})
        print(f"\n📝 Echo: {result}")
        
        # Call calculate
        result = client.call_tool("calculate", {"expression": "10 * 5 + 3"})
        print(f"🔢 Calculate: 10 * 5 + 3 = {result}")
        
        # Call reverse_text
        result = client.call_tool("reverse_text", {"text": "MCP Client"})
        print(f"🔄 Reverse: 'MCP Client' → {result}")
        
        # Call word_count
        result = client.call_tool("word_count", {"text": "The quick brown fox"})
        print(f"📊 Word count: {result}")
        
        # Call system info
        result = client.call_tool("get_system_info", {})
        print(f"\n💻 System Info: {result}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Always disconnect
        print("\n" + "-" * 60)
        client.disconnect()
    
    print("\n" + "=" * 60)
    print("Done!")
