# Part 4 — System Agent

This agent can now **access the system**.

It adds **system tools** to interact with the environment.

---

## What Makes It Different from Part 3?

| Feature | Part 3 | Part 4 |
|---------|--------|--------|
| Tools | Calculator | Calculator + System |
| System Access | No | Yes (disk, memory, OS info) |
| Use Case | Math & Planning | DevOps Assistant |

---

## What This Agent Does

1. Takes a goal from the user
2. **Decides** the type of task:
   - Math problem → Calculator tool
   - System query → System tool
   - Planning task → LLM planning
3. Executes the appropriate tool
4. Returns structured output

Example system input:

```
Check disk usage on this machine
```

Example system output:

```json
{
  "goal": "Check disk usage on this machine",
  "action": "system_tool",
  "command": "disk_usage",
  "result": {
    "total_gb": 512.0,
    "used_gb": 245.5,
    "free_gb": 266.5,
    "percent_used": 47.95
  }
}
```

---

## Available System Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `disk_usage` | Check disk space | "Check disk usage" |
| `memory_info` | Check RAM usage | "Show memory info" |
| `os_info` | Get OS details | "What OS am I running?" |

---

## Requirements

- Python 3.8+
- Ollama installed
- A local model pulled (e.g., mistral)

---

## Setup Instructions

### Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 2 — Make Sure Ollama Is Running

Test:

```bash
ollama --version
```

---

### Step 3 — Pull a Model

```bash
ollama pull mistral
```

---

### Step 4 — Run the Agent

```bash
python agent.py
```

Try these examples:
- `What is 25 * 4 + 100?`
- `Check disk usage`
- `Show me memory info`
- `Plan a server setup`

---

## Architecture (Block Diagram)

```
+-------------+
|   User      |
+-------------+
        |
        v
+------------------+
|   agent.py       |
| (System Agent)   |
+------------------+
        |
        v
+--------------------------+
| 1. Detect Input Type     |
|    (Math/System/Plan)    |
+--------------------------+
        |
    +---+---+---+
    |   |   |
    v   v   v
+-------+ +--------+ +---------+
| Math  | | System | | Planning|
+-------+ +--------+ +---------+
    |         |          |
    v         v          v
+--------+ +--------+ +---------+
|calcu-  | |system_ | | Ollama  |
|lator   | |tool    | |  LLM    |
|_tool   | |        | |         |
+--------+ +--------+ +---------+
    |         |          |
    +----+----+----------+
         |
         v
+------------------+
| Print JSON Output|
+------------------+
```

---

## How the Code Works

### 1. System Tool Function

```python
def system_tool(command_type: str):
    """
    Execute safe system commands.
    Supported: disk_usage, memory_info, os_info
    """
    if command_type == "disk_usage":
        total, used, free = shutil.disk_usage("/")
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 2)
        }
```

Uses Python's built-in `shutil` and `platform` modules.

---

### 2. Keyword Detection

```python
system_keywords = ["disk", "memory", "cpu", "system", "os", "platform", "storage", "space"]
if any(keyword in goal_lower for keyword in system_keywords):
    # Route to system tool
```

Simple keyword matching to detect system queries.

---

### 3. Command Routing

```python
if "disk" in goal_lower or "storage" in goal_lower:
    result = system_tool("disk_usage")
elif "memory" in goal_lower or "ram" in goal_lower:
    result = system_tool("memory_info")
elif "os" in goal_lower or "platform" in goal_lower:
    result = system_tool("os_info")
```

Routes to the specific system command based on keywords.

---

### 4. Safe Command Execution

```python
result = subprocess.run(
    ["free", "-h"],
    capture_output=True,
    text=True,
    timeout=10
)
```

Uses `subprocess` with timeout for safe shell command execution.

---

## Decision Flow

```
User Input
    |
    v
+------------------+
| Contains system  |
| keywords?        |
+------------------+
    |         |
   Yes        No
    |         |
    v         v
+------------------+    +------------------+
| Route to System  |    | Check for math   |
| Tool             |    |                  |
+------------------+    +------------------+
                               |
                          +----+----+
                          |         |
                         Yes        No
                          |         |
                          v         v
                   +-----------+  +-----------+
                   | Calculator|  | Planning  |
                   | Tool      |  | Agent     |
                   +-----------+  +-----------+
```

---

## What You Just Built

This agent demonstrates:

- **System interaction** from an AI agent
- **Environment awareness** (disk, memory, OS)
- **Multi-tool routing** (3+ tools)

This is the foundation for:

- DevOps assistants
- System monitoring agents
- Infrastructure automation
- Server management bots

---

## Safety Note

The system tool only allows **read-only** operations:
- ✅ Disk usage (read)
- ✅ Memory info (read)
- ✅ OS info (read)
- ❌ No write operations
- ❌ No dangerous commands

Always validate and sanitize system commands in production!
