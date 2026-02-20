# Part 3 — Tool-Using Agent

This agent can **decide** whether to use a tool or plan.

It adds **tool calling** capability to the planning agent.

---

## What Makes It Different from Part 2?

| Feature | Part 2 | Part 3 |
|---------|--------|--------|
| Output | JSON plan | JSON plan OR tool result |
| Tools | None | Calculator tool |
| Decision | Always plans | Decides based on input |

---

## What This Agent Does

1. Takes a goal from the user
2. **Decides** if it's a math problem or planning task
3. If math → uses calculator tool
4. If planning → generates structured plan

Example math input:

```
What is 25 * 4 + 100?
```

Example math output:

```json
{
  "goal": "What is 25 * 4 + 100?",
  "action": "calculator_tool",
  "expression": "25*4+100",
  "result": 200
}
```

Example planning input:

```
Prepare a system health check
```

Example planning output:

```json
{
  "goal": "Prepare a system health check",
  "steps": [
    "Check CPU usage",
    "Check memory usage",
    "Check disk usage"
  ]
}
```

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

Try both math and planning goals!

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
|  (Tool Agent)    |
+------------------+
        |
        v
+--------------------------+
| 1. Detect Input Type     |
|    (Math or Plan?)       |
+--------------------------+
        |
    +---+---+
    |       |
    v       v
+-------+  +------------------+
| Math  |  | Planning         |
| Detected  | Task             |
+-------+  +------------------+
    |       |
    v       v
+----------------+  +------------------+
| Extract        |  | HTTP POST to     |
| Expression     |  | Ollama           |
+----------------+  +------------------+
        |                   |
        v                   v
+----------------+  +------------------+
| calculator_tool|  | Mistral Model    |
| (Local Python) |  | (Local LLM)      |
+----------------+  +------------------+
        |                   |
        v                   v
+----------------+  +------------------+
| Return Result  |  | Return JSON Plan |
+----------------+  +------------------+
        |                   |
        +---------+---------+
                  |
                  v
        +------------------+
        | Print JSON Output|
        +------------------+
```

---

## How the Code Works

### 1. Calculator Tool

```python
def calculator_tool(expression: str):
    """
    Safely evaluate basic math expressions.
    """
    # Only allow safe characters
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        return "Invalid characters in expression."

    result = eval(expression)
    return result
```

A local Python function that evaluates math safely.

---

### 2. Input Detection

```python
if re.search(r'[0-9]', goal) and re.search(r'[\+\-\*/]', goal):
    # Math detected → use calculator
else:
    # Planning task → use LLM
```

Simple regex pattern to detect math problems.

---

### 3. Tool Agent (Decision Maker)

```python
def tool_agent(goal: str):
    """
    Agent decides whether to:
    - Use calculator tool
    - Or generate planning steps
    """
```

The main function that routes to the right handler.

---

### 4. Expression Extraction

```python
expression = re.findall(r'[0-9+\-*/().]+', goal)
expression = "".join(expression)
```

Cleans the input to extract only valid math characters.

---

### 5. Fallback to Planning

```python
return planning_agent(goal)
```

If not math, falls back to the Part 2 planning agent.

---

## Tool vs LLM Decision Flow

```
User Input
    |
    v
+------------------+
| Contains digits? |
+------------------+
    |         |
   Yes        No
    |         |
    v         v
+------------------+    +------------------+
| Contains ops?    |    | Use Planning     |
| (+, -, *, /)     |    | Agent (LLM)      |
+------------------+    +------------------+
    |         |
   Yes        No
    |         |
    v         v
+------------------+    +------------------+
| Use Calculator   |    | Use Planning     |
| Tool (Local)     |    | Agent (LLM)      |
+------------------+    +------------------+
```

---

## What You Just Built

This agent demonstrates:

- **Tool calling** from an agent
- **Decision making** (router pattern)
- **Local tools** (no API needed)

This is the foundation for:

- Multi-tool agents
- Function calling
- ReAct pattern (Reasoning + Acting)

