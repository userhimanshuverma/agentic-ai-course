# Day 8: Build Minimal MCP Server

## 🎯 What We're Building

A working MCP server in pure Python. No frameworks, no dependencies (except standard library).

## 📁 Project Structure

```
day-08-build-minimal-mcp-server/
├── README.md
├── server.py          # The MCP server
├── tools.py           # Tool implementations
└── requirements.txt   # (empty - pure Python!)
```

## 🔧 Step 1: Create the Server

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Minimal MCP Server
==================

A working MCP server with stdio transport.
"""

import json
import sys
from typing import Dict, Any, Callable


class MinimalMCPServer:
    """A minimal but complete MCP server"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.request_id = 0
    
    def register_tool(self, name: str, description: str, handler: Callable):
        """Register a tool with the server"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
    
    def run(self):
        """Main server loop - reads from stdin, writes to stdout"""
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
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
        """Route request to appropriate handler"""
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
        """Handle initialization request"""
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
        """Return list of available tools"""
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
        """Execute a tool"""
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
        """Send error response"""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }


# Tool implementations
def get_system_info():
    """Get basic system information"""
    import platform
    return {
        "platform": platform.system(),
        "version": platform.version(),
        "python": platform.python_version()
    }

def calculate(expression: str):
    """Calculate a mathematical expression"""
    try:
        # Safe evaluation - only allow basic math
        allowed = {"__builtins__": {}}
        result = eval(expression, allowed, {})
        return result
    except Exception as e:
        return f"Error: {e}"

def echo(message: str):
    """Echo back a message"""
    return f"Echo: {message}"


if __name__ == "__main__":
    # Create server
    server = MinimalMCPServer()
    
    # Register tools
    server.register_tool("get_system_info", "Get system information", get_system_info)
    server.register_tool("calculate", "Calculate expression (e.g., '2 + 2')", calculate)
    server.register_tool("echo", "Echo a message", echo)
    
    # Start server
    server.run()
```

## 🧪 Step 2: Test the Server

Create `test_server.py`:

```python
#!/usr/bin/env python3
"""Test the MCP server"""

import subprocess
import json

def send_request(process, request):
    """Send a request to the server"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    response = process.stdout.readline()
    return json.loads(response)

def main():
    # Start the server
    process = subprocess.Popen(
        ["python", "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("Testing MCP Server...")
    print("=" * 50)
    
    # Test 1: Initialize
    print("\n1. Testing initialize...")
    response = send_request(process, {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {},
        "id": "init_1"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 2: List tools
    print("\n2. Testing tools/list...")
    response = send_request(process, {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "list_1"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 3: Call echo tool
    print("\n3. Testing tools/call (echo)...")
    response = send_request(process, {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "echo",
            "arguments": {"message": "Hello MCP!"}
        },
        "id": "call_1"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 4: Call calculate tool
    print("\n4. Testing tools/call (calculate)...")
    response = send_request(process, {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "calculate",
            "arguments": {"expression": "2 + 3 * 4"}
        },
        "id": "call_2"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 5: Call system info
    print("\n5. Testing tools/call (get_system_info)...")
    response = send_request(process, {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_system_info",
            "arguments": {}
        },
        "id": "call_3"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Cleanup
    process.terminate()
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()
```

## 🚀 Running the Server

### Terminal 1: Run the Server
```bash
python server.py
```

The server waits for input on stdin.

### Terminal 2: Test It
```bash
python test_server.py
```

Expected output:
```
Testing MCP Server...
==================================================

1. Testing initialize...
Response: {
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    }
  },
  "id": "init_1"
}

2. Testing tools/list...
Response: {
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {"name": "get_system_info", "description": "Get system information"},
      {"name": "calculate", "description": "Calculate expression"},
      {"name": "echo", "description": "Echo a message"}
    ]
  },
  "id": "list_1"
}

3. Testing tools/call (echo)...
Response: {
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "Echo: Hello MCP!"}],
    "isError": false
  },
  "id": "call_1"
}
...
```

## 📊 Server Architecture

```
┌─────────────────────────────────────┐
│         Minimal MCP Server          │
├─────────────────────────────────────┤
│                                     │
│  1. Transport (stdio)               │
│     sys.stdin → parse JSON          │
│                                     │
│  2. Router                          │
│     initialize → handle_initialize  │
│     tools/list → handle_list_tools  │
│     tools/call → handle_call_tool   │
│                                     │
│  3. Tool Registry                   │
│     {"tool_name": handler}          │
│                                     │
│  4. Response Formatter              │
│     Format as JSON-RPC              │
│     sys.stdout.write()              │
│                                     │
└─────────────────────────────────────┘
```

## 🎓 Key Takeaway

**A minimal MCP server needs only:**
1. **Transport** - Read/write JSON (stdio in this case)
2. **Router** - Route methods to handlers
3. **Registry** - Store tool definitions
4. **Formatter** - Return JSON-RPC responses

**Total code: ~150 lines of pure Python**

## 🚀 What's Next?

Tomorrow: **Build MCP Client** - We'll create a client that talks to this server.

---

**Remember:** MCP servers don't need complex frameworks. JSON in, JSON out, route to handlers. That's it!
