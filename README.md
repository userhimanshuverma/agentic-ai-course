# 🚀 Agentic AI Course

### (From First Principles → Production Systems)

Everyone is talking about **Agentic AI**.

Few actually understand how agents work.

This repository is my journey of building AI agents:

* From scratch
* Without magic frameworks
* Without hiding behind abstractions
* Step by step

This is part of my LinkedIn series where I break down Agentic AI in the simplest way possible.

---

# 🧠 What Is This About?

We are not building chatbots.

We are building **agents that think, plan, and act.**

We will go from:

```
User → LLM → Output
```

To:

```
User → Agent → Planning → Tools → Memory → Execution → Reflection → Production
```

No hype.
Just real systems.

---

# 📚 What We Will Build

* ✅ Basic planning agents
* ✅ Tool-using agents
* ✅ Memory systems
* ✅ Autonomous multi-step agents
* ✅ MCP servers
* ✅ Production-grade architecture
* ✅ Deployment-ready agents

Each folder contains simple code + clear explanations.

---

# ⚙️ Before Running the Code

You need **one of the following**:

---

## 🟢 Option 1 — Use a Cloud LLM (API Key Required)

If using OpenAI / Anthropic / etc:

### Windows (PowerShell)

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

Restart terminal after setting it.

---

### Linux / macOS

```bash
export OPENAI_API_KEY="your_api_key_here"
```

You can add this to your `.bashrc` or `.zshrc` for persistence.

---

## 🟢 Option 2 — Run an Open-Source Model Locally (Recommended 🔥)

No API cost.
No external dependency.
Fully local.

We will use Ollama.

---

# 🖥 Install Ollama (Local LLM Setup)

We use **Ollama** to run open-source models locally.

---

## 🪟 Windows Setup

### Step 1 — Download Ollama

Download installer from:

👉 [https://ollama.com](https://ollama.com)

Install it normally.

Verify installation:

```bash
ollama --version
```

---

### Step 2 — Pull a Model

Example:

```bash
ollama pull mistral
```

Or:

```bash
ollama pull llama3
```

---

### Step 3 — Test It

```bash
ollama run mistral
```

If it responds — your local LLM is ready.

---

## 🐧 Linux Setup

### Step 1 — Install Ollama

Run:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify installation:

```bash
ollama --version
```

---

### Step 2 — Pull a Model

```bash
ollama pull mistral
```

Or:

```bash
ollama pull llama3
```

---

### Step 3 — Test It

```bash
ollama run mistral
```

If you get a response — you're good to go.

---

# 🏗 Repository Structure

```
agentic-ai-course/
  part-1-basic-agent/
  part-2-tool-agent/
  part-3-memory-agent/
  part-4-autonomous-agent/
```

Each part evolves the agent further.

We start simple.
Then we scale.

---

# 🎯 Why This Repository Exists

Because most tutorials:

* Show frameworks
* Hide internals
* Skip fundamentals

This repo focuses on:

* How agents think
* How they plan
* How prompts are structured
* How tools are integrated
* How real production systems are built

---

# 🔥 Who Is This For?

* Engineers exploring AI agents
* Backend developers moving into AI
* ML engineers building production systems
* Anyone tired of shallow tutorials

---

# 📢 Follow the LinkedIn Series

I’m documenting everything publicly.

Every part.
Every mistake.
Every improvement.

This is not just a repo.

It’s a build-in-public journey.

---

If you’re building agents too —
Fork it.
Improve it.
Let’s push this space forward.

---

