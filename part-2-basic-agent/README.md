# Part 2 — Structured JSON Planning Agent

This is an upgraded version of the basic planning agent.

It adds **structured output** using JSON format.

---

## What Makes It Different from Part 1?

| Feature | Part 1 | Part 2 |
|---------|--------|--------|
| Output | Plain text | JSON format |
| Structure | Simple list | Goal + Steps array |
| Parsing | Direct print | JSON parsing |

---

## What This Agent Does

1. Takes a goal from the user
2. Sends it to a local LLM
3. **Forces the LLM to return valid JSON**
4. Parses and displays the structured plan

Example input:

```
Prepare a system health check for a server
```

Example output:

```json
{
  "goal": "Prepare a system health check for a server",
  "steps": [
    "Check CPU usage",
    "Check memory usage",
    "Check disk usage",
    "Review system logs",
    "Generate summary report"
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

Enter a goal and see the structured JSON plan.

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
| (JSON Planning   |
|     Agent)       |
+------------------+
        |
        v
+--------------------------+
| HTTP POST Request        |
| localhost:11434          |
+--------------------------+
        |
        v
+--------------------------+
| Ollama Local Server      |
+--------------------------+
        |
        v
+--------------------------+
| Mistral Model (Local)    |
+--------------------------+
        |
        v
+--------------------------+
| JSON Response            |
| {"goal": "...",          |
|  "steps": [...]}         |
+--------------------------+
        |
        v
+------------------+
| Parsed & Printed |
| (Pretty JSON)    |
+------------------+
```

---

## How the Code Works

### 1. MODEL Variable

```python
MODEL = "mistral"
```

Tells Ollama which model to use.

---

### 2. planning_agent Function

```python
def planning_agent(goal):
```

Takes user goal and returns structured JSON plan.

---

### 3. Prompt Engineering (JSON Focus)

```python
prompt = f"""
You are a planning AI agent.
...
ALWAYS return valid JSON.
Do not return anything except JSON.
"""
```

**Key instruction:** Forces the LLM to return only valid JSON.

---

### 4. Sending Request to Ollama

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
)
```

---

### 5. Parsing JSON Response

```python
result = response.json()
raw_output = result["response"].strip()

# Try to parse as JSON
try:
    structured_output = json.loads(raw_output)
    return structured_output
except json.JSONDecodeError:
    print("Model did not return valid JSON")
    return None
```

**Key difference from Part 1:**
- Part 1: Prints raw text directly
- Part 2: Parses JSON and handles errors

---

### 6. Pretty Printing

```python
print(json.dumps(plan, indent=2))
```

Displays the JSON in a readable format.

---

## Why JSON Output Matters

```
Plain Text          JSON
    |                 |
    v                 v
Hard to parse    Easy to process
Not reusable     Can be used by
                 other programs
```

JSON output allows:
- Other code to use the plan programmatically
- Validation of the structure
- Integration with APIs and databases

---

## What You Just Built

This agent demonstrates:

- **Structured output** from LLMs
- **JSON parsing** in Python
- **Error handling** for invalid responses

This is the foundation for:

- API integrations
- Multi-step workflows
- Agent-to-agent communication

