# Part 7 — Long-Term Memory Agent

This agent has **long-term memory** that persists across sessions.

It uses vector embeddings for semantic search.

---

## What Makes It Different from Part 6?

| Feature | Part 6 | Part 7 |
|---------|--------|--------|
| Memory | Short-term only | Short-term + Long-term |
| Persistence | Lost on exit | Saved to disk |
| Search | None | Semantic similarity |
| Storage | In-memory list | JSON file + vectors |

---

## What This Agent Does

1. Takes user input
2. Stores it in **short-term** memory (conversation)
3. Extracts important facts to **long-term** memory
4. Searches past memories for relevant context
5. Uses memories to answer follow-up questions

**Example with Long-Term Memory:**

```
Session 1:
You: My favorite language is Python
Agent: Noted! I'll remember that.

[Exit and restart program]

Session 2:
You: What language do I prefer?
Agent: Your favorite language is Python.
```

---

## Project Structure

```
part-7-memory-agent(long-term-upgrade)/
├── agent.py              # Main agent with hybrid memory
├── memory.py             # Long-term memory with vectors
├── memory_short.py       # Short-term conversation memory
├── tools.py              # Available tools
├── memory_store.json     # Auto-generated: stored memories
├── README.md             # This file
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
| `show memory` | Display all memory status |
| `search memory <query>` | Search long-term memories |
| `list all memories` | List all stored memories |
| `clear memory` | Clear ALL memories (short + long) |
| `clear short term` | Clear only conversation history |

### Regular Usage

```
You: My name is Alice
Agent: Nice to meet you, Alice! (stores in long-term)

You: I work at Google
Agent: Noted! (stores in long-term)

You: show memory
Agent: (shows stored facts about you)

[Exit and restart]

You: Where do I work?
Agent: You work at Google. (retrieved from long-term memory!)
```

---

## Example Session

```
============================================================
🧠 Long-Term Memory Agent
============================================================

I remember things across sessions!

Memory commands:
  • 'show memory' - See all memory status
  • 'search memory <query>' - Search long-term memories
  • 'list all memories' - List all stored memories
  • 'clear memory' - Clear all memories
  • 'clear short term' - Clear only conversation

I can also:
  • Use tools: calculator, system, file_organizer, list_directory
  • Remember facts, preferences, and context


You: My favorite programming language is Python

🧠 Using LLM with long-term memory...

Agent:
{
  "goal": "My favorite programming language is Python",
  "action": "llm_response",
  "response": "Great choice! Python is a versatile language. I'll remember that Python is your favorite programming language."
}

You: show memory

Agent:
{
  "message": "Memory Status",
  "long_term_stats": {
    "total_memories": 1,
    "storage_file": "memory_store.json",
    "types": {
      "preference": 1
    }
  },
  "short_term_conversation": "User: My favorite programming language is Python\nAssistant: Great choice! Python is a versatile language..."
}

[Exit and restart the program]

You: What is my favorite programming language?

🧠 Using LLM with long-term memory...

Agent:
{
  "goal": "What is my favorite programming language?",
  "action": "llm_response",
  "response": "Your favorite programming language is Python."
}
```

---

## How It Works

### 1. Vector Embeddings

```python
def _simple_embedding(self, text: str) -> list:
    # Convert text to numbers (vector)
    # This simplified version uses character frequencies
    # Production: Use OpenAI, HuggingFace, or Ollama embeddings
```

Text → Numbers (vector representation)

### 2. Similarity Search

```python
def search(self, query: str) -> list:
    query_embedding = self._simple_embedding(query)
    # Find memories with similar vectors
    # Using cosine similarity
```

Find memories that are "close" to the query.

### 3. Hybrid Memory

```python
class HybridMemory:
    def __init__(self):
        self.short_term = ConversationMemory()  # Recent chat
        self.long_term = LongTermMemory()       # Persistent storage
```

Combines both memory types.

### 4. Information Extraction

```python
def _extract_and_store(self, message: str):
    # Detect patterns like:
    # - "my name is..."
    # - "I like..."
    # - "I work at..."
    # Store extracted facts in long-term memory
```

Automatically extracts important information.

---

## Architecture

```
+-------------+
|   User      |
+-------------+
        |
        v
+------------------+
|   agent.py       |
| (Long-Term       |
|  Memory Agent)   |
+------------------+
        |
        v
+--------------------------+
| 1. Check memory commands |
+--------------------------+
        |
        v
+--------------------------+
| 2. Add to short-term     |
+--------------------------+
        |
        v
+--------------------------+
| 3. Extract & store in    |
|    long-term memory      |
+--------------------------+
        |
        v
+--------------------------+
| 4. Search similar        |
|    memories              |
+--------------------------+
        |
        v
+--------------------------+
| 5. Build prompt with     |
|    context + memories    |
+--------------------------+
        |
        v
+--------------------------+
| 6. Call LLM (Ollama)     |
+--------------------------+
        |
        v
+--------------------------+
| 7. Save to disk          |
+--------------------------+
```

---

## Memory Storage Format

`memory_store.json`:
```json
{
  "memories": [
    {
      "id": "a1b2c3d4",
      "content": "my favorite language is python",
      "type": "preference",
      "embedding": [0.1, 0.2, 0.3, ...],
      "timestamp": "2024-01-15T10:30:00",
      "metadata": {}
    }
  ],
  "metadata": {
    "count": 1,
    "last_updated": "2024-01-15T10:30:00"
  }
}
```

---

## What Gets Stored Automatically

The agent extracts and stores:

| Pattern | Type | Example |
|---------|------|---------|
| "my name is..." | name | "my name is Alice" |
| "I like/prefer/love..." | preference | "I like Python" |
| "I work at..." | work | "I work at Google" |
| "I live in..." | location | "I live in NYC" |

---

## Test Examples

### Test 1: Persistent Memory (Your Actual Session)
```
Session 1:
You: My name is Alice
Agent: Hello Alice! It's nice to meet you again.

You: show memory
Agent: {
  "long_term_stats": {
    "total_memories": 1,
    "types": {"name": 1}
  }
}

[Exit and restart program]

Session 2:
You: list all memories
Agent: {
  "memories": [
    {
      "id": "8fce0ceb",
      "content": "my name is alice",
      "type": "name"
    }
  ]
}

You: What is my name?
Agent: Your name is Alice.
```

### Test 2: Memory Persists Across Restarts
```
You: My favorite color is blue
Agent: Noted! I'll remember that.

[Exit program]

[Restart next day]

You: show memory
Agent: {
  "long_term_stats": {
    "total_memories": 2,  // Name + color
    "types": {"name": 1, "preference": 1}
  }
}

You: What is my favorite color?
Agent: Your favorite color is blue.
```

### Test 3: Semantic Search
```
You: I love Italian food
Agent: Noted! Italian cuisine is delicious.

You: search memory food
Agent: (finds: "I love Italian food" with similarity score)

You: What cuisine do I like?
Agent: You love Italian food.
```

### Test 4: Memory Commands
```
You: list all memories
Agent: {
  "message": "Total memories: 2",
  "memories": [
    {"id": "8fce0ceb", "content": "my name is alice", "type": "name"},
    {"id": "a1b2c3d4", "content": "my favorite color is blue", "type": "preference"}
  ]
}

You: search memory work
Agent: (finds work-related memories or empty if none)

You: clear memory
Agent: All memories cleared.

You: list all memories
Agent: Total memories: 0
```

### Test 5: Short-term vs Long-term
```
You: Calculate 5 times 2
Agent: The product of 5 times 2 is 10.

You: list all memories
Agent: (still shows only name preference - math not stored)

You: show memory
Agent: {
  "short_term_conversation": "User: Calculate 5 times 2\nAssistant: The product...",
  // Short-term has the conversation
  "long_term_stats": {"total_memories": 1}
  // Long-term only has facts, not calculations
}

[Restart program]

You: show memory
Agent: {
  "short_term_conversation": "No recent conversation.",
  // Short-term cleared!
  "long_term_stats": {"total_memories": 1}
  // Long-term still has your name!
}
```

### Test 6: Context + Memory
```
You: I prefer Windows over Mac
Agent: Noted!

You: What operating system do I like?
Agent: You prefer Windows.

You: Why might someone prefer Windows?
Agent: (answers generally, but knows YOU prefer Windows)
```

---

## What You Just Built

This agent demonstrates:

- **Vector embeddings** for text
- **Semantic search** (similarity matching)
- **Persistent storage** (JSON file)
- **Hybrid memory** (short + long term)
- **Automatic information extraction**

This is the foundation for:

- Personal assistants
- Chatbots with memory
- Knowledge management systems
- Context-aware AI applications

---

## Next Steps

Current: **Simple embeddings** (character frequencies)

Next: **Advanced embeddings**

- OpenAI embeddings (text-embedding-ada-002)
- HuggingFace models (sentence-transformers)
- Ollama embeddings (nomic-embed-text)
- Vector databases (Chroma, Pinecone, Weaviate)

---

## Notes

- Memories are stored in `memory_store.json` in the same folder
- The simple embedding is basic but works for demonstration
- For production, replace with proper embedding models
- Memory file can be backed up, copied, or edited manually
