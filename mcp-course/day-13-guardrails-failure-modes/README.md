# Day 13: Guardrails & Failure Modes

## 🎯 Why Guardrails Matter

AI agents can make mistakes:
- Call wrong tools
- Pass bad parameters
- Get stuck in loops
- Hit timeouts

**Guardrails prevent disasters.**

## 🛡️ Guardrail Types

```
┌─────────────────────────────────────────────────────────┐
│                 GUARDRAIL LAYERS                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. INPUT VALIDATION                                    │
│     • Schema validation                                 │
│     • Type checking                                     │
│     • Dangerous pattern detection                       │
│                                                          │
│  2. EXECUTION LIMITS                                    │
│     • Timeout protection                                │
│     • Resource limits                                   │
│     • Rate limiting                                     │
│                                                          │
│  3. ERROR HANDLING                                      │
│     • Graceful degradation                              │
│     • Retry logic                                       │
│     • Circuit breakers                                  │
│                                                          │
│  4. SAFETY CHECKS                                       │
│     • Permission validation                             │
│     • Content filtering                                 │
│     • Audit logging                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Implementation

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Guardrails MCP Server
=====================

MCP server with comprehensive guardrails and failure handling.
"""

import json
import sys
import time
import re
from typing import Dict, Any, Optional
from functools import wraps


class GuardrailsMCPServer:
    """MCP server with guardrails"""
    
    def __init__(self):
        self.tools = {}
        self.request_counts = {}
        self.circuit_breakers = {}
    
    def register_tool(self, name: str, description: str, handler, 
                      timeout: int = 30, max_retries: int = 3):
        """Register tool with guardrail config"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "timeout": timeout,
            "max_retries": max_retries
        }
    
    def run(self):
        """Main server loop"""
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
        """Validate input for dangerous patterns"""
        # Convert to string for checking
        args_str = json.dumps(arguments)
        
        # Dangerous patterns
        dangerous = [
            r"rm\s+-rf\s+/",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r";\s*rm",
            r"\|\s*sh",
            r"__import__",
            r"os\.system",
            r"subprocess",
            r"eval\s*\(",
            r"exec\s*\("
        ]
        
        for pattern in dangerous:
            if re.search(pattern, args_str, re.IGNORECASE):
                return f"Dangerous pattern detected: {pattern}"
        
        # Type validation for known tools
        if tool_name == "calculate":
            expr = arguments.get("expression", "")
            # Only allow safe math
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expr):
                return "Expression contains invalid characters"
        
        return None
    
    def check_rate_limit(self, tool_name: str) -> bool:
        """Simple rate limiting"""
        now = time.time()
        window = 60  # 1 minute window
        max_requests = 10  # 10 requests per minute
        
        if tool_name not in self.request_counts:
            self.request_counts[tool_name] = []
        
        # Remove old requests
        self.request_counts[tool_name] = [
            t for t in self.request_counts[tool_name] if now - t < window
        ]
        
        # Check limit
        if len(self.request_counts[tool_name]) >= max_requests:
            return False
        
        # Record request
        self.request_counts[tool_name].append(now)
        return True
    
    def is_circuit_open(self, tool_name: str) -> bool:
        """Check if circuit breaker is open"""
        if tool_name not in self.circuit_breakers:
            return False
        
        cb = self.circuit_breakers[tool_name]
        if cb["failures"] >= 5:
            # Check if we should reset
            if time.time() - cb["last_failure"] > 30:  # 30 second cooldown
                cb["failures"] = 0
                return False
            return True
        
        return False
    
    def record_failure(self, tool_name: str):
        """Record a failure for circuit breaker"""
        if tool_name not in self.circuit_breakers:
            self.circuit_breakers[tool_name] = {"failures": 0, "last_failure": 0}
        
        self.circuit_breakers[tool_name]["failures"] += 1
        self.circuit_breakers[tool_name]["last_failure"] = time.time()
    
    def execute_with_guardrails(self, tool: Dict, arguments: Dict) -> Dict:
        """Execute with timeout and retry"""
        max_retries = tool["max_retries"]
        timeout = tool["timeout"]
        
        for attempt in range(max_retries):
            try:
                # Execute with timeout
                import concurrent.futures
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(tool["handler"], **arguments)
                    result = future.result(timeout=timeout)
                    
                    return {"success": True, "data": result}
                    
            except concurrent.futures.TimeoutError:
                if attempt == max_retries - 1:
                    self.record_failure(tool["name"])
                    return {"success": False, "error": f"Timeout after {timeout}s"}
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                
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
    """Safe calculator"""
    # Only allow basic math operations
    allowed = {"__builtins__": {}}
    return eval(expression, allowed, {})

def slow_operation(delay: float):
    """Simulates slow operation"""
    time.sleep(delay)
    return f"Completed after {delay}s"

def flaky_operation(fail_probability: float = 0.5):
    """Simulates unreliable operation"""
    import random
    if random.random() < fail_probability:
        raise Exception("Random failure!")
    return "Success!"


if __name__ == "__main__":
    server = GuardrailsMCPServer()
    server.register_tool("calculate", "Safe calculator", calculate, timeout=5)
    server.register_tool("slow_operation", "Slow operation (for timeout testing)", slow_operation, timeout=2)
    server.register_tool("flaky_operation", "Unreliable operation (for retry testing)", flaky_operation, max_retries=5)
    server.run()
```

## 🧪 Testing Guardrails

Create `test_guardrails.py`:

```python
#!/usr/bin/env python3
"""Test guardrails"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))
from client import MCPClient


def test_input_validation(client):
    """Test dangerous input blocking"""
    print("\n1. Testing Input Validation...")
    
    # Should be blocked
    try:
        result = client.call_tool("calculate", {"expression": "__import__('os').system('ls')"})
        print(f"   ❌ FAIL: Dangerous code executed!")
    except Exception as e:
        print(f"   ✅ PASS: Dangerous code blocked - {e}")
    
    # Should work
    result = client.call_tool("calculate", {"expression": "2 + 2"})
    print(f"   ✅ PASS: Safe code works - {result}")


def test_timeout(client):
    """Test timeout protection"""
    print("\n2. Testing Timeout Protection...")
    
    # Should timeout
    try:
        result = client.call_tool("slow_operation", {"delay": 5})
        print(f"   ❌ FAIL: Should have timed out!")
    except Exception as e:
        print(f"   ✅ PASS: Timeout works - {e}")


def test_retry(client):
    """Test retry logic"""
    print("\n3. Testing Retry Logic...")
    
    # May fail or succeed (random)
    try:
        result = client.call_tool("flaky_operation", {"fail_probability": 0.7})
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Failed after retries: {e}")


def test_rate_limit(client):
    """Test rate limiting"""
    print("\n4. Testing Rate Limiting...")
    
    # Make many rapid requests
    success = 0
    limited = 0
    
    for i in range(15):
        try:
            client.call_tool("calculate", {"expression": f"{i} + 1"})
            success += 1
        except Exception as e:
            if "Rate limit" in str(e):
                limited += 1
    
    print(f"   Success: {success}, Rate Limited: {limited}")
    if limited > 0:
        print(f"   ✅ PASS: Rate limiting works!")
    else:
        print(f"   ❌ FAIL: Should have rate limited!")


def main():
    print("=" * 60)
    print("Guardrails Testing")
    print("=" * 60)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        client.connect()
        
        test_input_validation(client)
        test_timeout(client)
        test_retry(client)
        test_rate_limit(client)
        
    finally:
        client.disconnect()
    
    print("\n" + "=" * 60)
    print("Testing complete!")


if __name__ == "__main__":
    main()
```

## 🎓 Key Takeaway

**Guardrails = Safety**

1. **Validate inputs** - Block dangerous patterns
2. **Set timeouts** - Prevent hanging
3. **Retry failures** - Handle transient issues
4. **Rate limit** - Prevent abuse
5. **Circuit break** - Fail fast when broken

Without guardrails, one bad request can crash everything. With them, your system is resilient.

## 🚀 What's Next?

Tomorrow: **Production Architecture** - The final piece: putting it all together!

---

**Remember:** Hope is not a strategy. Build guardrails from day one.
