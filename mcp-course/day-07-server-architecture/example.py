#!/usr/bin/env python3
"""
Day 7 Example: Server Architecture
===================================

This shows the internal architecture of an MCP server:
1. Transport Layer - How clients connect
2. Protocol Handler - JSON-RPC routing
3. Tool Registry - Available tools
4. Execution Engine - Running tools
5. Response Formatter - Output formatting
"""

import json

print("=" * 70)
print("MCP SERVER ARCHITECTURE DEMONSTRATION")
print("=" * 70)


# ============================================================
# LAYER 1: TRANSPORT
# ============================================================
class TransportLayer:
    """
    LAYER 1: TRANSPORT
    ==================
    Handles how clients connect to the server.
    Could be stdio, HTTP, WebSocket, etc.
    """
    
    def __init__(self):
        print("  [Layer 1] Transport Layer initialized")
        self.messages = []
    
    def receive(self, message_json):
        """Receive a message from client"""
        print(f"  [Layer 1] 📥 Received: {message_json[:50]}...")
        self.messages.append(json.loads(message_json))
        return json.loads(message_json)
    
    def send(self, response):
        """Send a response to client"""
        response_json = json.dumps(response)
        print(f"  [Layer 1] 📤 Sending: {response_json[:50]}...")
        return response_json


# ============================================================
# LAYER 2: PROTOCOL HANDLER
# ============================================================
class ProtocolHandler:
    """
    LAYER 2: PROTOCOL HANDLER
    =========================
    Routes JSON-RPC requests to the right handler.
    """
    
    def __init__(self, server):
        print("  [Layer 2] Protocol Handler initialized")
        self.server = server
    
    def handle(self, request):
        """Route request to appropriate handler"""
        method = request.get("method")
        request_id = request.get("id")
        
        print(f"  [Layer 2] 🔄 Routing method: {method}")
        
        # Route to appropriate handler
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.server.tool_registry.list_tools(request_id)
        elif method == "tools/call":
            params = request.get("params", {})
            return self.server.execution_engine.execute(request_id, params)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            }
    
    def handle_initialize(self, request_id):
        """Handle initialization request"""
        print("  [Layer 2] 🤝 Handling initialize")
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}}
            },
            "id": request_id
        }


# ============================================================
# LAYER 3: TOOL REGISTRY
# ============================================================
class ToolRegistry:
    """
    LAYER 3: TOOL REGISTRY
    ======================
    Manages available tools and their definitions.
    """
    
    def __init__(self):
        print("  [Layer 3] Tool Registry initialized")
        self.tools = {}
    
    def register(self, name, description, handler, input_schema=None):
        """Register a new tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": input_schema or {"type": "object"}
        }
        print(f"  [Layer 3] 📝 Registered tool: {name}")
    
    def list_tools(self, request_id):
        """Return list of available tools"""
        print(f"  [Layer 3] 📋 Listing {len(self.tools)} tools")
        tools_list = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": request_id
        }
    
    def get_handler(self, name):
        """Get the handler function for a tool"""
        tool = self.tools.get(name)
        return tool["handler"] if tool else None


# ============================================================
# LAYER 4: EXECUTION ENGINE
# ============================================================
class ExecutionEngine:
    """
    LAYER 4: EXECUTION ENGINE
    =========================
    Executes tools safely and handles errors.
    """
    
    def __init__(self, registry):
        print("  [Layer 4] Execution Engine initialized")
        self.registry = registry
    
    def execute(self, request_id, params):
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        print(f"  [Layer 4] ⚙️  Executing tool: {tool_name}")
        
        # Get tool handler
        handler = self.registry.get_handler(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": f"Tool not found: {tool_name}"},
                "id": request_id
            }
        
        # Execute with error handling
        try:
            result = handler(**arguments)
            print(f"  [Layer 4] ✅ Execution successful")
            
            # Pass to formatter
            return self.format_result(result, request_id)
            
        except Exception as e:
            print(f"  [Layer 4] ❌ Execution failed: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id
            }
    
    def format_result(self, result, request_id):
        """Format successful result"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False
            },
            "id": request_id
        }


# ============================================================
# COMPLETE SERVER
# ============================================================
class MCPServer:
    """
    COMPLETE MCP SERVER
    ===================
    Combines all layers into a working server.
    """
    
    def __init__(self):
        print("\n🏗️  Building MCP Server...")
        print("=" * 50)
        
        # Initialize layers
        self.transport = TransportLayer()
        self.tool_registry = ToolRegistry()
        self.execution_engine = ExecutionEngine(self.tool_registry)
        self.protocol_handler = ProtocolHandler(self)
        
        print("=" * 50)
        print("✅ Server ready!\n")
    
    def register_tool(self, name, description, handler):
        """Register a tool"""
        self.tool_registry.register(name, description, handler)
    
    def process(self, message_json):
        """Process a request through all layers"""
        print("\n📨 Processing Request:")
        print("-" * 50)
        
        # Layer 1: Transport (receive)
        request = self.transport.receive(message_json)
        
        # Layer 2: Protocol Handler (route)
        response = self.protocol_handler.handle(request)
        
        # Layer 1: Transport (send)
        return self.transport.send(response)


# ============================================================
# DEMONSTRATION
# ============================================================
print("\n" + "=" * 70)
print("BUILDING THE SERVER")
print("=" * 70)

# Create server
server = MCPServer()

# Register some tools
print("\n🛠️  Registering Tools:")
server.register_tool("hello", "Say hello", lambda name: f"Hello, {name}!")
server.register_tool("add", "Add two numbers", lambda a, b: a + b)
server.register_tool("status", "Get status", lambda: "All systems operational")


# ============================================================
# PROCESS REQUESTS
# ============================================================
print("\n" + "=" * 70)
print("PROCESSING REQUESTS")
print("=" * 70)

# Request 1: Initialize
print("\n1️⃣  Initialize Request:")
req1 = json.dumps({
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": "init_1"
})
resp1 = server.process(req1)

# Request 2: List Tools
print("\n2️⃣  List Tools Request:")
req2 = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": "list_1"
})
resp2 = server.process(req2)

# Request 3: Call Tool
print("\n3️⃣  Call Tool Request:")
req3 = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "hello",
        "arguments": {"name": "World"}
    },
    "id": "call_1"
})
resp3 = server.process(req3)

# Request 4: Call Another Tool
print("\n4️⃣  Call Add Tool:")
req4 = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "add",
        "arguments": {"a": 10, "b": 20}
    },
    "id": "call_2"
})
resp4 = server.process(req4)

# Request 5: Unknown Tool
print("\n5️⃣  Unknown Tool Request:")
req5 = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "nonexistent",
        "arguments": {}
    },
    "id": "call_3"
})
resp5 = server.process(req5)


# ============================================================
# ARCHITECTURE SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SERVER ARCHITECTURE SUMMARY")
print("=" * 70)
print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP SERVER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: TRANSPORT                                          │   │
│  │  • Receives JSON-RPC requests                                │   │
│  │  • Sends JSON-RPC responses                                  │   │
│  │  • Handles connection (stdio/HTTP/WebSocket)                 │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐   │
│  │  LAYER 2: PROTOCOL HANDLER                                   │   │
│  │  • Parses JSON-RPC                                           │   │
│  │  • Routes to correct handler                                 │   │
│  │  • Manages request IDs                                       │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐   │
│  │  LAYER 3: TOOL REGISTRY                                      │   │
│  │  • Stores tool definitions                                   │   │
│  │  • Lists available tools                                     │   │
│  │  • Provides tool handlers                                    │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐   │
│  │  LAYER 4: EXECUTION ENGINE                                   │   │
│  │  • Validates inputs                                          │   │
│  │  • Executes tool handlers                                    │   │
│  │  • Handles errors                                            │   │
│  │  • Formats results                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Each layer has ONE job:
• Transport: Move messages
• Protocol: Route requests
• Registry: Manage tools
• Engine: Execute safely

This separation makes the server:
✅ Maintainable - Each layer is independent
✅ Testable - Test layers separately
✅ Extensible - Add new layers easily
""")

print("=" * 70)
