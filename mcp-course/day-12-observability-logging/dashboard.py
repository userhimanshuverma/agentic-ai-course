#!/usr/bin/env python3
"""
Day 12: Metrics Dashboard
=========================

Displays real-time metrics from the observable MCP server.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))
from client import MCPClient


def print_dashboard(metrics):
    """Print formatted metrics."""
    print("\n" + "=" * 70)
    print("📊 MCP SERVER METRICS DASHBOARD")
    print("=" * 70)
    
    print(f"\n📈 General:")
    print(f"   ⏱️  Uptime: {metrics['uptime_seconds']}s")
    print(f"   📨 Total Requests: {metrics['requests_total']}")
    print(f"   ❌ Total Errors: {metrics['errors_total']}")
    print(f"   📉 Error Rate: {metrics['error_rate']}%")
    print(f"   ⏱️  Avg Response Time: {metrics['avg_response_time_ms']}ms")
    
    print(f"\n🔧 Tool Usage:")
    if metrics['requests_by_tool']:
        max_count = max(metrics['requests_by_tool'].values())
        for tool, count in sorted(metrics['requests_by_tool'].items()):
            bar_length = int(count / max_count * 30) if max_count > 0 else 0
            bar = "█" * bar_length
            print(f"   {tool:20} {bar} {count}")
    else:
        print("   No tool usage yet")
    
    print(f"\n👤 Agent Usage:")
    if metrics['requests_by_agent']:
        for agent, count in sorted(metrics['requests_by_agent'].items()):
            print(f"   {agent}: {count} requests")
    else:
        print("   No agent activity yet")


def main():
    print("=" * 70)
    print("OBSERVABILITY DASHBOARD")
    print("=" * 70)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        client.connect()
        
        # Generate some traffic
        print("\n🔄 Generating traffic...")
        agents = ["devops", "support", "analyst"]
        
        for i in range(10):
            agent = agents[i % len(agents)]
            try:
                client.call_tool("calculate", {"expression": f"{i} * 2"})
                if i % 2 == 0:
                    client.call_tool("get_time", {})
            except:
                pass  # Ignore errors for demo
        
        # Get metrics
        print("\n📊 Fetching metrics...")
        response = client._send_request("metrics/get", {})
        metrics = response["result"]["metrics"]
        
        print_dashboard(metrics)
        
    finally:
        client.disconnect()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
