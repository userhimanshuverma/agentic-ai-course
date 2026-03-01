#!/usr/bin/env python3
"""
Support Agent Example
=====================

A customer support agent that handles tickets, sends notifications,
and manages customer communications through MCP.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))
from client import MCPClient


class SupportAgent:
    """
    Support Agent for customer service.
    
    Capabilities:
    - Create and manage tickets
    - Send notifications
    - Handle customer inquiries
    - Escalate issues
    """
    
    def __init__(self, mcp_server_command=None):
        self.name = "Support Agent"
        
        if mcp_server_command is None:
            server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
            mcp_server_command = ["python", server_path]
        
        self.client = MCPClient(mcp_server_command)
        self.connected = False
    
    def connect(self):
        """Connect to MCP server."""
        print(f"\n🔌 [{self.name}] Connecting to MCP server...")
        self.client.connect()
        self.connected = True
        
        tools = self.client.list_tools()
        print(f"✅ Connected! Available tools: {len(tools)}")
        for tool in tools:
            print(f"   • {tool['name']}")
        
        return True
    
    def disconnect(self):
        """Disconnect from MCP server."""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            print(f"\n🔌 [{self.name}] Disconnected.")
    
    def create_ticket(self, customer: str, issue: str, priority: str = "medium"):
        """Create a support ticket."""
        print(f"\n🎫 [{self.name}] Creating ticket for {customer}...")
        
        ticket = self.client.call_tool("create_ticket", {
            "customer": customer,
            "issue": issue,
            "priority": priority
        })
        print(f"   ✅ {ticket}")
        
        # Notify team
        self.client.call_tool("send_notification", {
            "channel": "support-team",
            "message": f"New {priority} priority ticket from {customer}"
        })
        print(f"   📢 Team notified")
        
        return ticket
    
    def respond_to_customer(self, ticket_id: str, customer: str, response: str):
        """Send response to customer."""
        print(f"\n💬 [{self.name}] Responding to ticket {ticket_id}...")
        
        result = self.client.call_tool("send_email", {
            "to": customer,
            "subject": f"Re: Ticket #{ticket_id}",
            "body": response
        })
        print(f"   ✅ {result}")
        
        # Update ticket
        self.client.call_tool("update_ticket", {
            "ticket_id": ticket_id,
            "status": "waiting_for_customer"
        })
        
        return True
    
    def escalate_ticket(self, ticket_id: str, reason: str):
        """Escalate ticket to engineering."""
        print(f"\n🚨 [{self.name}] Escalating ticket {ticket_id}...")
        
        # Update ticket status
        self.client.call_tool("update_ticket", {
            "ticket_id": ticket_id,
            "status": "escalated"
        })
        
        # Notify engineering
        self.client.call_tool("send_notification", {
            "channel": "engineering",
            "message": f"Escalated ticket #{ticket_id}: {reason}"
        })
        print(f"   ✅ Escalated to engineering")
        
        return True
    
    def get_ticket_status(self, ticket_id: str):
        """Get ticket status."""
        print(f"\n📊 [{self.name}] Checking status of ticket {ticket_id}...")
        
        status = self.client.call_tool("get_ticket_status", {
            "ticket_id": ticket_id
        })
        print(f"   Status: {status}")
        
        return status
    
    def run_daily_report(self):
        """Generate daily support report."""
        print(f"\n📈 [{self.name}] Generating daily report...")
        
        # Get stats
        stats = self.client.call_tool("get_ticket_stats", {})
        print(f"   Today's Stats: {stats}")
        
        # Send report to manager
        self.client.call_tool("send_email", {
            "to": "manager@company.com",
            "subject": "Daily Support Report",
            "body": f"Support statistics for today:\n{stats}"
        })
        print(f"   📧 Report sent to manager")
        
        return stats


def main():
    """Main entry point."""
    print("=" * 70)
    print("SUPPORT AGENT EXAMPLE")
    print("=" * 70)
    
    agent = SupportAgent()
    
    try:
        agent.connect()
        
        print("\n" + "=" * 70)
        print("RUNNING SUPPORT SCENARIOS")
        print("=" * 70)
        
        # Scenario 1: Create ticket
        ticket = agent.create_ticket(
            "john@example.com",
            "Cannot login to dashboard",
            priority="high"
        )
        
        # Scenario 2: Respond to customer
        agent.respond_to_customer(
            "TICK-001",
            "john@example.com",
            "We're investigating this issue. Please try clearing your browser cache."
        )
        
        # Scenario 3: Check status
        agent.get_ticket_status("TICK-001")
        
        # Scenario 4: Escalate
        agent.escalate_ticket("TICK-001", "Requires backend investigation")
        
        # Scenario 5: Daily report
        agent.run_daily_report()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        agent.disconnect()
    
    print("\n" + "=" * 70)
    print("Support Agent completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
