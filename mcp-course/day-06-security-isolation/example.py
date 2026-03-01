#!/usr/bin/env python3
"""
Day 6 Example: Security & Isolation
====================================

This shows MCP security layers:
1. Authentication - Who are you?
2. Authorization - What can you do?
3. Validation - Is this safe?
4. Auditing - What happened?
"""

import json
import time
from datetime import datetime

print("=" * 70)
print("MCP SECURITY & ISOLATION DEMONSTRATION")
print("=" * 70)


# ============================================================
# SECURITY LAYER 1: AUTHENTICATION
# ============================================================
print("\n" + "=" * 70)
print("LAYER 1: AUTHENTICATION (Who are you?)")
print("=" * 70)

# API Keys database
VALID_API_KEYS = {
    "key_devops_123": "devops_agent",
    "key_support_456": "support_agent",
    "key_analyst_789": "analyst_agent"
}

def authenticate(api_key):
    """Check if API key is valid"""
    if api_key in VALID_API_KEYS:
        return VALID_API_KEYS[api_key]
    return None

print("\n🔐 Testing Authentication:")

test_keys = ["key_devops_123", "key_invalid_999", "key_support_456"]
for key in test_keys:
    agent = authenticate(key)
    if agent:
        print(f"  ✅ Key '{key[:12]}...' → Authenticated as '{agent}'")
    else:
        print(f"  ❌ Key '{key[:12]}...' → Authentication FAILED")


# ============================================================
# SECURITY LAYER 2: AUTHORIZATION
# ============================================================
print("\n" + "=" * 70)
print("LAYER 2: AUTHORIZATION (What can you do?)")
print("=" * 70)

# Permissions database
PERMISSIONS = {
    "devops_agent": ["git_*", "aws_*", "docker_*"],
    "support_agent": ["jira_*", "slack_*", "email_*"],
    "analyst_agent": ["sql_*", "chart_*", "report_*"]
}

def is_authorized(agent_id, tool_name):
    """Check if agent can use this tool"""
    allowed_patterns = PERMISSIONS.get(agent_id, [])
    
    for pattern in allowed_patterns:
        if pattern.endswith("*"):
            if tool_name.startswith(pattern[:-1]):
                return True
        elif tool_name == pattern:
            return True
    return False

print("\n🔒 Testing Authorization:")

test_cases = [
    ("devops_agent", "git_status"),
    ("devops_agent", "jira_create"),  # Should fail
    ("support_agent", "slack_send"),
    ("support_agent", "aws_deploy"),  # Should fail
    ("analyst_agent", "sql_query"),
]

for agent, tool in test_cases:
    allowed = is_authorized(agent, tool)
    status = "✅ ALLOWED" if allowed else "❌ DENIED"
    print(f"  {status}: '{agent}' → '{tool}'")


# ============================================================
# SECURITY LAYER 3: VALIDATION
# ============================================================
print("\n" + "=" * 70)
print("LAYER 3: VALIDATION (Is this safe?)")
print("=" * 70)

DANGEROUS_PATTERNS = [
    "rm -rf",
    "DROP TABLE",
    "DELETE FROM",
    "__import__",
    "os.system",
    "subprocess",
    "eval(",
    "exec("
]

def validate_input(tool_name, arguments):
    """Validate input for dangerous patterns"""
    args_str = json.dumps(arguments)
    
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in args_str.lower():
            return f"Dangerous pattern detected: {pattern}"
    
    # Tool-specific validation
    if tool_name == "calculate":
        expr = arguments.get("expression", "")
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expr):
            return "Expression contains invalid characters"
    
    return None

print("\n🛡️  Testing Input Validation:")

test_inputs = [
    ("calculate", {"expression": "2 + 2"}),
    ("calculate", {"expression": "__import__('os').system('ls')"}),
    ("sql_query", {"query": "SELECT * FROM users"}),
    ("sql_query", {"query": "DROP TABLE users"}),
]

for tool, args in test_inputs:
    error = validate_input(tool, args)
    if error:
        print(f"  ❌ BLOCKED: {tool}({args})")
        print(f"      Reason: {error}")
    else:
        print(f"  ✅ ALLOWED: {tool}({args})")


# ============================================================
# SECURITY LAYER 4: AUDITING
# ============================================================
print("\n" + "=" * 70)
print("LAYER 4: AUDITING (What happened?)")
print("=" * 70)

audit_log = []

def log_event(agent_id, tool_name, arguments, success, error=None):
    """Log every tool execution"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "success": success,
        "error": error
    }
    audit_log.append(event)
    return event

print("\n📝 Simulating Tool Executions:")

# Simulate some tool calls
log_event("devops_agent", "git_status", {}, True)
log_event("support_agent", "slack_send", {"channel": "alerts"}, True)
log_event("analyst_agent", "sql_query", {"query": "SELECT * FROM sales"}, True)
log_event("devops_agent", "aws_delete", {"resource": "*"}, False, "Not authorized")

print("\n  Audit Log:")
for event in audit_log:
    status = "✅" if event["success"] else "❌"
    print(f"    {status} [{event['timestamp'][:19]}] {event['agent_id']} → {event['tool_name']}")


# ============================================================
# COMPLETE SECURITY PIPELINE
# ============================================================
print("\n" + "=" * 70)
print("COMPLETE SECURITY PIPELINE")
print("=" * 70)

class SecureMCPServer:
    """MCP server with all security layers"""
    
    def __init__(self):
        self.tools = {
            "git_status": lambda: "Branch: main, Status: clean",
            "calculate": lambda expression: eval(expression, {"__builtins__": {}}, {})
        }
    
    def handle_request(self, api_key, tool_name, arguments):
        """Full security pipeline"""
        print(f"\n  🔍 Processing request: {tool_name}")
        
        # 1. AUTHENTICATE
        agent_id = authenticate(api_key)
        if not agent_id:
            print("     ❌ Authentication failed")
            return {"error": "Invalid API key"}
        print(f"     ✅ Authenticated as: {agent_id}")
        
        # 2. AUTHORIZE
        if not is_authorized(agent_id, tool_name):
            print(f"     ❌ Not authorized for tool: {tool_name}")
            log_event(agent_id, tool_name, arguments, False, "Unauthorized")
            return {"error": f"Not authorized for {tool_name}"}
        print(f"     ✅ Authorized for tool: {tool_name}")
        
        # 3. VALIDATE
        validation_error = validate_input(tool_name, arguments)
        if validation_error:
            print(f"     ❌ Validation failed: {validation_error}")
            log_event(agent_id, tool_name, arguments, False, validation_error)
            return {"error": validation_error}
        print(f"     ✅ Input validated")
        
        # 4. EXECUTE
        try:
            result = self.tools[tool_name](**arguments)
            print(f"     ✅ Execution successful")
            
            # 5. AUDIT
            log_event(agent_id, tool_name, arguments, True)
            
            return {"result": result}
        except Exception as e:
            print(f"     ❌ Execution failed: {e}")
            log_event(agent_id, tool_name, arguments, False, str(e))
            return {"error": str(e)}


# Run security pipeline examples
server = SecureMCPServer()

print("\n  Example 1: Valid request")
result = server.handle_request("key_devops_123", "git_status", {})
print(f"     Result: {result}")

print("\n  Example 2: Invalid API key")
result = server.handle_request("key_bad", "git_status", {})
print(f"     Result: {result}")

print("\n  Example 3: Unauthorized tool")
result = server.handle_request("key_support_456", "git_status", {})
print(f"     Result: {result}")

print("\n  Example 4: Dangerous input")
result = server.handle_request("key_devops_123", "calculate", 
                                {"expression": "2 + 2; rm -rf /"})
print(f"     Result: {result}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SECURITY SUMMARY")
print("=" * 70)
print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP SECURITY LAYERS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. AUTHENTICATION                                                   │
│     • Verify API keys/tokens                                         │
│     • Know WHO is calling                                            │
│                                                                      │
│  2. AUTHORIZATION                                                    │
│     • Check permissions                                              │
│     • Know WHAT they can do                                          │
│                                                                      │
│  3. VALIDATION                                                       │
│     • Sanitize inputs                                                │
│     • Block dangerous patterns                                       │
│     • Ensure safety                                                  │
│                                                                      │
│  4. AUDITING                                                         │
│     • Log all requests                                               │
│     • Track success/failure                                          │
│     • Accountability                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Without these layers: Anyone can do anything (DANGEROUS!)
With these layers:    Controlled, safe, accountable access
""")

print("=" * 70)
