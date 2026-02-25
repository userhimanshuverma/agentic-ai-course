# Part 8 — Support Assistant Agent

A support assistant that **remembers you** and your issues across sessions.

---

## What This Agent Does

This is a practical support bot that:

1. **Remembers your name** - Personalizes every interaction
2. **Logs your issues** - Keeps track of problems you report
3. **Recalls past issues** - Answers "What was my last issue?"
4. **Suggests solutions** - Based on issue type and history
5. **Tracks resolutions** - Knows which issues are solved

---

## Real-World Example

```
Session 1:
You: My name is Himanshu
Assistant: Nice to meet you, Himanshu! I'll remember you.

You: I have a disk space problem
Assistant: Hi Himanshu, I see you're having disk space issues...
[Logs issue: category=disk, status=open]

[Exit and restart]

Session 2:
Assistant: Hello Himanshu! Welcome back. How can I help you today?

You: What was my last issue?
Assistant: Your last issue was about disk: I have a disk space problem
(This is still open)
```

---

## Project Structure

```
part-8-support-assistant/
├── agent.py              # Main support assistant
├── memory.py             # SupportMemory class
├── tools.py              # Support tools (disk check, fixes)
├── support_memory.json   # Auto-generated: your data
├── README.md             # This file
└── requirements.txt      # No dependencies needed!
```

---

## Requirements

- Python 3.8+
- **No external dependencies!** (uses only standard library)

---

## Setup & Run

```bash
cd part-8-support-assistant
python agent.py
```

That's it! No API keys, no models to download.

---

## How to Use

### First Time - Set Your Name

```
Assistant: Hello! I'm your support assistant. What's your name?

You: My name is Himanshu
Assistant: Nice to meet you, Himanshu! I'll remember you.
```

### Report an Issue

```
You: My disk is almost full
Assistant: Hi Himanshu, I see you're having disk space issues.
Disk Status: WARNING: Disk space is getting full...

[Issue automatically logged]
```

### Ask About Past Issues

```
You: What was my last issue?
Assistant: Your last issue was about disk: My disk is almost full
(This is still open)
```

### List All Issues

```
You: list my issues
Assistant: Found 3 issue(s)

[Your Issues]
  ○ [DISK] My disk is almost full...
  ✓ [NETWORK] WiFi keeps disconnecting...
  ○ [SLOW] Computer is running very slow...
```

### Resolve an Issue

```
You: resolve disk
Assistant: Marked issue as resolved: My disk is almost full...
```

### Check Memory Status

```
You: show memory
Assistant: Memory Status

[Memory Data]
{
  "user_name": "Himanshu",
  "total_issues": 3,
  "open_issues": 2,
  "resolved_issues": 1,
  "preferences_count": 0,
  "conversations_count": 15
}
```

---

## Issue Categories

The assistant automatically categorizes issues:

| Category | Keywords | Example |
|----------|----------|---------|
| disk | disk, space, storage, full | "My disk is full" |
| slow | slow, lag, freeze, performance | "Computer is slow" |
| network | network, wifi, internet, connection | "WiFi not working" |
| memory | memory, ram, crash | "Out of memory" |
| software | app, program, install | "App won't start" |
| hardware | hardware, device, driver | "Screen flickering" |
| general | (default) | "I need help" |

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `show memory` | Display your profile and stats |
| `list my issues` | Show all your issues with status |
| `resolve <description>` | Mark matching issue as resolved |
| `clear memory` | Delete all your data |
| `exit` | Quit the assistant |

---

## Example Session

```
============================================================
🎧 Support Assistant - I Remember You!
============================================================

I can help you with:
  • Technical issues (disk, network, performance)
  • Remember your past problems
  • Suggest solutions based on your history

Commands:
  • 'show memory' - See what I remember about you
  • 'list my issues' - See all your past issues
  • 'resolve <issue>' - Mark an issue as resolved
  • 'clear memory' - Forget everything
  • 'exit' - Quit

Assistant: Hello! I'm your support assistant. What's your name?

You: My name is Alice
Assistant: Nice to meet you, Alice! I'll remember you. How can I help today?

You: I had an issue with disk space yesterday
Assistant: Hi Alice, I see you're having disk space issues.
Disk Status: WARNING: Disk space is getting full. Consider organizing or deleting files.

Would you like me to suggest folders to organize?

Common fixes for disk issues:
1. Run Disk Cleanup utility
2. Uninstall unused programs
3. Clear browser cache

You: What was my last issue?
Assistant: Your last issue was about disk: I had an issue with disk space yesterday
(This is still open)

You: list my issues
Assistant: Found 1 issue(s)

[Your Issues]
  ○ [DISK] I had an issue with disk space yesterday...

You: resolve disk
Assistant: Marked issue as resolved: I had an issue with disk space yesterday...

You: show memory
Assistant: Memory Status

[Memory Data]
{
  "user_name": "Alice",
  "total_issues": 1,
  "open_issues": 0,
  "resolved_issues": 1,
  "preferences_count": 0,
  "conversations_count": 5
}

You: exit
Assistant: Goodbye, Alice! Take care.
```

---

## Memory Storage Format

Your data is stored in `support_memory.json`:

```json
{
  "user_profile": {
    "name": "Himanshu"
  },
  "issues": [
    {
      "id": "a1b2c3d4",
      "description": "My disk is almost full",
      "category": "disk",
      "status": "resolved",
      "created_at": "2024-01-15T10:30:00",
      "resolved_at": "2024-01-15T11:00:00",
      "resolution": "Resolved by user request"
    }
  ],
  "preferences": {},
  "conversations": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "user": "My disk is almost full",
      "assistant": "Hi Himanshu, I see you're having disk space issues..."
    }
  ]
}
```

---

## How It Works

### 1. User Recognition

```python
def _load_user(self):
    self.user_name = self.memory.get_user_name()

def _get_greeting(self):
    if self.user_name:
        return f"Hello {self.user_name}! Welcome back."
```

### 2. Issue Detection

```python
def _detect_issue(self, message):
    categories = {
        "disk": ["disk", "space", "storage"],
        "slow": ["slow", "lag", "freeze"],
        # ...
    }
    # Match keywords to category
```

### 3. Memory Query

```python
def _is_question_about_past(self, message):
    # Detect: "What was my last issue?"
    # "Previous problem", "Before", etc.
```

### 4. Persistent Storage

```python
def _save(self):
    # Save to JSON file
    # Loaded on next startup
```

---

## Test Examples

### Test 1: Name Remembering
```
You: My name is John
Assistant: Nice to meet you, John!

[Restart]

Assistant: Hello John! Welcome back.
```

### Test 2: Issue Logging
```
You: My WiFi is not working
Assistant: [Logs network issue]

You: list my issues
Assistant: Shows network issue
```

### Test 3: Context Recall
```
You: I have a disk problem
[Issue logged]

[Restart]

You: What was my last issue?
Assistant: Your last issue was about disk...
```

### Test 4: Issue Resolution
```
You: list my issues
Assistant: Shows 2 open issues

You: resolve disk
Assistant: Marked as resolved

You: list my issues
Assistant: Shows 1 open, 1 resolved
```

### Test 5: Multiple Sessions
```
Session 1:
You: My name is Alice
You: I have a slow computer issue

Session 2 (next day):
Assistant: Hello Alice! Welcome back.
You: What issues do I have?
Assistant: You have a slow computer issue (open)
```

---

## What This Demonstrates

- **User profiling** - Remembering identity
- **Issue tracking** - Logging and categorizing problems
- **Context awareness** - Understanding follow-up questions
- **Persistent state** - Data survives restarts
- **Real-world application** - Practical support bot pattern

---

## Next Steps

This is a foundation for:

- **Customer support bots** - With ticket systems
- **IT helpdesk assistants** - With knowledge bases
- **Personal tech support** - For family/friends
- **Health trackers** - Log symptoms, remember history
- **Learning assistants** - Track progress, remember weak areas

---

## No AI Required!

Unlike previous parts, this agent:
- ✅ Does NOT use Ollama
- ✅ Does NOT need internet
- ✅ Works completely offline
- ✅ Uses only Python standard library

This is **pure logic + memory** - the foundation of practical automation!
