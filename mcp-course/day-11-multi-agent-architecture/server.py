#!/usr/bin/env python3
"""
Day 11: Multi-Agent MCP Server
==============================

One server serving multiple agents with different permissions.
- DevOps Agent: Can use git, aws, docker tools
- Support Agent: Can use jira, slack, email tools
- Analyst Agent: Can use sql, chart, report tools
"""

import json
import sys
from typing import Dict, Any


class MultiAgentMCPServer:
    """
    MCP server with agent-specific permissions.
    
    Each agent type can only access certain tools,
    but all connect through the same server.
    """
    
    def __init__(self):
        self.tools = {}
        
        # Define permissions for each agent type
        self.permissions = {
            "devops": ["git_", "aws_", "docker_", "deploy_"],
            "support": ["jira_", "slack_", "email_", "ticket_"],
            "analyst": ["sql_", "chart_", "report_", "query_"]
        }
        
        print("Multi-Agent Server initialized", file=sys.stderr)
    
    def register_tool(self, name: str, description: str, handler, category: str):
        """
        Register a tool with a category for permission control.
        
        Args:
            name: Tool name
            description: What the tool does
            handler: Function to execute
            category: Tool category (devops, support, analyst)
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "category": category
        }
        print(f"Registered tool: {name} (category: {category})", file=sys.stderr)
    
    def run(self):
        """Main server loop."""
        print(f"Server running with {len(self.tools)} tools", file=sys.stderr)
        
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
        """Route request to handler."""
        method = request.get("method")
        request_id = request.get("id")
        
        # Get agent type from request (in real world, from auth token)
        params = request.get("params", {})
        agent_type = params.get("_agent_type", "unknown")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id, agent_type)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, agent_type, params)
        else:
            return self.send_error(request_id, -32601, f"Method not found: {method}")
    
    def handle_initialize(self, request_id) -> Dict:
        return {
            "jsonrpc": "2.0",
            "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}},
            "id": request_id
        }
    
    def handle_list_tools(self, request_id, agent_type: str) -> Dict:
        """Return only tools this agent can use."""
        allowed_prefixes = self.permissions.get(agent_type, [])
        
        tools_list = []
        for tool in self.tools.values():
            if any(tool["name"].startswith(prefix) for prefix in allowed_prefixes):
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
        """Execute a tool with permission check."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Check permission
        allowed_prefixes = self.permissions.get(agent_type, [])
        if not any(tool_name.startswith(prefix) for prefix in allowed_prefixes):
            return self.send_error(
                request_id, 403, 
                f"Agent '{agent_type}' cannot use tool '{tool_name}'"
            )
        
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
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def git_status():
    return {"branch": "main", "status": "clean", "commits_ahead": 0}

def git_push(branch: str):
    return f"Pushed to {branch}"

def aws_list_instances():
    return ["i-12345 (running)", "i-67890 (stopped)"]

def docker_ps():
    return [{"name": "web", "status": "running"}, {"name": "db", "status": "running"}]

def jira_create_ticket(title: str, description: str):
    return {"ticket_id": "TICKET-123", "title": title, "status": "open"}

def slack_send_message(channel: str, message: str):
    return f"Sent to #{channel}: {message}"

def email_send(to: str, subject: str, body: str):
    return f"Email sent to {to} with subject: {subject}"

def sql_query(query: str):
    return [{"id": 1, "name": "Alice", "sales": 1000}, {"id": 2, "name": "Bob", "sales": 2000}]

def chart_generate(data: list, chart_type: str = "bar"):
    return f"Generated {chart_type} chart with {len(data)} data points"


# ============================================================
# MAIN
# ============================================================

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
