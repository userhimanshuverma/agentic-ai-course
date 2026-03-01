# Day 12: Observability & Logging

## 🎯 Why Observability Matters

When you have multiple agents using shared tools, you need to know:
- Who did what?
- When did it happen?
- Did it succeed or fail?
- How long did it take?

## 📊 Observability Stack

```
┌─────────────────────────────────────────────────────────┐
│              OBSERVABILITY LAYERS                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. LOGGING                                             │
│     • Request/response logging                          │
│     • Error logging                                     │
│     • Audit trails                                      │
│                                                          │
│  2. METRICS                                             │
│     • Tool usage counts                                 │
│     • Response times                                    │
│     • Error rates                                       │
│                                                          │
│  3. TRACING                                             │
│     • Request flow                                      │
│     • Agent identification                              │
│     • Tool execution path                               │
│                                                          │
│  4. ALERTING                                            │
│     • High error rates                                  │
│     • Slow responses                                    │
│     • Unusual patterns                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Implementation

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Observable MCP Server
=====================

MCP server with comprehensive logging and metrics.
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, Any
from collections import defaultdict


class ObservableMCPServer:
    """MCP server with observability features"""
    
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
    
    def register_tool(self, name: str, description: str, handler):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
    
    def run(self):
        """Main server loop with observability"""
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
        
        # Log the request
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
            
            # Log success
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
            # Log error
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
        """Return current metrics"""
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
        """Record request metrics"""
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
        """Log an event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        self.request_log.append(event)
        
        # Print to stderr for visibility
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
```

## 📈 Metrics Dashboard

Create `dashboard.py`:

```python
#!/usr/bin/env python3
"""Simple metrics dashboard"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))
from client import MCPClient


def print_dashboard(metrics):
    """Print formatted metrics"""
    print("\n" + "=" * 60)
    print("MCP SERVER METRICS DASHBOARD")
    print("=" * 60)
    
    print(f"\n📊 General:")
    print(f"   Uptime: {metrics['uptime_seconds']}s")
    print(f"   Total Requests: {metrics['requests_total']}")
    print(f"   Total Errors: {metrics['errors_total']}")
    print(f"   Error Rate: {metrics['error_rate']}%")
    print(f"   Avg Response Time: {metrics['avg_response_time_ms']}ms")
    
    print(f"\n🔧 Tool Usage:")
    for tool, count in metrics['requests_by_tool'].items():
        bar = "█" * int(count / max(metrics['requests_by_tool'].values()) * 20)
        print(f"   {tool:20} {bar} {count}")
    
    print(f"\n👤 Agent Usage:")
    for agent, count in metrics['requests_by_agent'].items():
        print(f"   {agent}: {count} requests")


def main():
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        client.connect()
        
        # Generate some traffic
        print("Generating traffic...")
        for i in range(5):
            client.call_tool("calculate", {"expression": f"{i} * 2"})
            client.call_tool("get_time", {})
        
        # Get metrics
        response = client._send_request("metrics/get", {})
        metrics = response["result"]["metrics"]
        
        print_dashboard(metrics)
        
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
```

## 🎓 Key Takeaway

**Observability = Visibility**

1. **Log everything** - Who, what, when
2. **Measure metrics** - Usage, performance, errors
3. **Track agents** - Know which agent does what
4. **Monitor health** - Error rates, response times

Without observability, you're flying blind. With it, you can optimize, debug, and scale confidently.

## 🚀 What's Next?

Tomorrow: **Guardrails & Failure Modes** - Handle things going wrong gracefully.

---

**Remember:** You can't improve what you don't measure. Start logging and monitoring from day one.
