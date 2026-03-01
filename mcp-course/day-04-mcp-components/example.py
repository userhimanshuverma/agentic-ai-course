#!/usr/bin/env python3
"""
Day 4 Example: MCP Components
=============================

This shows the 4 main components of MCP:
1. MCP Client - makes requests
2. MCP Server - fulfills requests  
3. Tools - actions the server can do
4. Resources - data the server can share
"""

print("=" * 60)
print("MCP COMPONENTS EXAMPLE")
print("=" * 60)

# ============================================================
# COMPONENT 1: MCP CLIENT
# ============================================================
class MCPClient:
    """
    MCP CLIENT
    ==========
    - Makes requests to MCP servers
    - Discovers available tools
    - Calls tools and receives results
    """
    
    def __init__(self, server):
        self.server = server
        self.tools = []
        print("  [MCP Client] Created")
    
    def connect(self):
        """Connect to server and discover tools"""
        print("  [MCP Client] Connecting to server...")
        self.tools = self.server.list_tools()
        print(f"  [MCP Client] Discovered {len(self.tools)} tools")
        return self.tools
    
    def call_tool(self, tool_name, **kwargs):
        """Call a tool on the server"""
        print(f"  [MCP Client] Calling tool: {tool_name}")
        result = self.server.execute_tool(tool_name, kwargs)
        return result
    
    def read_resource(self, resource_uri):
        """Read a resource from the server"""
        print(f"  [MCP Client] Reading resource: {resource_uri}")
        return self.server.get_resource(resource_uri)


# ============================================================
# COMPONENT 2: MCP SERVER
# ============================================================
class MCPServer:
    """
    MCP SERVER
    ==========
    - Hosts tools and resources
    - Listens for client requests
    - Executes tools and returns results
    """
    
    def __init__(self, name):
        self.name = name
        self.tools = {}      # Tool registry
        self.resources = {}  # Resource registry
        print(f"  [MCP Server '{name}'] Created")
    
    def register_tool(self, name, description, handler):
        """Register a tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
        print(f"  [MCP Server] Registered tool: {name}")
    
    def register_resource(self, uri, content):
        """Register a resource"""
        self.resources[uri] = content
        print(f"  [MCP Server] Registered resource: {uri}")
    
    def list_tools(self):
        """Return list of available tools"""
        return [{"name": t["name"], "description": t["description"]} 
                for t in self.tools.values()]
    
    def execute_tool(self, tool_name, params):
        """Execute a tool"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools[tool_name]
        result = tool["handler"](**params)
        return result
    
    def get_resource(self, uri):
        """Get a resource"""
        return self.resources.get(uri, "Resource not found")


# ============================================================
# COMPONENT 3: TOOLS (Actions)
# ============================================================
print("\n" + "-" * 60)
print("COMPONENT 3: TOOLS (Actions)")
print("-" * 60)

# Tool implementations
def git_status():
    """TOOL: Check git status"""
    return {"branch": "main", "status": "clean", "commits_ahead": 0}

def git_commit(message):
    """TOOL: Commit changes"""
    return {"success": True, "commit_id": "abc123", "message": message}

def list_files(directory="."):
    """TOOL: List files"""
    return {"files": ["README.md", "main.py", "config.yaml"], "directory": directory}

print("  Tools are ACTIONS the server can perform:")
print("    • git_status() - Check repository status")
print("    • git_commit(message) - Commit changes")
print("    • list_files(directory) - List directory contents")


# ============================================================
# COMPONENT 4: RESOURCES (Data)
# ============================================================
print("\n" + "-" * 60)
print("COMPONENT 4: RESOURCES (Read-Only Data)")
print("-" * 60)

print("  Resources are DATA the server can share:")
print("    • config://app.yaml - Configuration file")
print("    • docs://README.md - Documentation")
print("    • logs://error.log - Log files")


# ============================================================
# PUTTING IT ALL TOGETHER
# ============================================================
print("\n" + "=" * 60)
print("DEMONSTRATION: All Components Working Together")
print("=" * 60)

# 1. Create Server
server = MCPServer("GitServer")

# 2. Register Tools (Component 3)
server.register_tool("status", "Check git status", git_status)
server.register_tool("commit", "Commit changes", git_commit)
server.register_tool("list_files", "List files", list_files)

# 3. Register Resources (Component 4)
server.register_resource("config://app.yaml", "database_url: localhost")
server.register_resource("docs://README.md", "# My Project\nThis is a demo.")

# 4. Create Client (Component 1)
client = MCPClient(server)

# 5. Connect and Discover
tools = client.connect()
print(f"\n  Available Tools:")
for tool in tools:
    print(f"    • {tool['name']}: {tool['description']}")

# 6. Call Tools
print(f"\n  Calling Tools:")
result = client.call_tool("status")
print(f"    git_status() → {result}")

result = client.call_tool("commit", message="Fix bug")
print(f"    git_commit() → {result}")

result = client.call_tool("list_files", directory="src")
print(f"    list_files() → {result}")

# 7. Read Resources
print(f"\n  Reading Resources:")
config = client.read_resource("config://app.yaml")
print(f"    config://app.yaml → {config}")

docs = client.read_resource("docs://README.md")
print(f"    docs://README.md → {docs[:30]}...")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("COMPONENT SUMMARY")
print("=" * 60)
print("""
┌─────────────────────────────────────────────────────────┐
│                    MCP SYSTEM                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ MCP CLIENT   │◄───────►│ MCP SERVER   │             │
│  │              │         │              │             │
│  │ • Connects   │         │ • Hosts      │             │
│  │ • Discovers  │         │ • Listens    │             │
│  │ • Calls      │         │ • Executes   │             │
│  └──────────────┘         └───────┬──────┘             │
│                                   │                     │
│                         ┌─────────▼────────┐           │
│                         │                  │           │
│                         │  TOOLS           │           │
│                         │  (Actions)       │           │
│                         │                  │           │
│                         │  • git_status    │           │
│                         │  • git_commit    │           │
│                         │  • list_files    │           │
│                         │                  │           │
│                         │  RESOURCES       │           │
│                         │  (Read-Only)     │           │
│                         │                  │           │
│                         │  • config files  │           │
│                         │  • docs          │           │
│                         │  • logs          │           │
│                         │                  │           │
│                         └──────────────────┘           │
│                                                          │
└─────────────────────────────────────────────────────────┘

Key Points:
• CLIENT asks for things
• SERVER provides things
• TOOLS do actions
• RESOURCES provide data
""")

print("=" * 60)
