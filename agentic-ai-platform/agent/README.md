# 🤖 Agentic AI Platform

A production-ready, MCP-enabled Agentic AI system that runs entirely locally using Ollama and Mistral.

## What is This?

This is an autonomous AI agent that can:
- **Plan** how to achieve goals
- **Execute** tasks using tools
- **Reflect** on results and learn

All running locally on your machine with **zero cloud dependencies**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    CLI      │  │   FastAPI   │  │      MCP Client         │  │
│  │   (main.py) │  │   Server    │  │                         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          └────────────────┴─────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AGENT CORE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   PLANNER    │  │   EXECUTOR   │  │     REFLECTOR        │   │
│  │              │  │              │  │                      │   │
│  │ • Breaks     │  │ • Runs tools │  │ • Analyzes results   │   │
│  │   goals into │  │ • Handles    │  │ • Learns from        │   │
│  │   steps      │  │   errors     │  │   mistakes           │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │                 │                     │
          └─────────────────┴─────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
┌──────────────────────┐      ┌──────────────────────┐
│     LLM LAYER        │      │     MEMORY SYSTEM    │
│  ┌────────────────┐  │      │  ┌────────────────┐  │
│  │    Ollama      │  │      │  │  Short-term    │  │
│  │   (Mistral)    │  │      │  │  (In-memory)   │  │
│  │                │  │      │  └────────────────┘  │
│  │ • Plans        │  │      │                      │
│  │ • Reflects     │  │      │  ┌────────────────┐  │
│  │ • Structured   │  │      │  │  Long-term     │  │
│  │   JSON output  │  │      │  │  (ChromaDB)    │  │
│  └────────────────┘  │      │  └────────────────┘  │
└──────────────────────┘      └──────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│                    MCP SERVER / TOOLS                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Calculator│ │ Code     │ │ File     │ │ Web      │         │
│  │          │ │ Executor │ │ Tool     │ │ Search   │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐                                    │
│  │ System   │ │ (Add     │                                    │
│  │ Info     │ │  more...)│                                    │
│  └──────────┘ └──────────┘                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Install Ollama

```bash
# Download from https://ollama.ai
# Or use command line:
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Mistral Model

```bash
ollama pull mistral
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Agent

```bash
# Check system health
python main.py --health

# Execute a goal
python main.py --goal "Calculate 15 * 23"

# Run with detailed output
python main.py --goal "Get system information" --detail

# Start API server
python main.py --api
```

---

## Project Structure

```
agentic-ai-platform/agent/
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image
├── docker-compose.yml           # Full stack with Ollama + ChromaDB
│
├── agentic_ai/                  # Main package
│   ├── agent/                   # Core agent logic
│   │   ├── core.py             # Main agent orchestrator
│   │   ├── llm.py              # Ollama/Mistral integration
│   │   ├── planner.py          # Plan generation
│   │   ├── executor.py         # Step execution
│   │   ├── reflector.py        # Reflection & analysis
│   │   └── memory.py           # Short & long-term memory
│   │
│   ├── mcp_server/              # MCP implementation
│   │   ├── server.py           # MCP server (stdio/HTTP)
│   │   ├── registry.py         # Tool registry
│   │   └── tools/              # Available tools
│   │       ├── calculator.py
│   │       ├── code_executor.py
│   │       ├── file_tool.py
│   │       ├── web_search.py
│   │       └── system_tool.py
│   │
│   ├── api/                     # FastAPI REST API
│   │   └── server.py
│   │
│   └── utils/                   # Utilities
│       ├── config.py           # Configuration
│       ├── logger.py           # Structured logging
│       └── schema.py           # Pydantic schemas
│
├── logs/                        # Execution logs (JSON)
└── safe_workspace/              # File tool sandbox
```

---

## Available Tools

### 1. Calculator
Mathematical expression evaluator with safety checks.

```python
# Example usage via agent
goal = "Calculate sqrt(144) + 10"
# Result: 22.0
```

**Supported operations:**
- Basic: `+`, `-`, `*`, `/`, `^` (power)
- Functions: `sqrt()`, `log()`, `sin()`, `cos()`, `tan()`
- Constants: `pi`, `e`

### 2. Code Executor
Sandboxed Python code execution.

```python
# Example usage via agent
goal = "Write a Python script to calculate factorial of 5"
# Code runs in restricted environment
```

**Allowed:** `print`, `math`, `random`, `datetime`, `json`, `re`, `statistics`

### 3. File Tool
Safe file operations in sandboxed directory.

```python
# Example usage via agent
goal = "Create a file called report.txt with today's date"
# File created in safe_workspace/
```

**Operations:** `read`, `write`, `list`, `delete`

### 4. Web Search
Mock web search for demonstration.

```python
# Example usage via agent
goal = "Search for Python tutorials"
# Returns mock search results
```

### 5. System Tool
System information retrieval.

```python
# Example usage via agent
goal = "Check CPU and memory usage"
# Returns platform, CPU, memory info
```

---

## How It Works

### The Agent Loop

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│  Plan   │────▶│ Execute │────▶│ Reflect │
│  Goal   │     │         │     │         │     │         │
└─────────┘     └────┬────┘     └────┬────┘     └────┬────┘
                     │               │               │
                     ▼               ▼               ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │  LLM     │    │  Tools   │    │  LLM     │
              │ generates│    │  execute │    │ analyzes │
              │  steps   │    │  steps   │    │  results │
              └──────────┘    └──────────┘    └──────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │  Report  │
                                            │  saved   │
                                            └──────────┘
```

### Example Execution Flow

**Goal:** "Calculate the area of a circle with radius 5"

1. **Planning Phase**
   ```json
   {
     "goal": "Calculate the area of a circle with radius 5",
     "steps": [
       {
         "step_number": 1,
         "description": "Use calculator to compute pi * r^2",
         "tool_call": {
           "tool_name": "calculator",
           "arguments": {"expression": "pi * 5^2"}
         },
         "expected_output": "78.54"
       }
     ]
   }
   ```

2. **Execution Phase**
   - Calls calculator tool with `pi * 5^2`
   - Gets result: `78.5398163397`

3. **Reflection Phase**
   - Analyzes if goal was achieved
   - Generates summary and lessons learned

4. **Output**
   ```
   ✅ Success: True
   📊 Result: 78.54
   📝 Summary: Successfully calculated circle area
   💾 Report saved to: execution_report_abc123.json
   ```

---

## Usage Examples

### CLI Examples

```bash
# Basic calculation
python main.py --goal "Calculate 25 * 48"

# System information
python main.py --goal "Check my system CPU and memory"

# File operations
python main.py --goal "Create a file called todo.txt with my tasks"

# Code execution
python main.py --goal "Write a Python script to generate random numbers"

# Detailed output
python main.py --goal "Calculate fibonacci sequence up to 100" --detail

# Interactive mode
python main.py
```

### API Examples

Start the API server:
```bash
python main.py --api
```

Then use curl or any HTTP client:

```bash
# Submit a goal
curl -X POST http://localhost:8000/goal \
  -H "Content-Type: application/json" \
  -d '{"goal": "Calculate 15 * 23"}'

# Get detailed execution
curl -X POST http://localhost:8000/goal/detail \
  -H "Content-Type: application/json" \
  -d '{"goal": "Get system information"}'

# Check health
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools

# View logs
curl http://localhost:8000/logs
```

### Python API

```python
from agentic_ai.agent import agent

# Run a goal
report = agent.run_goal("Calculate the factorial of 10")

print(f"Success: {report.success}")
print(f"Result: {report.results[0].output}")
print(f"Time: {report.total_execution_time_ms}ms")

# Check health
health = agent.health_check()
print(f"LLM Available: {health['llm_available']}")
```

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Start everything (Agent + Ollama + ChromaDB)
docker-compose up -d

# View logs
docker-compose logs -f agent

# Stop everything
docker-compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Agent API | 8000 | FastAPI server |
| Ollama | 11434 | LLM inference |
| ChromaDB | 8001 | Vector database |

---

## Configuration

Environment variables (all optional):

```bash
# LLM Configuration
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="mistral"
export LLM_TIMEOUT="120"

# API Configuration
export API_HOST="0.0.0.0"
export API_PORT="8000"

# Memory Configuration
export CHROMA_DB_PATH="./chroma_db"
export MAX_SHORT_TERM_MEMORY="10"

# Logging
export LOG_LEVEL="INFO"
export LOG_FILE="./logs/agent.log"

# Security
export SAFE_DIRECTORY="./safe_workspace"
```

---

## Architecture Deep Dive

### 1. Planner (`agent/planner.py`)

Uses LLM to break goals into steps:

```python
plan = planner.create_plan(
    goal="Calculate circle area",
    goal_id="uuid-here"
)
# Returns: Plan with steps and tool calls
```

### 2. Executor (`agent/executor.py`)

Executes each step and calls tools:

```python
result = executor.execute_step(step, goal_id)
# Returns: StepResult with output/error
```

### 3. Reflector (`agent/reflector.py`)

Analyzes execution results:

```python
reflection = reflector.reflect(goal, plan, results, goal_id)
# Returns: Reflection with success, summary, lessons
```

### 4. Memory (`agent/memory.py`)

Two-tier memory system:

**Short-term:** In-memory buffer (last 10 items)
**Long-term:** ChromaDB with embeddings for retrieval

### 5. LLM (`agent/llm.py`)

Ollama integration with:
- Structured JSON output
- Retry logic
- Token tracking

### 6. MCP Server (`mcp_server/`)

Implements Model Context Protocol:
- Tool registry
- JSON-RPC interface
- Stdio and HTTP transports

---

## Testing

### Run All Tests

```bash
# Test individual tools
python -c "from agentic_ai.mcp_server.tools.calculator import calculator_tool; print(calculator_tool.execute({'expression': '2+2'}))"

# Test agent
python main.py --goal "Calculate 2 + 2" --detail

# Health check
python main.py --health
```

### Example Test Script

```python
#!/usr/bin/env python3
"""Test all tools."""

from agentic_ai.mcp_server.tools import *

print("=== Testing Calculator ===")
print(calculator_tool.execute({"expression": "sqrt(16) + 10"}))

print("\n=== Testing Code Executor ===")
print(code_executor_tool.execute({"code": "print('Hello from sandbox')"}))

print("\n=== Testing File Tool ===")
print(file_tool.execute({"operation": "write", "filename": "test.txt", "content": "Hello"}))
print(file_tool.execute({"operation": "read", "filename": "test.txt"}))

print("\n=== Testing Web Search ===")
print(web_search_tool.execute({"query": "python programming"}))

print("\n=== Testing System Tool ===")
print(system_tool.execute({"info_type": "platform"}))
```

---

## Troubleshooting

### Ollama Connection Error

```
Error: Cannot connect to Ollama at http://localhost:11434
```

**Fix:**
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags

# Pull mistral if not already
ollama pull mistral
```

### ChromaDB Not Available

```
Warning: ChromaDB not available. Long-term memory disabled.
```

**Fix:** This is optional. Install with:
```bash
pip install chromadb sentence-transformers
```

### Tool Execution Failed

Check logs:
```bash
# View recent logs
tail -f logs/agent.log

# On Windows
Get-Content logs/agent.log -Tail 20
```

---

## Extending the Platform

### Adding a New Tool

1. Create tool file in `mcp_server/tools/`:

```python
# mcp_server/tools/my_tool.py
from typing import Any, Dict

class MyTool:
    name = "my_tool"
    description = "Does something useful"
    
    input_schema = {
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        param = arguments.get("param")
        # Do something
        return {
            "content": [{"type": "text", "text": f"Result: {param}"}],
            "isError": False
        }

my_tool = MyTool()
```

2. Register in `mcp_server/registry.py`:

```python
from .tools.my_tool import my_tool

# In _register_default_tools():
self.register(my_tool)
```

3. Test:

```bash
python main.py --goal "Use my_tool with param='test'"
```

---

## License

MIT License - Free for personal and commercial use.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## Support

- 📖 Documentation: This README
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Made with ❤️ for the AI community**
