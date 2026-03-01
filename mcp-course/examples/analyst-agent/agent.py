#!/usr/bin/env python3
"""
Analyst Agent Example
=====================

A data analyst agent that queries databases, generates reports,
and creates visualizations through MCP.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "day-09-build-mcp-client"))
from client import MCPClient


class AnalystAgent:
    """
    Analyst Agent for data analysis.
    
    Capabilities:
    - Query databases
    - Generate reports
    - Create visualizations
    - Perform data analysis
    """
    
    def __init__(self, mcp_server_command=None):
        self.name = "Analyst Agent"
        
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
    
    def query_data(self, query: str):
        """Execute a data query."""
        print(f"\n🔍 [{self.name}] Executing query...")
        print(f"   Query: {query[:60]}...")
        
        result = self.client.call_tool("execute_query", {"query": query})
        print(f"   ✅ Retrieved data")
        
        return result
    
    def generate_report(self, title: str, data_summary: str):
        """Generate a report."""
        print(f"\n📊 [{self.name}] Generating report: {title}...")
        
        report = self.client.call_tool("generate_report", {
            "title": title,
            "data": data_summary
        })
        print(f"   ✅ {report}")
        
        return report
    
    def create_chart(self, chart_type: str, data: str):
        """Create a visualization."""
        print(f"\n📈 [{self.name}] Creating {chart_type} chart...")
        
        chart = self.client.call_tool("create_chart", {
            "type": chart_type,
            "data": data
        })
        print(f"   ✅ {chart}")
        
        return chart
    
    def analyze_sales(self, period: str):
        """Analyze sales data."""
        print(f"\n💰 [{self.name}] Analyzing sales for {period}...")
        
        # Query sales data
        sales_data = self.client.call_tool("execute_query", {
            "query": f"SELECT * FROM sales WHERE period = '{period}'"
        })
        print(f"   Sales data: {sales_data}")
        
        # Generate summary
        summary = self.client.call_tool("analyze_data", {
            "data": sales_data,
            "analysis_type": "summary"
        })
        print(f"   Analysis: {summary}")
        
        # Create chart
        chart = self.create_chart("bar", sales_data)
        
        # Generate report
        report = self.generate_report(
            f"Sales Report - {period}",
            f"Sales analysis for {period}: {summary}"
        )
        
        return {"summary": summary, "chart": chart, "report": report}
    
    def predict_trends(self, metric: str, days: int):
        """Predict future trends."""
        print(f"\n🔮 [{self.name}] Predicting {metric} trends for next {days} days...")
        
        # Get historical data
        history = self.client.call_tool("execute_query", {
            "query": f"SELECT {metric}, date FROM metrics ORDER BY date DESC LIMIT 30"
        })
        
        # Run prediction
        prediction = self.client.call_tool("predict", {
            "metric": metric,
            "historical_data": history,
            "forecast_days": days
        })
        
        print(f"   Prediction: {prediction}")
        return prediction
    
    def export_data(self, format: str, query: str):
        """Export data to file."""
        print(f"\n📤 [{self.name}] Exporting data to {format}...")
        
        # Execute query
        data = self.client.call_tool("execute_query", {"query": query})
        
        # Export
        result = self.client.call_tool("export", {
            "data": data,
            "format": format
        })
        
        print(f"   ✅ {result}")
        return result


def main():
    """Main entry point."""
    print("=" * 70)
    print("ANALYST AGENT EXAMPLE")
    print("=" * 70)
    
    agent = AnalystAgent()
    
    try:
        agent.connect()
        
        print("\n" + "=" * 70)
        print("RUNNING ANALYST SCENARIOS")
        print("=" * 70)
        
        # Scenario 1: Query data
        agent.query_data("SELECT * FROM users WHERE created_at > '2024-01-01'")
        
        # Scenario 2: Sales analysis
        agent.analyze_sales("January 2026")
        
        # Scenario 3: Create visualization
        agent.create_chart("line", "revenue_data")
        
        # Scenario 4: Predict trends
        agent.predict_trends("daily_active_users", 7)
        
        # Scenario 5: Export data
        agent.export_data("csv", "SELECT * FROM transactions")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        agent.disconnect()
    
    print("\n" + "=" * 70)
    print("Analyst Agent completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
