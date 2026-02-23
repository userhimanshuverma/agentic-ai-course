# Part 6 — Memory Agent

This agent has **short-term memory**.

It remembers the conversation history.

---

## What Makes It Different from Part 5?

| Feature | Part 5 | Part 6 |
|---------|--------|--------|
| Memory | None | Conversation history |
| Context | Per request only | Full conversation |
| Follow-up | Doesn't understand | Understands context |

---

## What This Agent Does

1. Takes user input
2. **Stores it in memory**
3. Uses memory for context in responses
4. Can reference previous messages

**Example with Memory:**

```
You: Organize files in Downloads
Agent: (organizes files)

You: What did you move?
Agent: (knows "you" refers to the previous action)
```

Without memory, the agent wouldn't understand "What did you move?"

---

## Project Structure

```
part-6-memory-agent/
├── agent.py       # Main agent with memory integration
├── memory.py      # ConversationMemory class
├── tools.py       # Available tools
├── README.md      # This file
└── requirements.txt
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

---

## How to Use

### Memory Commands

| Command | What it does |
|---------|--------------|
| `show memory` | Display conversation history |
| `clear memory` | Forget everything |

### Regular Usage

```
You: Organize files in ~/Downloads
Agent: (organizes and remembers)

You: Show memory
Agent: (shows full conversation)

You: What folder did you organize?
Agent: (answers based on memory)
```

---

## Example Session

```
============================================================
🧠 Memory Agent - I remember our conversation!
============================================================

Available commands:
  • 'show memory' - See what I remember
  • 'clear memory' - Forget everything
  • 'exit' - Quit

I can also:
  • Use tools: calculator, system, file_organizer, list_directory
  • Answer questions with context


You: What is 25 * 4?

🧠 Using LLM with memory context...

Agent:
{
  "goal": "What is 25 * 4?",
  "action": "llm_response",
  "response": "25 * 4 = 100"
}

You: Now add 50 to that

🧠 Using LLM with memory context...

Agent:
{
  "goal": "Now add 50 to that",
  "action": "llm_response",
  "response": "100 + 50 = 150"
}

You: show memory

Agent:
{
  "message": "Here's what I remember:",
  "memory": "User: What is 25 * 4?\nAssistant: 25 * 4 = 100\nUser: Now add 50 to that\nAssistant: 100 + 50 = 150\nUser: show memory"
}
```

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
|  (Memory Agent)  |
+------------------+
        |
        v
+--------------------------+
| 1. Store user message    |
|    in memory.py          |
+--------------------------+
        |
        v
+--------------------------+
| 2. Detect tool needed?   |
+--------------------------+
    |              |
   Yes             No
    |              |
    v              v
+--------+   +------------------+
| Execute|   | Build prompt with|
| Tool   |   | memory context   |
+--------+   +------------------+
    |              |
    v              v
+--------+   +------------------+
| Store  |   | Call Ollama LLM  |
| result |   | with full history|
+--------+   +------------------+
    |              |
    +------+-------+
           |
           v
+--------------------------+
| Store assistant response |
| in memory                |
+--------------------------+
           |
           v
+------------------+
| Return response  |
+------------------+
```

---

## How the Code Works

### 1. Memory Module (memory.py)

```python
class ConversationMemory:
    def __init__(self, max_history=10):
        self.history = []  # Simple list storage

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})

    def add_assistant_message(self, message):
        self.history.append({"role": "assistant", "content": message})

    def get_context_string(self):
        # Format history for prompts
        return "\n".join([f"{msg['role']}: {msg['content']}" 
                         for msg in self.history])
```

Simple in-memory list storage.

---

### 2. Storing Messages

```python
# When user speaks
MEMORY.add_user_message(goal)

# When agent responds
MEMORY.add_assistant_message(response)
```

Every interaction is stored.

---

### 3. Using Memory in Prompts

```python
context = MEMORY.get_context_string()

prompt = f"""
Previous conversation:
{context}

Current request: {goal}
"""
```

LLM sees the full conversation.

---

### 4. Memory Management

```python
def _trim_history(self):
    # Keep only last N exchanges
    while len(self.history) > self.max_history * 2:
        # Remove oldest
```

Prevents memory from growing too large.

---

## Memory vs No Memory

### Without Memory (Part 5)
```
User: Organize Downloads
Agent: Done!

User: What did you organize?
Agent: ??? (doesn't know)
```

### With Memory (Part 6)
```
User: Organize Downloads
Agent: Done!

User: What did you organize?
Agent: I organized your Downloads folder,
       moving files into categories.
```

---

## What You Just Built

This agent demonstrates:

- **Conversation history** storage
- **Context-aware** responses
- **Memory management** (trimming)
- **Tool + LLM** integration with memory

This is the foundation for:

- Chatbots
- Personal assistants
- Multi-turn agents
- Context-aware automation

---

## Test Examples

Here are example conversations to test the memory functionality:

### Test 1: Basic Memory
```
You: What is 25 * 4?
Agent: 25 * 4 = 100

You: Now add 50 to that
Agent: 100 + 50 = 150

You: show memory
Agent: (shows full conversation history)
```

### Test 2: File Organization with Follow-up
```
You: Organize files in ~/Downloads
Agent: (organizes files and shows result)

You: What folder did you organize?
Agent: (answers based on memory: Downloads)

You: How many files did you move?
Agent: (answers based on previous result)
```

### Test 3: Context Understanding
```
You: My name is Alice
Agent: Nice to meet you, Alice!

You: What is my name?
Agent: Your name is Alice.

You: show memory
Agent: (shows it remembers your name)
```

### Test 4: Multi-turn Tool Usage
```
You: Check disk usage
Agent: (shows disk info)

You: What about OS info?
Agent: (shows OS info)

You: What system commands have I asked for?
Agent: (lists: disk usage, OS info)
```

### Test 5: Clear Memory
```
You: My favorite color is blue
Agent: Noted! Your favorite color is blue.

You: What is my favorite color?
Agent: Your favorite color is blue.

You: clear memory
Agent: Memory cleared. Starting fresh conversation.

You: What is my favorite color?
Agent: (doesn't know - memory was cleared!)
```

### Test 6: Math with Context
```
You: Calculate 100 / 5
Agent: 100 / 5 = 20

You: Multiply that by 3
Agent: 20 * 3 = 60

You: Now subtract 10
Agent: 60 - 10 = 50
```

### Test 7: Directory Listing Context
```
You: List files in .
Agent: (shows current directory)

You: Are there any Python files?
Agent: (checks previous listing and answers)
```

---

## Next Steps

Current: **Short-term memory** (in-memory list)

Next: **Long-term memory** (persistent storage)

- Vector databases
- File-based storage
- Semantic search
- Permanent knowledge
