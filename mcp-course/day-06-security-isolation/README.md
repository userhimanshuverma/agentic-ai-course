# Day 6: Security & Isolation

## 🎯 The Security Problem

When you let AI agents use tools, you're giving them power. Power needs boundaries.

### The Danger Scenario

```
Agent: "Delete all files in production"
Tool:  "OK, deleted!"
Result: 💥 Company offline
```

**Without security:**
- Any agent can do anything
- No audit trail
- No permission checks
- No isolation

**With MCP security:**
- Controlled access
- Full audit logs
- Permission validation
- Sandboxed execution

## 🛡️ MCP Security Model

### Four Layers of Protection

```
┌─────────────────────────────────────────────────────────┐
│              MCP SECURITY LAYERS                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 1: AUTHENTICATION                                │
│  "Who are you?"                                         │
│  ├─ API keys                                            │
│  ├─ Tokens                                              │
│  └─ Certificates                                        │
│                                                          │
│  Layer 2: AUTHORIZATION                                 │
│  "What can you do?"                                     │
│  ├─ Tool permissions                                    │
│  ├─ Resource access                                     │
│  └─ Rate limits                                         │
│                                                          │
│  Layer 3: VALIDATION                                    │
│  "Is this request safe?"                                │
│  ├─ Input sanitization                                  │
│  ├─ Schema validation                                   │
│  └─ Parameter bounds                                    │
│                                                          │
│  Layer 4: AUDITING                                      │
│  "What happened?"                                       │
│  ├─ Request logging                                     │
│  ├─ Response logging                                    │
│  └─ Error logging                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔐 Layer 1: Authentication

### API Key Authentication

```python
# Server-side authentication
class MCPServer:
    def __init__(self):
        self.valid_api_keys = {
            "agent_devops_123": "devops_agent",
            "agent_support_456": "support_agent"
        }
    
    def authenticate(self, request_headers):
        api_key = request_headers.get("X-API-Key")
        
        if api_key not in self.valid_api_keys:
            raise AuthenticationError("Invalid API key")
        
        return self.valid_api_keys[api_key]
```

### Client-side Authentication

```python
# Client sends API key with every request
class MCPClient:
    def __init__(self, server_url, api_key):
        self.server_url = server_url
        self.api_key = api_key
    
    def call_tool(self, tool_name, params):
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.server_url,
            headers=headers,
            json={"method": "tools/call", "params": {"name": tool_name, "arguments": params}}
        )
        
        return response.json()
```

## 📝 Layer 2: Authorization

### Permission System

```python
# Define who can do what
PERMISSIONS = {
    "devops_agent": {
        "tools": ["git_*", "aws_*", "docker_*"],
        "resources": ["config/*", "logs/*"],
        "rate_limit": 100  # requests per minute
    },
    "support_agent": {
        "tools": ["jira_*", "slack_*", "email_*"],
        "resources": ["tickets/*", "docs/*"],
        "rate_limit": 50
    },
    "analyst_agent": {
        "tools": ["sql_query", "chart_generate"],
        "resources": ["data/*", "reports/*"],
        "rate_limit": 20
    }
}
```

### Authorization Check

```python
class MCPServer:
    def authorize_tool_call(self, agent_id, tool_name):
        """Check if agent can use this tool"""
        agent_perms = PERMISSIONS.get(agent_id, {})
        allowed_tools = agent_perms.get("tools", [])
        
        # Check if tool matches any allowed pattern
        for pattern in allowed_tools:
            if self._matches_pattern(tool_name, pattern):
                return True
        
        raise AuthorizationError(
            f"Agent '{agent_id}' not authorized to use tool '{tool_name}'"
        )
    
    def _matches_pattern(self, tool_name, pattern):
        """Simple pattern matching (e.g., 'git_*' matches 'git_status')"""
        if pattern.endswith("*"):
            return tool_name.startswith(pattern[:-1])
        return tool_name == pattern
```

## ✅ Layer 3: Validation

### Input Sanitization

```python
class MCPServer:
    def validate_tool_input(self, tool_name, arguments):
        """Validate tool inputs before execution"""
        
        # Dangerous patterns to block
        dangerous_patterns = [
            "rm -rf /",
            "DROP TABLE",
            "DELETE FROM",
            ";",  # Command injection
            "|",  # Pipe injection
        ]
        
        # Convert arguments to string for checking
        args_str = json.dumps(arguments)
        
        for pattern in dangerous_patterns:
            if pattern.lower() in args_str.lower():
                raise ValidationError(
                    f"Dangerous pattern detected: {pattern}"
                )
        
        return True
```

### Schema Validation

```python
from jsonschema import validate, ValidationError

class MCPServer:
    def validate_against_schema(self, tool_name, arguments):
        """Validate arguments match tool's input schema"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValidationError(f"Tool not found: {tool_name}")
        
        schema = tool.get("inputSchema", {})
        
        try:
            validate(instance=arguments, schema=schema)
        except ValidationError as e:
            raise ValidationError(f"Invalid input: {e.message}")
        
        return True
```

### Parameter Bounds

```python
class MCPServer:
    def validate_bounds(self, tool_name, arguments):
        """Ensure parameters are within safe bounds"""
        
        # Example: Limit query results
        if tool_name == "sql_query":
            if arguments.get("limit", 100) > 1000:
                raise ValidationError("Query limit cannot exceed 1000")
        
        # Example: Limit file size
        if tool_name == "file_upload":
            if arguments.get("size", 0) > 100 * 1024 * 1024:  # 100MB
                raise ValidationError("File size cannot exceed 100MB")
        
        return True
```

## 📊 Layer 4: Auditing

### Request Logging

```python
import logging
from datetime import datetime

# Setup audit logger
audit_logger = logging.getLogger("mcp_audit")
audit_logger.setLevel(logging.INFO)

# Log to file
handler = logging.FileHandler("mcp_audit.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(message)s'
))
audit_logger.addHandler(handler)

class MCPServer:
    def log_request(self, agent_id, tool_name, arguments, result):
        """Log every tool execution"""
        audit_logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "success": not result.get("isError", False),
            "response_size": len(str(result))
        }))
```

### Audit Log Example

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_id": "devops_agent",
  "tool_name": "git_push",
  "arguments": {"branch": "main"},
  "success": true,
  "response_size": 256
}
```

## 🏗️ Complete Security Implementation

### Secure Server

```python
class SecureMCPServer:
    def __init__(self):
        self.tools = {}
        self.permissions = PERMISSIONS
        self.request_counts = {}  # For rate limiting
    
    def handle_request(self, request, headers):
        """Full security pipeline"""
        
        # 1. AUTHENTICATION
        try:
            agent_id = self.authenticate(headers)
        except AuthenticationError as e:
            return self._error_response(str(e), 401)
        
        # 2. RATE LIMITING
        if not self._check_rate_limit(agent_id):
            return self._error_response("Rate limit exceeded", 429)
        
        # 3. AUTHORIZATION
        tool_name = request.get("params", {}).get("name")
        try:
            self.authorize(agent_id, tool_name)
        except AuthorizationError as e:
            self._log_security_event("UNAUTHORIZED", agent_id, tool_name)
            return self._error_response(str(e), 403)
        
        # 4. VALIDATION
        arguments = request.get("params", {}).get("arguments", {})
        try:
            self.validate(tool_name, arguments)
        except ValidationError as e:
            return self._error_response(str(e), 400)
        
        # 5. EXECUTION
        result = self.execute_tool(tool_name, arguments)
        
        # 6. AUDIT
        self.audit_log(agent_id, tool_name, arguments, result)
        
        return self._success_response(result)
    
    def authenticate(self, headers):
        """Verify identity"""
        api_key = headers.get("X-API-Key")
        if not api_key or api_key not in VALID_API_KEYS:
            raise AuthenticationError("Invalid API key")
        return VALID_API_KEYS[api_key]
    
    def authorize(self, agent_id, tool_name):
        """Check permissions"""
        agent_perms = self.permissions.get(agent_id, {})
        allowed = agent_perms.get("tools", [])
        
        for pattern in allowed:
            if self._matches(tool_name, pattern):
                return True
        
        raise AuthorizationError(f"Not authorized: {tool_name}")
    
    def validate(self, tool_name, arguments):
        """Validate inputs"""
        # Check for dangerous patterns
        self._check_dangerous_patterns(arguments)
        
        # Validate schema
        self._validate_schema(tool_name, arguments)
        
        # Check bounds
        self._validate_bounds(tool_name, arguments)
    
    def audit_log(self, agent_id, tool_name, arguments, result):
        """Record execution"""
        audit_logger.info(json.dumps({
            "agent": agent_id,
            "tool": tool_name,
            "args": arguments,
            "success": not result.get("isError"),
            "timestamp": datetime.utcnow().isoformat()
        }))
```

## 🔒 Isolation Strategies

### Process Isolation

```python
import subprocess
import tempfile
import os

class IsolatedToolExecutor:
    """Execute tools in isolated environment"""
    
    def execute(self, tool_func, arguments):
        # Create temporary workspace
        with tempfile.TemporaryDirectory() as workspace:
            # Run in subprocess with limited resources
            result = subprocess.run(
                ["python", "-c", tool_code],
                cwd=workspace,
                capture_output=True,
                timeout=30,  # Kill after 30 seconds
                env={"PATH": "/usr/bin"}  # Limited environment
            )
            
            return {
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode(),
                "returncode": result.returncode
            }
```

### Resource Limits

```python
import resource

def set_resource_limits():
    """Limit CPU and memory usage"""
    # Max 10 seconds CPU time
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    
    # Max 512MB memory
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    
    # Max 100 file descriptors
    resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
```

## 🎯 Security Checklist

### For Production MCP Servers:

```
[ ] Authentication
    [ ] API keys or tokens required
    [ ] Keys rotated regularly
    [ ] Invalid keys rejected immediately

[ ] Authorization
    [ ] Permission system implemented
    [ ] Agents can only access allowed tools
    [ ] Rate limiting enforced

[ ] Validation
    [ ] Input sanitization
    [ ] Schema validation
    [ ] Dangerous patterns blocked
    [ ] Parameter bounds checked

[ ] Auditing
    [ ] All requests logged
    [ ] All responses logged
    [ ] Errors logged
    [ ] Logs retained for compliance

[ ] Isolation
    [ ] Tools run in sandbox
    [ ] Resource limits enforced
    [ ] Network access restricted
    [ ] Filesystem access limited
```

## 🎓 Key Takeaway

**MCP Security = Defense in Depth**

1. **Authenticate** - Know who is calling
2. **Authorize** - Know what they can do
3. **Validate** - Ensure requests are safe
4. **Audit** - Record everything for accountability
5. **Isolate** - Contain potential damage

Without these layers, you're giving AI agents unlimited power. With them, you have controlled, accountable, safe AI tool usage.

## 🚀 What's Next?

Tomorrow: **Server Architecture** - How to build the actual MCP server infrastructure.

---

**Remember:** Security isn't optional in production. Start with authentication, add authorization, validate everything, and log it all.
