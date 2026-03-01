# Day 9: Build MCP Client

## 🎯 What We're Building

A client that connects to our MCP server and uses its tools.

## 📁 Project Structure

```
day-09-build-mcp-client/
├── README.md
├── client.py          # The MCP client
├── main.py            # Example usage
└── requirements.txt   # (empty - pure Python!)
```

## 🔧 Step 1: Create the Client

Create `client.py`:

```python
#!/usr/bin/env python3
"""
Minimal MCP Client
==================

A client that connects to MCP servers and uses their tools.
"""

import json
import subprocess
from typing import Dict, Any, List


class MCPClient:
    """A minimal but complete MCP client"""
    
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
        """Start the server and connect to it"""
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
            print(f"  - {tool['name']}: {tool['description']}")
    
    def disconnect(self):
        """Close connection to server"""
        if self.process:
            self.process.terminate()
            self.process = None
    
    def list_tools(self) -> List[Dict]:
        """Return list of available tools"""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict = None) -> Any:
        """
        Call a tool by name.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool result
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
        """Send a JSON-RPC request to the server"""
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


if __name__ == "__main__":
    # Example usage
    import os
    
    # Path to server from Day 8
    server_path = os.path.join(os.path.dirname(__file__), "..", "day-08-build-minimal-mcp-server", "server.py")
    
    # Create client
    client = MCPClient(["python", server_path])
    
    try:
        # Connect to server
        client.connect()
        
        # Use tools
        print("\nUsing tools:")
        print("-" * 40)
        
        # Call echo
        result = client.call_tool("echo", {"message": "Hello from client!"})
        print(f"Echo: {result}")
        
        # Call calculate
        result = client.call_tool("calculate", {"expression": "10 * 5 + 3"})
        print(f"Calculate: {result}")
        
        # Call system info
        result = client.call_tool("get_system_info", {})
        print(f"System Info: {result}")
        
    finally:
        # Always disconnect
        client.disconnect()
```

## 🧪 Step 2: Create Example Usage

Create `main.py`:

```python
#!/usr/bin/env python3
"""Example: Using the MCP client"""

import os
from client import MCPClient


def main():
    print("=" * 50)
    print("MCP Client Example")
    print("=" * 50)
    
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
        # Connect
        print("\n1. Connecting to server...")
        client.connect()
        
        # Show available tools
        print("\n2. Available tools:")
        for tool in client.list_tools():
            print(f"   • {tool['name']}: {tool['description']}")
        
        # Use calculator
        print("\n3. Using calculator:")
        expressions = ["2 + 2", "10 * 5", "100 / 4", "2 ** 8"]
        for expr in expressions:
            result = client.call_tool("calculate", {"expression": expr})
            print(f"   {expr} = {result}")
        
        # Use echo
        print("\n4. Using echo:")
        messages = ["Hello", "MCP is cool", "Python rocks"]
        for msg in messages:
            result = client.call_tool("echo", {"message": msg})
            print(f"   {result}")
        
        # Get system info
        print("\n5. System information:")
        result = client.call_tool("get_system_info", {})
        print(f"   {result}")
        
    except Exception as e:
        print(f"\nError: {e}")
    
    finally:
        # Disconnect
        print("\n6. Disconnecting...")
        client.disconnect()
    
    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
```

## 🚀 Running the Client

```bash
python main.py
```

Expected output:
```
==================================================
MCP Client Example
==================================================

1. Connecting to server...
Connected! Found 3 tools:
  - get_system_info: Get system information
  - calculate: Calculate expression
  - echo: Echo a message

2. Available tools:
   • get_system_info: Get system information
   • calculate: Calculate expression
   • echo: Echo a message

3. Using calculator:
   2 + 2 = 4
   10 * 5 = 50
   100 / 4 = 25.0
   2 ** 8 = 256

4. Using echo:
   Echo: Hello
   Echo: MCP is cool
   Echo: Python rocks

5. System information:
   {'platform': 'Windows', 'version': '10', 'python': '3.12'}

6. Disconnecting...

==================================================
Done!
```

## 📊 Client Architecture

```
┌─────────────────────────────────────┐
│           MCP Client                │
├─────────────────────────────────────┤
│                                     │
│  1. Connection Management           │
│     subprocess.Popen(server)        │
│                                     │
│  2. Request Builder                 │
│     Build JSON-RPC requests         │
│                                     │
│  3. Transport                       │
│     stdin.write() → server          │
│     stdout.readline() ← response    │
│                                     │
│  4. Response Handler                │
│     Parse JSON-RPC                  │
│     Check for errors                │
│     Return result                   │
│                                     │
│  5. Tool Interface                  │
│     list_tools()                    │
│     call_tool(name, args)           │
│                                     │
└─────────────────────────────────────┘
```

## 🎓 Key Takeaway

**MCP Client = JSON-RPC over stdio**

1. **Start server** as subprocess
2. **Send JSON** to server's stdin
3. **Read JSON** from server's stdout
4. **Parse and return** results

Simple, clean, works with any MCP server!

## 🚀 What's Next?

Tomorrow: **Plug-and-Play Tools** - We'll add new tools without changing the client!

---

**Remember:** The client doesn't need to know about tools in advance. It discovers them at runtime. That's the power of MCP!
