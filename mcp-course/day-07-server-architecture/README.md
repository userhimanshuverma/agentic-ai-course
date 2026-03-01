# Day 7: Server Architecture

## 🎯 MCP Server Internals

Today we learn how MCP servers are structured internally.

## 🏗️ Server Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  MCP SERVER                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │           TRANSPORT LAYER                        │   │
│  │  (How clients connect)                           │   │
│  │  • stdio (standard input/output)                 │   │
│  │  • HTTP/SSE (Server-Sent Events)                 │   │
│  │  • WebSocket                                     │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           PROTOCOL HANDLER                       │   │
│  │  (JSON-RPC processing)                           │   │
│  │  • Parse requests                                │   │
│  │  • Validate format                               │   │
│  │  • Route to handlers                             │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           TOOL REGISTRY                          │   │
│  │  (Available tools)                               │   │
│  │  • Tool definitions                              │   │
│  │  • Input schemas                                 │   │
│  │  • Handler functions                             │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           EXECUTION ENGINE                       │   │
│  │  (Run the tools)                                 │   │
│  │  • Validate inputs                               │   │
│  │  • Execute tool                                  │   │
│  │  • Format output                                 │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           RESPONSE FORMATTER                     │   │
│  │  (JSON-RPC responses)                            │   │
│  │  • Success responses                             │   │
│  │  • Error responses                               │   │
│  │  • Content formatting                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📡 Transport Layer

### stdio (Standard Input/Output)

Best for: Local processes, simple setups

```python
# Server reads from stdin, writes to stdout
import sys
import json

class StdioTransport:
    def read_message(self):
        """Read JSON-RPC message from stdin"""
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    
    def write_message(self, message):
        """Write JSON-RPC message to stdout"""
        sys.stdout.write(json.dumps(message) + "\n")
        sys.stdout.flush()
```

### HTTP/SSE (Server-Sent Events)

Best for: Web applications, remote connections

```python
from flask import Flask, Response, request
import json

app = Flask(__name__)

@app.route('/mcp', methods=['POST'])
def handle_mcp_request():
    """Handle MCP over HTTP"""
    message = request.json
    response = server.process(message)
    return json.dumps(response)

@app.route('/mcp/events')
def sse_events():
    """Server-Sent Events for streaming"""
    def event_stream():
        while True:
            message = server.get_next_message()
            yield f"data: {json.dumps(message)}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')
```

### WebSocket

Best for: Real-time, bidirectional communication

```python
import asyncio
import websockets
import json

async def handle_websocket(websocket, path):
    """Handle MCP over WebSocket"""
    async for message in websocket:
        request = json.loads(message)
        response = server.process(request)
        await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_websocket, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
```

## 🔧 Protocol Handler

### Request Routing

```python
class ProtocolHandler:
    def __init__(self, server):
        self.server = server
    
    def handle(self, request):
        """Route request to appropriate handler"""
        method = request.get("method")
        
        handlers = {
            "initialize": self.handle_initialize,
            "tools/list": self.handle_list_tools,
            "tools/call": self.handle_call_tool,
            "resources/read": self.handle_read_resource,
        }
        
        handler = handlers.get(method)
        if not handler:
            return self.error(-32601, f"Method not found: {method}")
        
        return handler(request)
    
    def handle_initialize(self, request):
        """Handle initialization handshake"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                }
            },
            "id": request["id"]
        }
    
    def handle_list_tools(self, request):
        """Return list of available tools"""
        tools = self.server.tool_registry.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": request["id"]
        }
    
    def handle_call_tool(self, request):
        """Execute a tool"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        result = self.server.execution_engine.execute(tool_name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request["id"]
        }
```

## 📋 Tool Registry

### Registering Tools

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name, description, input_schema, handler):
        """Register a new tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler
        }
    
    def list_tools(self):
        """Return tool definitions (without handlers)"""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
    
    def get_handler(self, name):
        """Get the handler function for a tool"""
        tool = self.tools.get(name)
        if tool:
            return tool["handler"]
        return None
```

### Example Tool Registration

```python
registry = ToolRegistry()

# Register Git tools
registry.register(
    name="git_status",
    description="Get current Git status",
    input_schema={"type": "object", "properties": {}},
    handler=lambda: run_git_command("status")
)

registry.register(
    name="git_branch",
    description="List Git branches",
    input_schema={
        "type": "object",
        "properties": {
            "remote": {"type": "boolean"}
        }
    },
    handler=lambda remote=False: run_git_command("branch", "-r" if remote else "-a")
)
```

## ⚙️ Execution Engine

### Tool Execution

```python
class ExecutionEngine:
    def __init__(self, registry, security_layer):
        self.registry = registry
        self.security = security_layer
    
    def execute(self, tool_name, arguments):
        """Execute a tool with full pipeline"""
        
        # 1. Validate tool exists
        handler = self.registry.get_handler(tool_name)
        if not handler:
            return self._error(f"Tool not found: {tool_name}")
        
        # 2. Security check
        try:
            self.security.validate(tool_name, arguments)
        except Exception as e:
            return self._error(str(e))
        
        # 3. Execute with timeout
        try:
            result = self._run_with_timeout(handler, arguments)
            return self._format_result(result)
        except TimeoutError:
            return self._error("Tool execution timed out")
        except Exception as e:
            return self._error(str(e))
    
    def _run_with_timeout(self, handler, arguments, timeout=30):
        """Run handler with timeout protection"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(handler, **arguments)
            return future.result(timeout=timeout)
    
    def _format_result(self, result):
        """Format successful result"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ],
            "isError": False
        }
    
    def _error(self, message):
        """Format error result"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {message}"
                }
            ],
            "isError": True
        }
```

## 🎓 Key Takeaway

**MCP Server = Pipeline of Components**

1. **Transport** - Receives connections (stdio/HTTP/WebSocket)
2. **Protocol Handler** - Routes JSON-RPC requests
3. **Tool Registry** - Manages available tools
4. **Execution Engine** - Runs tools safely
5. **Response Formatter** - Returns standardized responses

Each layer has one job. Together they create a robust, scalable server.

## 🚀 What's Next?

Tomorrow: **Build Minimal MCP Server** - We'll write actual working code!

---

**Remember:** Good architecture means each part does one thing well. Transport handles connections, registry manages tools, engine runs them safely.
