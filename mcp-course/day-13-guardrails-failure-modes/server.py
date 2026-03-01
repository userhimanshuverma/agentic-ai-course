#!/usr/bin/env python3
"""
Day 13: Guardrails MCP Server
=============================

MCP server with comprehensive guardrails:
- Input validation
- Rate limiting
- Timeout protection
- Retry logic
- Circuit breaker
"""

import json
import sys
import time
import re
from typing import Dict, Any, Optional


class GuardrailsMCPServer:
    """
    MCP server with guardrails for safe operation.
    """
    
    def __init__(self):
        self.tools = {}
        self.request_counts = {}
        self.circuit_breakers = {}
        print("Guardrails MCP Server initialized", file=sys.stderr)
    
    def register_tool(self, name: str, description: str, handler, 
                      timeout: int = 30, max_retries: int = 3):
        """Register tool with guardrail config."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "timeout": timeout,
            "max_retries": max_retries
        }
    
    def run(self):
        """Main server loop."""
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
        params = request.get("params", {})
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_list_tools(request_id)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, params)
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
    
    def handle_call_tool(self, request_id: str, params: Dict) -> Dict:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Guardrail 1: Validate tool exists
        if tool_name not in self.tools:
            return self.send_error(request_id, -32602, f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        
        # Guardrail 2: Input validation
        validation_error = self.validate_input(tool_name, arguments)
        if validation_error:
            return self.send_error(request_id, -32600, validation_error)
        
        # Guardrail 3: Rate limiting
        if not self.check_rate_limit(tool_name):
            return self.send_error(request_id, 429, "Rate limit exceeded")
        
        # Guardrail 4: Circuit breaker
        if self.is_circuit_open(tool_name):
            return self.send_error(request_id, 503, "Service temporarily unavailable (circuit open)")
        
        # Guardrail 5: Execute with timeout and retry
        result = self.execute_with_guardrails(tool, arguments)
        
        if result["success"]:
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": str(result["data"])}], "isError": False},
                "id": request_id
            }
        else:
            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": f"Error: {result['error']}"}], "isError": True},
                "id": request_id
            }
    
    def validate_input(self, tool_name: str, arguments: Dict) -> Optional[str]:
        """Validate input for dangerous patterns."""
        args_str = json.dumps(arguments)
        
        dangerous = [
            r"rm\s+-rf", r"DROP\s+TABLE", r"DELETE\s+FROM",
            r";\s*rm", r"\|\s*sh", r"__import__", r"os\.system",
            r"subprocess", r"eval\s*\(", r"exec\s*\("
        ]
        
        for pattern in dangerous:
            if re.search(pattern, args_str, re.IGNORECASE):
                return f"Dangerous pattern detected"
        
        if tool_name == "calculate":
            expr = arguments.get("expression", "")
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expr):
                return "Expression contains invalid characters"
        
        return None
    
    def check_rate_limit(self, tool_name: str) -> bool:
        """Simple rate limiting."""
        now = time.time()
        window = 60
        max_requests = 10
        
        if tool_name not in self.request_counts:
            self.request_counts[tool_name] = []
        
        self.request_counts[tool_name] = [
            t for t in self.request_counts[tool_name] if now - t < window
        ]
        
        if len(self.request_counts[tool_name]) >= max_requests:
            return False
        
        self.request_counts[tool_name].append(now)
        return True
    
    def is_circuit_open(self, tool_name: str) -> bool:
        """Check if circuit breaker is open."""
        if tool_name not in self.circuit_breakers:
            return False
        
        cb = self.circuit_breakers[tool_name]
        if cb["failures"] >= 5:
            if time.time() - cb["last_failure"] > 30:
                cb["failures"] = 0
                return False
            return True
        return False
    
    def record_failure(self, tool_name: str):
        """Record a failure for circuit breaker."""
        if tool_name not in self.circuit_breakers:
            self.circuit_breakers[tool_name] = {"failures": 0, "last_failure": 0}
        
        self.circuit_breakers[tool_name]["failures"] += 1
        self.circuit_breakers[tool_name]["last_failure"] = time.time()
    
    def execute_with_guardrails(self, tool: Dict, arguments: Dict) -> Dict:
        """Execute with timeout and retry."""
        max_retries = tool["max_retries"]
        timeout = tool["timeout"]
        
        for attempt in range(max_retries):
            try:
                import concurrent.futures
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(tool["handler"], **arguments)
                    result = future.result(timeout=timeout)
                    return {"success": True, "data": result}
                    
            except concurrent.futures.TimeoutError:
                if attempt == max_retries - 1:
                    self.record_failure(tool["name"])
                    return {"success": False, "error": f"Timeout after {timeout}s"}
                time.sleep(0.5 * (attempt + 1))
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.record_failure(tool["name"])
                    return {"success": False, "error": str(e)}
                time.sleep(0.5 * (attempt + 1))
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def send_error(self, request_id, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}


# Sample tools
def calculate(expression: str):
    allowed = {"__builtins__": {}}
    return eval(expression, allowed, {})

def slow_operation(delay: float):
    import time
    time.sleep(delay)
    return f"Completed after {delay}s"


if __name__ == "__main__":
    server = GuardrailsMCPServer()
    server.register_tool("calculate", "Safe calculator", calculate, timeout=5)
    server.register_tool("slow_operation", "Slow operation", slow_operation, timeout=2)
    server.run()
