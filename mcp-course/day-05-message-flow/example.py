#!/usr/bin/env python3
"""
Day 5 Example: Message Flow
===========================

This shows exactly how messages flow between
MCP Client and MCP Server using JSON-RPC.
"""

import json

print("=" * 70)
print("MCP MESSAGE FLOW DEMONSTRATION")
print("=" * 70)

print("""
MCP uses JSON-RPC 2.0 for all communication.

JSON-RPC Format:
{
  "jsonrpc": "2.0",
  "method": "what_to_do",
  "params": { ... },
  "id": "unique_id"
}
""")


# ============================================================
# STEP 1: Client Lists Tools
# ============================================================
print("\n" + "=" * 70)
print("STEP 1: Client Discovers Available Tools")
print("=" * 70)

request_1 = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": "req_001"
}

print("\n📤 CLIENT SENDS:")
print(json.dumps(request_1, indent=2))

response_1 = {
    "jsonrpc": "2.0",
    "result": {
        "tools": [
            {
                "name": "calculate",
                "description": "Calculate expression",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    }
                }
            },
            {
                "name": "get_time",
                "description": "Get current time",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    },
    "id": "req_001"
}

print("\n📥 SERVER RESPONDS:")
print(json.dumps(response_1, indent=2))

print("\n✅ Client now knows what tools are available!")


# ============================================================
# STEP 2: Client Calls a Tool
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: Client Calls a Tool")
print("=" * 70)

request_2 = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "calculate",
        "arguments": {
            "expression": "2 + 3 * 4"
        }
    },
    "id": "req_002"
}

print("\n📤 CLIENT SENDS:")
print(json.dumps(request_2, indent=2))

print("\n⚙️  SERVER processes the request:")
print("   1. Parses JSON-RPC")
print("   2. Validates method: 'tools/call'")
print("   3. Extracts tool name: 'calculate'")
print("   4. Extracts arguments: {'expression': '2 + 3 * 4'}")
print("   5. Executes the tool")
print("   6. Formats result")

response_2 = {
    "jsonrpc": "2.0",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "14"
            }
        ],
        "isError": False
    },
    "id": "req_002"
}

print("\n📥 SERVER RESPONDS:")
print(json.dumps(response_2, indent=2))

print("\n✅ Client receives the result!")


# ============================================================
# STEP 3: Error Handling
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: Error Handling")
print("=" * 70)

request_3 = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "unknown_tool",
        "arguments": {}
    },
    "id": "req_003"
}

print("\n📤 CLIENT SENDS (calling unknown tool):")
print(json.dumps(request_3, indent=2))

error_response = {
    "jsonrpc": "2.0",
    "error": {
        "code": -32602,
        "message": "Tool not found: unknown_tool"
    },
    "id": "req_003"
}

print("\n📥 SERVER RESPONDS (with error):")
print(json.dumps(error_response, indent=2))

print("\n✅ Client knows the request failed and why!")


# ============================================================
# COMPLETE FLOW VISUALIZATION
# ============================================================
print("\n" + "=" * 70)
print("COMPLETE MESSAGE FLOW")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│                      MESSAGE FLOW DIAGRAM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   CLIENT                          SERVER                             │
│     │                                │                               │
│     ├─1. tools/list───────────────►│                               │
│     │     {method: "tools/list"}     │                               │
│     │                                │                               │
│     │◄─────────────────────────────2.│                               │
│     │     {result: {tools: [...]}}   │                               │
│     │                                │                               │
│     ├─3. tools/call───────────────►│                               │
│     │     {method: "tools/call",     │                               │
│     │      params: {name: "calc"}}   │                               │
│     │                                │                               │
│     │◄─────────────────────────────4.│                               │
│     │     {result: {content: [...]}} │                               │
│     │                                │                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Key Points:
• Each request has a unique ID
• Response ID matches request ID
• Same format for success and errors
• All communication is stateless
""")


# ============================================================
# JSON-RPC ERROR CODES
# ============================================================
print("\n" + "=" * 70)
print("JSON-RPC ERROR CODES")
print("=" * 70)

error_codes = {
    -32700: "Parse Error - Invalid JSON",
    -32600: "Invalid Request - Not a valid request object",
    -32601: "Method Not Found - Method doesn't exist",
    -32602: "Invalid Params - Wrong parameters",
    -32603: "Internal Error - Server error",
}

for code, description in error_codes.items():
    print(f"  {code}: {description}")


# ============================================================
# PRACTICAL EXAMPLE
# ============================================================
print("\n" + "=" * 70)
print("PRACTICAL EXAMPLE: Calculator Tool")
print("=" * 70)

class SimpleMCPServer:
    """Simple server to demonstrate message flow"""
    
    def __init__(self):
        self.tools = {
            "add": lambda a, b: a + b,
            "multiply": lambda a, b: a * b
        }
    
    def handle(self, request_json):
        """Handle a JSON-RPC request"""
        request = json.loads(request_json)
        method = request.get("method")
        req_id = request.get("id")
        
        if method == "tools/list":
            result = {
                "tools": [
                    {"name": "add", "description": "Add two numbers"},
                    {"name": "multiply", "description": "Multiply two numbers"}
                ]
            }
            return json.dumps({"jsonrpc": "2.0", "result": result, "id": req_id})
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            if tool_name in self.tools:
                result = self.tools[tool_name](**args)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(result)}], "isError": False},
                    "id": req_id
                })
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": f"Tool not found: {tool_name}"},
                    "id": req_id
                })


# Run the example
server = SimpleMCPServer()

print("\n1. Client requests tool list:")
req = json.dumps({"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": "1"})
print(f"   Request:  {req}")
resp = server.handle(req)
print(f"   Response: {resp}")

print("\n2. Client calls 'add' tool:")
req = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "add", "arguments": {"a": 5, "b": 3}},
    "id": "2"
})
print(f"   Request:  {req}")
resp = server.handle(req)
print(f"   Response: {resp}")

print("\n3. Client calls unknown tool:")
req = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "divide", "arguments": {}},
    "id": "3"
})
print(f"   Request:  {req}")
resp = server.handle(req)
print(f"   Response: {resp}")


print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
✅ MCP uses JSON-RPC 2.0 for all messages
✅ Request has: jsonrpc, method, params, id
✅ Response has: jsonrpc, result OR error, id
✅ ID links request to response
✅ Same format works for all tools

This standardization is what makes MCP powerful!
""")

print("=" * 70)
