#!/usr/bin/env python3
"""
Support Agent MCP Server
========================

MCP server providing support tools for customer service.
"""

import json
import sys
import random
from datetime import datetime


class SupportMCPServer:
    """MCP server with support tools."""
    
    def __init__(self):
        self.tickets = {}
        self.ticket_counter = 100
        self.tools = {
            "create_ticket": self.create_ticket,
            "update_ticket": self.update_ticket,
            "get_ticket_status": self.get_ticket_status,
            "get_ticket_stats": self.get_ticket_stats,
            "send_email": self.send_email,
            "send_notification": self.send_notification,
        }
        print("Support MCP Server initialized", file=sys.stderr)
    
    def run(self):
        """Main server loop."""
        print("Server running...", file=sys.stderr)
        
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
    
    def handle_request(self, request):
        """Handle JSON-RPC request."""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}},
                "id": request_id
            }
        
        elif method == "tools/list":
            tools_list = [
                {"name": name, "description": self.get_description(name)}
                for name in self.tools.keys()
            ]
            return {
                "jsonrpc": "2.0",
                "result": {"tools": tools_list},
                "id": request_id
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
            
            try:
                result = self.tools[tool_name](**arguments)
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
        
        else:
            return self.send_error(request_id, -32601, f"Method not found: {method}")
    
    def get_description(self, tool_name):
        descriptions = {
            "create_ticket": "Create a support ticket",
            "update_ticket": "Update ticket status",
            "get_ticket_status": "Get ticket status",
            "get_ticket_stats": "Get ticket statistics",
            "send_email": "Send email to customer",
            "send_notification": "Send notification to team",
        }
        return descriptions.get(tool_name, "No description")
    
    # Tool implementations
    def create_ticket(self, customer, issue, priority="medium"):
        self.ticket_counter += 1
        ticket_id = f"TICK-{self.ticket_counter}"
        self.tickets[ticket_id] = {
            "id": ticket_id,
            "customer": customer,
            "issue": issue,
            "priority": priority,
            "status": "open",
            "created": datetime.now().isoformat()
        }
        return f"Created ticket {ticket_id} for {customer}"
    
    def update_ticket(self, ticket_id, status):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            return f"Updated {ticket_id} to {status}"
        return f"Ticket {ticket_id} not found"
    
    def get_ticket_status(self, ticket_id):
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            return f"{ticket_id}: {ticket['status']} (Priority: {ticket['priority']})"
        return f"Ticket {ticket_id} not found"
    
    def get_ticket_stats(self):
        total = len(self.tickets)
        open_tickets = sum(1 for t in self.tickets.values() if t["status"] == "open")
        return f"Total: {total}, Open: {open_tickets}, Resolved: {total - open_tickets}"
    
    def send_email(self, to, subject, body):
        return f"Email sent to {to}"
    
    def send_notification(self, channel, message):
        return f"Notification sent to #{channel}"
    
    def send_error(self, request_id, code, message):
        return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}


if __name__ == "__main__":
    server = SupportMCPServer()
    server.run()
