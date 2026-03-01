# Day 10: Plug-and-Play Tools

## 🎯 What We're Learning

How to add new tools to an MCP server without changing the client.

This is the "USB-C" magic of MCP!

## 🔌 The Problem

**Without MCP:**
```
Add new tool → Update server → Update client → Redeploy everything
```

**With MCP:**
```
Add new tool → Update server → Client automatically discovers it!
```

## 📁 Project Structure

```
day-10-plug-and-play-tools/
├── README.md
├── server.py              # Enhanced server with dynamic tools
├── tools/                 # Tool plugins
│   ├── __init__.py
│   ├── calculator.py
│   ├── datetime_tools.py
│   └── file_tools.py
├── client.py              # Unchanged from Day 9
└── main.py                # Demo
```

## 🔧 Step 1: Create Tool Plugins

Create `tools/__init__.py`:

```python
"""Tool plugins package"""

from typing import Dict, Callable

# Registry of all tools
TOOLS: Dict[str, Dict] = {}

def register_tool(name: str, description: str):
    """Decorator to register a tool"""
    def decorator(func: Callable):
        TOOLS[name] = {
            "name": name,
            "description": description,
            "handler": func
        }
        return func
    return decorator

def get_all_tools():
    """Get all registered tools"""
    return TOOLS
```

Create `tools/calculator.py`:

```python
"""Calculator tool plugin"""

from . import register_tool

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
```

Create `tools/datetime_tools.py`:

```python
"""DateTime tool plugin"""

from datetime import datetime, timedelta
from . import register_tool

@register_tool("get_current_time", "Get current time")
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@register_tool("get_current_date", "Get current date")
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

@register_tool("days_until", "Days until a date (YYYY-MM-DD)")
def days_until(target_date: str):
    target = datetime.strptime(target_date, "%Y-%m-%d")
    today = datetime.now()
    diff = target - today
    return diff.days
```

Create `tools/file_tools.py`:

```python
"""File tool plugin"""

import os
from . import register_tool

@register_tool("list_files", "List files in directory")
def list_files(directory: str = "."):
    try:
        files = os.listdir(directory)
        return {"files": files, "count": len(files)}
    except Exception as e:
        return {"error": str(e)}

@register_tool("read_file", "Read file contents")
def read_file(filepath: str):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

@register_tool("file_info", "Get file information")
def file_info(filepath: str):
    try:
        stat = os.stat(filepath)
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": os.path.isfile(filepath),
            "is_dir": os.path.isdir(filepath)
        }
    except Exception as e:
        return {"error": str(e)}
```

## 🔧 Step 2: Create Dynamic Server

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Plug-and-Play MCP Server
========================

Discovers tools automatically from the tools/ directory.
"""

import json
import sys
import importlib
import pkgutil
from typing import Dict, Any

# Import all tool modules to register them
from tools import get_all_tools
import tools

# Auto-discover and import all tool modules
for importer, modname, ispkg in pkgutil.iter_modules(tools.__path__):
    importlib.import_module(f"tools.{modname}")


class PlugAndPlayMCPServer:
    """MCP server with dynamic tool discovery"""
    
    def __init__(self):
        self.tools = get_all_tools()
        self.request_counter = 0
    
    def run(self):
        """Main server loop"""
        print(f"Server started with {len(self.tools)} tools", file=sys.stderr)
        
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
        """Route request to handler"""
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


if __name__ == "__main__":
    server = PlugAndPlayMCPServer()
    server.run()
```

## 🧪 Step 3: Create Demo

Create `main.py`:

```python
#!/usr/bin/env python3
"""Demo: Plug-and-Play Tools"""

import sys
import os

# Add parent directory to path for client import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))

from client import MCPClient


def main():
    print("=" * 60)
    print("Plug-and-Play Tools Demo")
    print("=" * 60)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        print("\n1. Connecting to server...")
        client.connect()
        
        print("\n2. All available tools (auto-discovered):")
        for tool in client.list_tools():
            print(f"   • {tool['name']}: {tool['description']}")
        
        # Calculator tools
        print("\n3. Calculator tools:")
        result = client.call_tool("add", {"a": 10, "b": 5})
        print(f"   10 + 5 = {result}")
        
        result = client.call_tool("multiply", {"a": 7, "b": 8})
        print(f"   7 * 8 = {result}")
        
        # DateTime tools
        print("\n4. DateTime tools:")
        result = client.call_tool("get_current_time", {})
        print(f"   Current time: {result}")
        
        result = client.call_tool("get_current_date", {})
        print(f"   Current date: {result}")
        
        result = client.call_tool("days_until", {"target_date": "2025-12-25"})
        print(f"   Days until Christmas 2025: {result}")
        
        # File tools
        print("\n5. File tools:")
        result = client.call_tool("list_files", {"directory": "."})
        print(f"   Files: {result}")
        
    finally:
        client.disconnect()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("\nTo add a new tool:")
    print("  1. Create tools/my_new_tool.py")
    print("  2. Use @register_tool decorator")
    print("  3. Restart server - client auto-discovers it!")


if __name__ == "__main__":
    main()
```

## 🚀 Running the Demo

```bash
python main.py
```

Expected output:
```
============================================================
Plug-and-Play Tools Demo
============================================================

1. Connecting to server...
Connected! Found 10 tools:
  - add: Add two numbers
  - subtract: Subtract two numbers
  - multiply: Multiply two numbers
  - divide: Divide two numbers
  - get_current_time: Get current time
  - get_current_date: Get current date
  - days_until: Days until a date
  - list_files: List files in directory
  - read_file: Read file contents
  - file_info: Get file information

2. All available tools (auto-discovered):
   • add: Add two numbers
   • subtract: Subtract two numbers
   ...

3. Calculator tools:
   10 + 5 = 15
   7 * 8 = 56

4. DateTime tools:
   Current time: 2024-01-15 14:30:45
   Current date: 2024-01-15
   Days until Christmas 2025: 344

5. File tools:
   Files: {'files': ['README.md', 'server.py', ...], 'count': 5}

============================================================
Demo complete!

To add a new tool:
  1. Create tools/my_new_tool.py
  2. Use @register_tool decorator
  3. Restart server - client auto-discovers it!
```

## 🎓 Key Takeaway

**Plug-and-Play Magic:**

1. **Create tool file** → `tools/my_tool.py`
2. **Add @register_tool decorator** → Tool appears in server
3. **Client discovers automatically** → No client changes needed!

This is why MCP is powerful: **Tools and clients are decoupled!**

## 🚀 What's Next?

Tomorrow: **Multi-Agent Architecture** - Multiple agents sharing one MCP server!

---

**Remember:** The client doesn't know about tools until runtime. It asks the server "what can you do?" and adapts. That's true plug-and-play!
