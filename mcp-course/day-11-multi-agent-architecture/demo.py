#!/usr/bin/env python3
"""
Day 11: Multi-Agent Architecture Demo
=====================================

Shows how multiple agents share one MCP server
with different permissions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))
from client import MCPClient


class Agent:
    """Base agent class."""
    
    def __init__(self, name, agent_type, server_command):
        self.name = name
        self.agent_type = agent_type
        self.client = MCPClient(server_command)
    
    def connect(self):
        print(f"\n[{self.name}] Connecting...")
        self.client.connect()
        print(f"[{self.name}] Available tools: {[t['name'] for t in self.client.list_tools()]}")
    
    def disconnect(self):
        self.client.disconnect()


class DevOpsAgent(Agent):
    """DevOps Agent - manages infrastructure."""
    
    def __init__(self, server_command):
        super().__init__("DevOps Agent", "devops", server_command)
    
    def deploy(self):
        print(f"\n[{self.name}] Deploying application...")
        status = self.client.call_tool("git_status", {})
        print(f"  Git status: {status}")
        
        result = self.client.call_tool("git_push", {"branch": "main"})
        print(f"  {result}")
        
        instances = self.client.call_tool("aws_list_instances", {})
        print(f"  Available instances: {instances}")
        
        return "Deployment complete!"
    
    def check_health(self):
        print(f"\n[{self.name}] Checking infrastructure health...")
        containers = self.client.call_tool("docker_ps", {})
        print(f"  Running containers: {containers}")
        return "Health check complete!"


class SupportAgent(Agent):
    """Support Agent - handles customer issues."""
    
    def __init__(self, server_command):
        super().__init__("Support Agent", "support", server_command)
    
    def handle_ticket(self, customer: str, issue: str):
        print(f"\n[{self.name}] Handling ticket from {customer}...")
        
        ticket = self.client.call_tool("jira_create_ticket", {
            "title": f"Issue: {issue[:30]}...",
            "description": issue
        })
        print(f"  Created ticket: {ticket}")
        
        # Extract ticket ID from string representation
        import re
        ticket_id_match = re.search(r"'ticket_id': '([^']+)'", ticket)
        ticket_id = ticket_id_match.group(1) if ticket_id_match else "UNKNOWN"
        
        self.client.call_tool("slack_send_message", {
            "channel": "support",
            "message": f"New ticket: {ticket_id}"
        })
        print(f"  Notified team on Slack")
        
        self.client.call_tool("email_send", {
            "to": customer,
            "subject": "Ticket Created",
            "body": f"We've created ticket {ticket_id} for your issue."
        })
        print(f"  Sent acknowledgment email")
        
        return "Ticket handled!"


class AnalystAgent(Agent):
    """Analyst Agent - analyzes data."""
    
    def __init__(self, server_command):
        super().__init__("Analyst Agent", "analyst", server_command)
    
    def generate_report(self):
        print(f"\n[{self.name}] Generating sales report...")
        
        data = self.client.call_tool("sql_query", {"query": "SELECT * FROM sales"})
        print(f"  Retrieved {len(data)} records")
        
        chart = self.client.call_tool("chart_generate", {
            "data": data,
            "chart_type": "bar"
        })
        print(f"  {chart}")
        
        return "Report generated!"


def main():
    print("=" * 70)
    print("MULTI-AGENT ARCHITECTURE DEMO")
    print("=" * 70)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    server_command = ["python", server_path]
    
    # Create agents
    devops = DevOpsAgent(server_command)
    support = SupportAgent(server_command)
    analyst = AnalystAgent(server_command)
    
    try:
        # Connect all agents
        print("\n" + "-" * 70)
        print("Connecting all agents to shared MCP server...")
        print("-" * 70)
        
        devops.connect()
        support.connect()
        analyst.connect()
        
        # Each agent does its work
        print("\n" + "=" * 70)
        print("AGENTS AT WORK")
        print("=" * 70)
        
        devops.check_health()
        devops.deploy()
        
        support.handle_ticket(
            "customer@example.com",
            "Cannot access dashboard after login"
        )
        
        analyst.generate_report()
        
    finally:
        print("\n" + "-" * 70)
        print("Disconnecting agents...")
        print("-" * 70)
        devops.disconnect()
        support.disconnect()
        analyst.disconnect()
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print("""
🎯 Key Benefits:

   • One MCP server serves all agents
   • Each agent has different permissions
   • Shared infrastructure reduces code duplication
   • Easy to add new agent types
   • Centralized tool management

📊 Architecture:

   DevOps Agent ──┐
   Support Agent ──┼──→ MCP Server ──→ Tools
   Analyst Agent ──┘

   Each agent sees only tools it's allowed to use!
""")


if __name__ == "__main__":
    main()
