# Day 5: Message Flow

## 🎯 What We're Learning

When an MCP client asks a server to do something, what actually happens? Let's trace every message, every step.

## 🔄 The Complete Message Flow

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│              MESSAGE FLOW OVERVIEW                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Client DISCOVERS what server can do               │
│     Client → Server: "What tools do you have?"        │
│     Server → Client: "I have tools A, B, C"           │
│                                                         │
│  2. Client CALLS a tool                               │
│     Client → Server: "Run tool A with params"         │
│     Server → Client: "Here's the result"              │
│                                                         │
│  3. Client ACCESSES resources                         │
│     Client → Server: "Give me resource X"             │
│     Server → Client: "Here's the data"                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📨 Message Format (JSON-RPC)

MCP uses **JSON-RPC 2.0** for all communication.

### JSON-RPC Structure

```json
{
  "jsonrpc": "2.0",
  "method": "what_to_do",
  "params": { /* parameters */ },
  "id": "unique_request_id"
}
```

### Fields Explained

| Field | Meaning | Example |
|-------|---------|---------|
| `jsonrpc` | Protocol version (always "2.0") | `"2.0"` |
| `method` | What operation to perform | `"tools/call"` |
| `params` | Data for that operation | `{"name": "git_branch"}` |
| `id` | Unique ID to match request/response | `"req_123"` |

## 🔍 Detailed Message Flow

### Step 1: Client Connects to Server

```
┌──────────────┐                  ┌──────────────┐
│  MCP Client  │                  │  MCP Server  │
└──────┬───────┘                  └──────┬───────┘
       │                                 │
       ├─────── OPEN CONNECTION ────────→│
       │     (TCP/WebSocket/stdio)       │
       │                                 │
       │← INITIALIZATION COMPLETE ───────┤
       │                                 │
```

### Step 2: Client Lists Available Tools

**Client Sends:**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": "tools_list_1"
}
```

**Server Responds:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "list_branches",
        "description": "List all Git branches",
        "inputSchema": {
          "type": "object",
          "properties": {
            "remote": {"type": "boolean"}
          }
        }
      },
      {
        "name": "create_branch",
        "description": "Create a new branch",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"}
          },
          "required": ["name"]
        }
      }
    ]
  },
  "id": "tools_list_1"
}
```

### Step 3: Client Calls a Tool

**Client Sends:**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_branches",
    "arguments": {
      "remote": true
    }
  },
  "id": "tool_call_1"
}
```

**Breakdown:**
- `method`: "tools/call" means "execute a tool"
- `name`: "list_branches" - which tool to execute
- `arguments`: Parameters to pass to the tool
- `id`: Unique ID for this request

### Step 4: Server Executes the Tool

Inside the server, this happens:

```python
# Server receives request
request = parse_json_rpc(incoming_message)

# Validate request
if request['method'] != 'tools/call':
    raise InvalidMethod()

# Get the tool
tool_name = request['params']['name']  # "list_branches"
tool = server.tools[tool_name]

# Execute it
result = tool(**request['params']['arguments'])
```

### Step 5: Server Responds with Result

**Server Sends:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "main\nfeature/auth\nfeature/api\nhotfix/bug-123"
      }
    ],
    "isError": false
  },
  "id": "tool_call_1"
}
```

**Response Fields:**
- `result.content`: The actual data (could be text, image, resource, etc.)
- `result.isError`: Whether execution failed
- `id`: Matches the request ID so client knows which request this answers

### Step 6: Client Processes Response

```python
# Client receives response
response = parse_json_rpc(incoming_message)

# Match to request
request_id = response['id']  # "tool_call_1"
original_request = pending_requests[request_id]

# Check for errors
if response.get('error'):
    print(f"Error: {response['error']['message']}")
else:
    # Process result
    result = response['result']
    print(f"Success: {result}")
```

## 🎯 Complete Example Walkthrough

### Scenario: Agent gets Git branches

### Message 1: Discovery Request

```json
→ CLIENT TO SERVER:
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": "discover_1"
}

← SERVER TO CLIENT:
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "list_branches",
        "description": "List all branches",
        "inputSchema": {
          "type": "object",
          "properties": {
            "remote": {"type": "boolean"}
          }
        }
      }
    ]
  },
  "id": "discover_1"
}
```

### Message 2: Tool Execution Request

```json
→ CLIENT TO SERVER:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_branches",
    "arguments": {
      "remote": false
    }
  },
  "id": "exec_1"
}

← SERVER TO CLIENT:
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "main\ndev\nfeature/new-dashboard"
      }
    ],
    "isError": false
  },
  "id": "exec_1"
}
```

## 📊 Message Diagram

```
TIME ┐
     │
     │  CLIENT                      SERVER
     │
  1  │  ┌─ tools/list request ──────────→
     │  │
  2  │  ├← tools list response ─────────┐
     │  │                                │
  3  │  ├─ tools/call request ──────────→
     │  │   (name: list_branches)        │
     │  │
  4  │  ├← tool result response ────────┐
     │  │   (branches: [...])            │
     │
```

## 🔄 Full Python Implementation

### Client Side

```python
import json

class MCPClient:
    def __init__(self, server_connection):
        self.conn = server_connection
        self.request_counter = 0
    
    def list_tools(self):
        """Discover available tools"""
        request_id = f"req_{self.request_counter}"
        self.request_counter += 1
        
        # Send request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": request_id
        }
        self.conn.send(json.dumps(request))
        
        # Wait for response
        response = json.loads(self.conn.receive())
        
        if response.get('error'):
            raise Exception(f"Error: {response['error']['message']}")
        
        return response['result']['tools']
    
    def call_tool(self, tool_name, arguments):
        """Execute a tool"""
        request_id = f"req_{self.request_counter}"
        self.request_counter += 1
        
        # Send request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": request_id
        }
        self.conn.send(json.dumps(request))
        
        # Wait for response
        response = json.loads(self.conn.receive())
        
        if response.get('error'):
            raise Exception(f"Error: {response['error']['message']}")
        
        return response['result']
```

### Server Side

```python
import json

class MCPServer:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name, description, func, input_schema):
        """Register a tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "function": func,
            "inputSchema": input_schema
        }
    
    def handle_request(self, request_str):
        """Handle an incoming JSON-RPC request"""
        request = json.loads(request_str)
        
        try:
            method = request['method']
            params = request.get('params', {})
            request_id = request['id']
            
            if method == 'tools/list':
                result = self._handle_list_tools()
            elif method == 'tools/call':
                result = self._handle_call_tool(params)
            else:
                raise Exception(f"Unknown method: {method}")
            
            # Return success response
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        
        except Exception as e:
            # Return error response
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id
            }
        
        return json.dumps(response)
    
    def _handle_list_tools(self):
        """Return list of available tools"""
        tools_list = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
        return {"tools": tools_list}
    
    def _handle_call_tool(self, params):
        """Execute a tool"""
        tool_name = params['name']
        arguments = params.get('arguments', {})
        
        if tool_name not in self.tools:
            raise Exception(f"Tool not found: {tool_name}")
        
        tool_def = self.tools[tool_name]
        result = tool_def['function'](**arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ],
            "isError": False
        }
```

## 🔀 Resource Request Flow

### Similar to Tools

**Client Requests:**

```json
→ CLIENT TO SERVER:
{
  "jsonrpc": "2.0",
  "method": "resources/read",
  "params": {
    "uri": "git://config/settings.json"
  },
  "id": "resource_1"
}

← SERVER TO CLIENT:
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"autoCommit\": true}"
      }
    ]
  },
  "id": "resource_1"
}
```

## 📋 Error Handling

### Success Response

```json
{
  "jsonrpc": "2.0",
  "result": { /* data */ },
  "id": "req_1"
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  },
  "id": "req_1"
}
```

**Error Codes:**
- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32603`: Internal error
- `1-999`: Custom errors

## 🎓 Key Takeaway

**All MCP communication follows this pattern:**

1. **Client sends JSON-RPC request** with method and parameters
2. **Server processes request** and executes the method
3. **Server sends JSON-RPC response** with result or error
4. **Client processes response** and presents to application

Everything is **stateless**, **standardized**, and **traceable** (via request IDs).

## 🚀 What's Next?

Tomorrow: **Security & Isolation** - How does MCP keep agents from doing dangerous things?

---

**Remember:** JSON-RPC is the universal language. Request has ID, response matches ID. Simple. Elegant. Standardized.
