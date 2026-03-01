# Day 11: Multi-Agent Architecture

## 🎯 The Problem

You have multiple AI agents that need to share tools:
- **DevOps Agent** - manages infrastructure
- **Support Agent** - handles tickets
- **Analyst Agent** - analyzes data

**Without MCP:** Each agent writes custom integrations.  
**With MCP:** One server serves all agents.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MULTI-AGENT MCP ARCHITECTURE               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   DevOps Agent         Support Agent      Analyst Agent │
│        │                    │                   │       │
│        └────────────────────┼───────────────────┘       │
│                             │                          │
│                    ┌────────┴────────┐                 │
│                    │   MCP Server    │                 │
│                    │  (Shared)       │                 │
│                    └────────┬────────┘                 │
│                             │                          │
│         ┌───────────────────┼───────────────────┐      │
│         │                   │                   │      │
│    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐  │
│    │  Git    │        │  Jira   │        │   SQL   │  │
│    │  AWS    │        │  Slack  │        │  Excel  │  │
│    │ Docker  │        │  Email  │        │  API    │  │
│    └─────────┘        └─────────┘        └─────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
day-11-multi-agent-architecture/
├── README.md
├── server.py              # Shared MCP server
├── agents/
│   ├── __init__.py
│   ├── devops_agent.py
│   ├── support_agent.py
│   └── analyst_agent.py
└── main.py                # Demo all agents
```

## 🔧 Step 1: Create the Shared Server

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Multi-Agent MCP Server
======================

One server serving multiple agents with different permissions.
"""

import json
import sys
from typing import Dict, Any


class MultiAgentMCPServer:
    """MCP server with agent-specific permissions"""
    
    def __init__(self):
        self.tools = {}
        self.permissions = {
            "devops": ["git_*", "aws_*", "docker_*", "deploy_*"],
            "support": ["jira_*", "slack_*", "email_*", "ticket_*"],
            "analyst": ["sql_*", "chart_*", "report_*", "query_*"]
        }
    
    def register_tool(self, name: str, description: str, handler, category: str):
        """Register a tool with category for permissions"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "category": category
        }
    
    def run(self):
        """Main server loop"""
        print(f"Multi-Agent Server: {len(self.tools)} tools", file=sys.stderr)
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                self.send_error(None, -32603, str(e))
    
    def handle_request(self, request: Dict) -> Dict:
        method = request.get("method")
        request_id = request.get("id")
        
        # Get agent type from request context (simplified)
        agent_type = request.get("params", {}).get("_agent_type", "unknown")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id, agent_type)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, agent_type, request.get("params", {}))
        else:
            return self.send_error(request_id, -32601, f"Method not found: {method}")
    
    def handle_initialize(self, request_id) -> Dict:
        return {
            "jsonrpc": "2.0",
            "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}},
            "id": request_id
        }
    
    def handle_list_tools(self, request_id, agent_type: str) -> Dict:
        """Return only tools this agent can use"""
        allowed_patterns = self.permissions.get(agent_type, [])
        
        tools_list = []
        for tool in self.tools.values():
            if self._is_allowed(tool["name"], allowed_patterns):
                tools_list.append({
                    "name": tool["name"],
                    "description": tool["description"]
                })
        
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": request_id
        }
    
    def handle_call_tool(self, request_id: str, agent_type: str, params: Dict) -> Dict:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Check permission
        allowed_patterns = self.permissions.get(agent_type, [])
        if not self._is_allowed(tool_name, allowed_patterns):
            return self.send_error(request_id, 403, f"Agent '{agent_type}' cannot use '{tool_name}'")
        
        if tool_name not in self.tools:
            return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
        
        try:
            handler = self.tools[tool_name]["handler"]
            result = handler(**arguments)
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": str(result)}], "isError": False},
                "id": request_id
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True},
                "id": request_id
            }
    
    def _is_allowed(self, tool_name: str, patterns: list) -> bool:
        for pattern in patterns:
            if pattern.endswith("*"):
                if tool_name.startswith(pattern[:-1]):
                    return True
            elif tool_name == pattern:
                return True
        return False
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}


# Tool implementations
def git_status():
    return {"status": "clean", "branch": "main"}

def git_push(branch: str):
    return f"Pushed to {branch}"

def aws_list_instances():
    return ["i-12345", "i-67890"]

def docker_ps():
    return [{"name": "web", "status": "running"}]

def jira_create_ticket(title: str, description: str):
    return {"ticket_id": "TICKET-123", "title": title}

def slack_send_message(channel: str, message: str):
    return f"Sent to #{channel}: {message}"

def email_send(to: str, subject: str, body: str):
    return f"Email sent to {to}"

def sql_query(query: str):
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

def chart_generate(data: list, type: str = "bar"):
    return f"Generated {type} chart with {len(data)} items"


if __name__ == "__main__":
    server = MultiAgentMCPServer()
    
    # DevOps tools
    server.register_tool("git_status", "Check git status", git_status, "devops")
    server.register_tool("git_push", "Push to branch", git_push, "devops")
    server.register_tool("aws_list_instances", "List EC2 instances", aws_list_instances, "devops")
    server.register_tool("docker_ps", "List containers", docker_ps, "devops")
    
    # Support tools
    server.register_tool("jira_create_ticket", "Create Jira ticket", jira_create_ticket, "support")
    server.register_tool("slack_send_message", "Send Slack message", slack_send_message, "support")
    server.register_tool("email_send", "Send email", email_send, "support")
    
    # Analyst tools
    server.register_tool("sql_query", "Execute SQL query", sql_query, "analyst")
    server.register_tool("chart_generate", "Generate chart", chart_generate, "analyst")
    
    server.run()
```

## 🔧 Step 2: Create Agent Classes

Create `agents/__init__.py`:

```python
"""Multi-agent system"""

from .devops_agent import DevOpsAgent
from .support_agent import SupportAgent
from .analyst_agent import AnalystAgent

__all__ = ["DevOpsAgent", "SupportAgent", "AnalystAgent"]
```

Create `agents/devops_agent.py`:

```python
"""DevOps Agent - manages infrastructure"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))

from client import MCPClient


class DevOpsAgent:
    """Agent for DevOps tasks"""
    
    def __init__(self, server_command):
        self.client = MCPClient(server_command)
        self.agent_type = "devops"
    
    def connect(self):
        self.client.connect()
        print(f"\n[DevOps Agent] Connected!")
        print(f"Available tools: {[t['name'] for t in self.client.list_tools()]}")
    
    def deploy_application(self, branch: str = "main"):
        """Deploy application to production"""
        print(f"\n[DevOps Agent] Deploying from {branch}...")
        
        # Check git status
        status = self.client.call_tool("git_status", {})
        print(f"  Git status: {status}")
        
        # Push changes
        result = self.client.call_tool("git_push", {"branch": branch})
        print(f"  {result}")
        
        # List instances
        instances = self.client.call_tool("aws_list_instances", {})
        print(f"  Available instances: {instances}")
        
        return "Deployment complete!"
    
    def check_infrastructure(self):
        """Check infrastructure status"""
        print(f"\n[DevOps Agent] Checking infrastructure...")
        
        containers = self.client.call_tool("docker_ps", {})
        print(f"  Running containers: {containers}")
        
        instances = self.client.call_tool("aws_list_instances", {})
        print(f"  EC2 instances: {instances}")
        
        return "Infrastructure check complete!"
    
    def disconnect(self):
        self.client.disconnect()
```

Create `agents/support_agent.py`:

```python
"""Support Agent - handles customer issues"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))

from client import MCPClient


class SupportAgent:
    """Agent for support tasks"""
    
    def __init__(self, server_command):
        self.client = MCPClient(server_command)
        self.agent_type = "support"
    
    def connect(self):
        self.client.connect()
        print(f"\n[Support Agent] Connected!")
        print(f"Available tools: {[t['name'] for t in self.client.list_tools()]}")
    
    def handle_customer_issue(self, customer_email: str, issue: str):
        """Handle a customer support issue"""
        print(f"\n[Support Agent] Handling issue from {customer_email}...")
        
        # Create ticket
        ticket = self.client.call_tool("jira_create_ticket", {
            "title": f"Issue: {issue[:30]}...",
            "description": issue
        })
        print(f"  Created ticket: {ticket}")
        
        # Notify team
        self.client.call_tool("slack_send_message", {
            "channel": "support",
            "message": f"New ticket: {ticket}"
        })
        print(f"  Notified team on Slack")
        
        # Acknowledge customer
        self.client.call_tool("email_send", {
            "to": customer_email,
            "subject": "Ticket Created",
            "body": f"We've created ticket {ticket} for your issue."
        })
        print(f"  Sent acknowledgment email")
        
        return "Issue handled!"
    
    def disconnect(self):
        self.client.disconnect()
```

Create `agents/analyst_agent.py`:

```python
"""Analyst Agent - analyzes data"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))

from client import MCPClient


class AnalystAgent:
    """Agent for data analysis"""
    
    def __init__(self, server_command):
        self.client = MCPClient(server_command)
        self.agent_type = "analyst"
    
    def connect(self):
        self.client.connect()
        print(f"\n[Analyst Agent] Connected!")
        print(f"Available tools: {[t['name'] for t in self.client.list_tools()]}")
    
    def generate_report(self):
        """Generate data analysis report"""
        print(f"\n[Analyst Agent] Generating report...")
        
        # Query data
        data = self.client.call_tool("sql_query", {"query": "SELECT * FROM sales"})
        print(f"  Retrieved {len(data)} records")
        
        # Generate chart
        chart = self.client.call_tool("chart_generate", {
            "data": data,
            "type": "bar"
        })
        print(f"  {chart}")
        
        return "Report generated!"
    
    def disconnect(self):
        self.client.disconnect()
```

## 🧪 Step 3: Create Demo

Create `main.py`:

```python
#!/usr/bin/env python3
"""Multi-Agent Architecture Demo"""

import os
import sys

# Import agents
from agents import DevOpsAgent, SupportAgent, AnalystAgent


def main():
    print("=" * 60)
    print("Multi-Agent MCP Architecture Demo")
    print("=" * 60)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    server_command = ["python", server_path]
    
    # Create agents
    devops = DevOpsAgent(server_command)
    support = SupportAgent(server_command)
    analyst = AnalystAgent(server_command)
    
    try:
        # Connect all agents
        print("\n--- Connecting Agents ---")
        devops.connect()
        support.connect()
        analyst.connect()
        
        # Each agent does its work
        print("\n--- Agents at Work ---")
        
        devops.check_infrastructure()
        devops.deploy_application("main")
        
        support.handle_customer_issue(
            "customer@example.com",
            "Cannot access dashboard after login"
        )
        
        analyst.generate_report()
        
    finally:
        print("\n--- Disconnecting ---")
        devops.disconnect()
        support.disconnect()
        analyst.disconnect()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("\nKey insight: One MCP server serves all agents,")
    print("each with different permissions and capabilities.")


if __name__ == "__main__":
    main()
```

## 🎓 Key Takeaway

**Multi-Agent Benefits:**

1. **One server, many agents** - Shared infrastructure
2. **Agent-specific permissions** - Security boundaries
3. **Specialized capabilities** - Each agent has its tools
4. **Centralized management** - Update tools once, all agents benefit

## 🚀 What's Next?

Tomorrow: **Observability & Logging** - Track what all these agents are doing!

---

**Remember:** MCP enables true multi-agent systems where agents share infrastructure but maintain their own capabilities and permissions.
