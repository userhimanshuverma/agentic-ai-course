#!/usr/bin/env python3
"""
DevOps Agent Example
====================

A production-ready DevOps agent that monitors infrastructure,
deploys applications, and manages cloud resources through MCP.
"""

import sys
import os
import time

# Add path to MCP client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))
from client import MCPClient


class DevOpsAgent:
    """
    DevOps Agent for infrastructure management.
    
    Capabilities:
    - Monitor system health
    - Deploy applications
    - Manage cloud resources
    - Check logs and metrics
    """
    
    def __init__(self, mcp_server_command=None):
        self.name = "DevOps Agent"
        
        # Use default server if not provided
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
    
    def check_system_health(self):
        """Check overall system health."""
        print(f"\n🏥 [{self.name}] Checking system health...")
        
        # Check server status
        status = self.client.call_tool("server_status", {})
        print(f"   Server Status: {status}")
        
        # Check disk usage
        disk = self.client.call_tool("check_disk", {})
        print(f"   Disk Usage: {disk}")
        
        # Check memory
        memory = self.client.call_tool("check_memory", {})
        print(f"   Memory: {memory}")
        
        return {"status": "healthy", "checks": 3}
    
    def deploy_application(self, app_name: str, version: str):
        """Deploy an application."""
        print(f"\n🚀 [{self.name}] Deploying {app_name} v{version}...")
        
        # Pre-deployment checks
        print("   Running pre-deployment checks...")
        health = self.check_system_health()
        
        if health["status"] != "healthy":
            print("   ❌ Deployment aborted: System not healthy")
            return False
        
        # Deploy
        print("   Deploying to production...")
        result = self.client.call_tool("deploy", {
            "app_name": app_name,
            "version": version
        })
        print(f"   ✅ {result}")
        
        # Verify deployment
        print("   Verifying deployment...")
        verify = self.client.call_tool("verify_deployment", {"app_name": app_name})
        print(f"   ✅ {verify}")
        
        return True
    
    def scale_service(self, service: str, replicas: int):
        """Scale a service."""
        print(f"\n📈 [{self.name}] Scaling {service} to {replicas} replicas...")
        
        result = self.client.call_tool("scale", {
            "service": service,
            "replicas": replicas
        })
        
        print(f"   ✅ {result}")
        return result
    
    def get_logs(self, service: str, lines: int = 50):
        """Get logs from a service."""
        print(f"\n📜 [{self.name}] Getting logs for {service}...")
        
        logs = self.client.call_tool("get_logs", {
            "service": service,
            "lines": lines
        })
        
        print(f"   Retrieved {lines} lines:")
        for line in logs.split('\n')[:5]:
            print(f"   {line}")
        if len(logs.split('\n')) > 5:
            print(f"   ... and {len(logs.split('\n')) - 5} more lines")
        
        return logs
    
    def run_maintenance(self):
        """Run maintenance tasks."""
        print(f"\n🔧 [{self.name}] Running maintenance tasks...")
        
        # Clean up old logs
        result = self.client.call_tool("cleanup_logs", {"days": 7})
        print(f"   ✅ {result}")
        
        # Optimize database
        result = self.client.call_tool("optimize_db", {})
        print(f"   ✅ {result}")
        
        return "Maintenance complete"


def main():
    """Main entry point."""
    print("=" * 70)
    print("DEVOPS AGENT EXAMPLE")
    print("=" * 70)
    
    agent = DevOpsAgent()
    
    try:
        # Connect
        agent.connect()
        
        # Run scenarios
        print("\n" + "=" * 70)
        print("RUNNING DEVOPS SCENARIOS")
        print("=" * 70)
        
        # Scenario 1: Health check
        agent.check_system_health()
        
        # Scenario 2: Deploy application
        agent.deploy_application("web-api", "2.5.1")
        
        # Scenario 3: Scale service
        agent.scale_service("web-api", 5)
        
        # Scenario 4: Get logs
        agent.get_logs("web-api", 100)
        
        # Scenario 5: Maintenance
        agent.run_maintenance()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        agent.disconnect()
    
    print("\n" + "=" * 70)
    print("DevOps Agent completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
