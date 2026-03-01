#!/usr/bin/env python3
"""
Day 3 Example: MCP Tool Calling
===============================

This shows how MCP standardizes tool access.
More setup initially, but scales beautifully.
"""

print("=" * 60)
print("MCP TOOL CALLING EXAMPLE")
print("=" * 60)

# MCP Client (simplified)
class MCPClient:
    """Universal client that talks to any MCP server"""
    
    def __init__(self):
        print("  [MCP Client] Initializing...")
        # One client connects to all tools through MCP
        self.connected_tools = ["git", "aws", "slack"]
    
    def call_tool(self, tool_name, operation, params=None):
        """Universal method to call any tool"""
        if params is None:
            params = {}
        
        # In real MCP, this sends JSON-RPC to the server
        # Here we simulate the response
        responses = {
            ("git", "get_branches"): ["main", "dev", "feature-x"],
            ("git", "create_branch"): f"Created branch: {params.get('name')}",
            ("aws", "list_instances"): ["i-12345", "i-67890"],
            ("aws", "start_instance"): f"Started: {params.get('id')}",
            ("slack", "send_message"): f"Sent to #{params.get('channel')}: {params.get('text')}",
        }
        
        return responses.get((tool_name, operation), "Unknown operation")


# Agent using MCP
class DevOpsAgent:
    """Agent using MCP protocol"""
    
    def __init__(self):
        print("  [Agent] Connecting via MCP...")
        # One connection to rule them all
        self.mcp = MCPClient()
    
    def deploy(self):
        print("\n  [Agent] Deploying via MCP...")
        
        # All calls go through MCP - same interface!
        branches = self.mcp.call_tool("git", "get_branches")
        print(f"    Git branches: {branches}")
        
        instances = self.mcp.call_tool("aws", "list_instances")
        print(f"    AWS instances: {instances}")
        
        self.mcp.call_tool("slack", "send_message", {
            "channel": "deployments",
            "text": "Deployment started"
        })
        print(f"    Slack notification sent")
        
        return "Deployment complete!"


print("\n📋 PROS OF MCP:")
print("  ✅ One client for all tools")
print("  ✅ Same interface for everything")
print("  ✅ Easy to add new agents")
print("  ✅ Centralized authentication")
print("  ✅ Standardized errors")

print("\n📋 CONS OF MCP:")
print("  ⚠️  More initial setup")
print("  ⚠️  Extra layer (small latency)")
print("  ⚠️  Need to learn MCP concepts")

print("\n" + "=" * 60)
print("RUNNING THE AGENT:")
print("=" * 60)

agent = DevOpsAgent()
result = agent.deploy()
print(f"\n  Result: {result}")

print("\n" + "=" * 60)
print("THE BENEFIT:")
print("=" * 60)
print("""
With MCP, adding a new agent is trivial:

  DevOps Agent  → MCP → Git, AWS, Slack
  Support Agent → MCP → Git, AWS, Slack  (same servers!)
  Analyst Agent → MCP → Git, AWS, Slack  (same servers!)

  Total: 3 MCP servers (not 9 integrations!)
  
New agent? Just create MCP client!
New tool? Just create MCP server!
No duplication, no chaos!
""")

print("\n📊 COMPARISON:")
print("-" * 60)
print("  Direct Calling: 9 custom integrations")
print("  MCP:            3 shared servers")
print("  Savings:        67% less code!")

print("\n" + "=" * 60)
