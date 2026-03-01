#!/usr/bin/env python3
"""
Day 12: Observable MCP Server
=============================

MCP server with comprehensive logging and metrics.
Tracks: requests, errors, response times, tool usage.
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, Any
from collections import defaultdict


class ObservableMCPServer:
    """
    MCP server with observability features.
    
    Tracks:
    - Total requests
    - Requests per tool
    - Requests per agent
    - Error rates
    - Response times
    """
    
    def __init__(self):
        self.tools = {}
        
        # Metrics storage
        self.metrics = {
            "requests_total": 0,
            "requests_by_tool": defaultdict(int),
            "requests_by_agent": defaultdict(int),
            "errors_total": 0,
            "response_times": [],
            "start_time": time.time()
        }
        
        # Request log
        self.request_log = []
        
        print("Observable MCP Server initialized", file=sys.stderr)
    
    def register_tool(self, name: str, description: str, handler):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
    
    def run(self):
        """Main server loop with observability."""
        self.log_event("SERVER", "Server started", {"tools": list(self.tools.keys())})
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                start_time = time.time()
                request = json.loads(line)
                
                # Process request
                response = self.handle_request(request)
                
                # Record metrics
                duration = time.time() - start_time
                self.record_metrics(request, response, duration)
                
                # Send response
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                self.log_event("ERROR", str(e), {})
                self.send_error(None, -32603, str(e))
    
    def handle_request(self, request: Dict) -> Dict:
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        agent_id = params.get("_agent_id", "unknown")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, agent_id, params)
        elif method == "metrics/get":
            return self.handle_get_metrics(request_id)
        else:
            return self.send_error(request_id, -32601, f"Method not found: {method}")
    
    def handle_initialize(self, request_id) -> Dict:
        return {
            "jsonrpc": "2.0",
            "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}},
            "id": request_id
        }
    
    def handle_list_tools(self, request_id) -> Dict:
        tools_list = [
            {"name": tool["name"], "description": tool["description"]}
            for tool in self.tools.values()
        ]
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": request_id
        }
    
    def handle_call_tool(self, request_id: str, agent_id: str, params: Dict) -> Dict:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        self.log_event("REQUEST", f"Agent {agent_id} calling {tool_name}", {
            "agent_id": agent_id,
            "tool": tool_name,
            "arguments": arguments
        })
        
        if tool_name not in self.tools:
            return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
        
        try:
            handler = self.tools[tool_name]["handler"]
            result = handler(**arguments)
            
            self.log_event("SUCCESS", f"{tool_name} executed successfully", {
                "tool": tool_name,
                "agent_id": agent_id
            })
            
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": str(result)}], "isError": False},
                "id": request_id
            }
        except Exception as e:
            self.log_event("ERROR", f"{tool_name} failed: {str(e)}", {
                "tool": tool_name,
                "agent_id": agent_id,
                "error": str(e)
            })
            
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True},
                "id": request_id
            }
    
    def handle_get_metrics(self, request_id) -> Dict:
        """Return current metrics."""
        uptime = time.time() - self.metrics["start_time"]
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "metrics": {
                    "uptime_seconds": round(uptime, 2),
                    "requests_total": self.metrics["requests_total"],
                    "errors_total": self.metrics["errors_total"],
                    "error_rate": round(self.metrics["errors_total"] / max(self.metrics["requests_total"], 1) * 100, 2),
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "requests_by_tool": dict(self.metrics["requests_by_tool"]),
                    "requests_by_agent": dict(self.metrics["requests_by_agent"])
                }
            },
            "id": request_id
        }
    
    def record_metrics(self, request: Dict, response: Dict, duration: float):
        """Record request metrics."""
        self.metrics["requests_total"] += 1
        self.metrics["response_times"].append(duration)
        
        # Keep only last 100 response times
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
        
        # Record by tool
        if request.get("method") == "tools/call":
            tool_name = request.get("params", {}).get("name", "unknown")
            self.metrics["requests_by_tool"][tool_name] += 1
            
            agent_id = request.get("params", {}).get("_agent_id", "unknown")
            self.metrics["requests_by_agent"][agent_id] += 1
            
            # Check for errors
            if response.get("result", {}).get("isError"):
                self.metrics["errors_total"] += 1
    
    def log_event(self, level: str, message: str, data: Dict):
        """Log an event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        self.request_log.append(event)
        print(f"[{level}] {message}", file=sys.stderr)
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}


# Sample tools
def calculate(expression: str):
    return eval(expression)

def get_time():
    return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    server = ObservableMCPServer()
    server.register_tool("calculate", "Calculate expression", calculate)
    server.register_tool("get_time", "Get current time", get_time)
    server.run()
