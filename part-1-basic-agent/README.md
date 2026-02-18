# Part 1 — Basic Planning Agent

This is the simplest possible AI agent.

It does NOT use:

* Tools
* Memory
* Frameworks
* Agents libraries

It only:

```
User → LLM → Structured Plan
```

---

# 🧠 What This Agent Does

1. Takes a goal from the user
2. Sends it to a local LLM
3. Asks the LLM to break it into steps
4. Prints the structured plan

Example input:

```
Prepare a system health check for a server
```

Example output:

```
1. Check CPU usage
2. Check memory usage
3. Check disk usage
4. Review system logs
5. Generate summary report
```

---

# ⚙️ Requirements

You need:

* Python 3.8+
* Ollama installed
* A local model pulled (e.g., mistral)

---

# 🖥 Setup Instructions

## Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 — Make Sure Ollama Is Running

Test:

```bash
ollama --version
```

---

## Step 3 — Pull a Model

```bash
ollama pull mistral
```

---

## Step 4 — Run the Agent

```bash
python agent.py
```

Enter a goal and see the structured plan.

---

# 🔌 How Ollama Connects to This Script

When you install Ollama, it automatically runs a local server:

```
http://localhost:11434
```

Your Python script sends a POST request to:

```
http://localhost:11434/api/generate
```

This is how the connection happens:

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

So:

* Python sends goal
* Ollama receives it
* Ollama runs the model
* Ollama returns response
* Python prints result

No internet required.

Fully local.

---

# 🧩 How the Code Works (Simple Explanation)

Let’s break it down.

---

## 1️⃣ MODEL Variable

```python
MODEL = "mistral"
```

This tells Ollama which model to use.

If you pulled `llama3`, you can change it to:

```python
MODEL = "llama3"
```

---

## 2️⃣ planning_agent Function

```python
def planning_agent(goal):
```

This function:

* Takes user goal
* Creates a structured prompt
* Sends it to Ollama
* Returns the response

---

## 3️⃣ Prompt Engineering

```python
prompt = f"""
You are a planning AI agent.
...
"""
```

We clearly instruct the LLM:

* Break into ordered steps
* Return numbered list only

This makes output structured.

---

## 4️⃣ Sending Request to Ollama

```python
requests.post(...)
```

This sends:

* Model name
* Prompt
* Stream = False (we want full output at once)

Ollama processes it and returns JSON.

---

## 5️⃣ Extracting Response

```python
result = response.json()
return result["response"]
```

Ollama returns:

```json
{
  "response": "1. Step one\n2. Step two\n..."
}
```

We extract only the generated text.

---

## 6️⃣ Main Execution Block

```python
if __name__ == "__main__":
```

This runs when you execute:

```
python agent.py
```

It:

* Asks for input
* Calls planning_agent
* Prints result

---

# 🏗 Architecture (Block Diagram)

Here is the full flow:

```
+-------------+
|   User      |
+-------------+
        |
        v
+------------------+
|   agent.py       |
|  (Planning Agent)|
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
| Generated Plan (Text)    |
+--------------------------+
        |
        v
+------------------+
| Printed Output   |
+------------------+
```

---

# 🧠 What You Just Built

This is the foundation of:

* AutoGPT
* CrewAI
* LangGraph
* Multi-agent systems

All advanced agents start here:

```
Goal → Plan → Next Step
```

You built the core thinking unit.

---
