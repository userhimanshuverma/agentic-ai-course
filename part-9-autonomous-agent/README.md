# Part 9 — Autonomous Agent (Reasoning Loop)

This agent implements a **reasoning loop**:

```
Plan → Act → Observe → Repeat until goal complete
```

---

## What Makes It Different?

| Feature | Previous Agents | Part 9 |
|---------|-----------------|--------|
| Execution | Single step | Multiple steps |
| Decision | One-shot | Iterative |
| Goal handling | Immediate response | Loop until complete |

---

## The Reasoning Loop

```
while not goal_complete:
    1. PLAN → Decide next step
    2. ACT → Execute that step
    3. OBSERVE → Check result
    4. REPEAT → If needed
```

---

## Example: "Fix High Disk Usage"

**Not just one response — a sequence:**

```
Step 1: Check disk usage
   Result: WARNING - 85% full
   → Continue

Step 2: Identify large folders
   Result: Downloads (2.5GB), Desktop (1.2GB)
   → Continue

Step 3: Organize Downloads folder
   Result: 150 files organized
   → Continue

Step 4: Re-check disk usage
   Result: GOOD - 65% full
   → Goal complete! ✅
```

---

## Project Structure

```
part-9-autonomous-agent/
├── agent.py          # Autonomous agent with reasoning loop
├── tools.py          # Available tools
├── README.md         # This file
└── requirements.txt  # No dependencies needed
```

---

## Requirements

- Python 3.8+
- **No external dependencies!**

---

## Setup & Run

```bash
cd part-9-autonomous-agent
python agent.py
```

---

## How to Use

### Example 1: Fix Disk Usage

```
🎯 Enter your goal: Fix high disk usage

🔄 Iteration 1/5
🧠 PLANNING...
🔧 Step 1: Check current disk usage to assess the situation.
   ✓ Success
   📋 WARNING: Disk space is getting full. Consider cleaning up files.
   📊 Status: warning

👁️ OBSERVING...
   Goal not complete. Continuing...

🔄 Iteration 2/5
🧠 PLANNING...
🔧 Step 2: Disk space is low. Identify large folders to organize.
   ✓ Success
   📋 Found 3 folders that could be organized.

👁️ OBSERVING...
   Goal not complete. Continuing...

🔄 Iteration 3/5
🧠 PLANNING...
🔧 Step 3: Organizing files in Downloads to free space.
   ✓ Success
   📋 Organized 150 files into 5 categories.

👁️ OBSERVING...
   Goal not complete. Continuing...

🔄 Iteration 4/5
🧠 PLANNING...
🔧 Step 4: Files organized. Re-checking disk usage to verify improvement.
   ✓ Success
   📋 Disk is healthy (65% used).
   📊 Status: good

👁️ OBSERVING...
✅ Goal complete! Stopping after 4 steps.
```

### Example 2: Simple Organization

```
🎯 Enter your goal: Organize my Downloads folder

🔄 Iteration 1/5
🧠 PLANNING...
🔧 Step 1: Organize files in ~/Downloads by type.
   ✓ Success
   📋 Organized 75 files into 4 categories.

👁️ OBSERVING...
✅ Goal complete!
```

---

## How It Works

### 1. Plan Phase

```python
def plan(self, goal, previous_results):
    # Based on goal and past results, decide next step
    if "disk" in goal and last_result["status"] == "warning":
        return Step(action="Find large folders", tool="suggest_organize")
```

### 2. Act Phase

```python
def act(self, step):
    # Execute the planned step
    tool = get_tool(step.tool)
    result = tool(**step.params)
    return result
```

### 3. Observe Phase

```python
def observe(self, step):
    # Check if goal is achieved
    if step.tool == "check_disk" and result["status"] == "good":
        return True  # Goal complete!
    return False  # Continue looping
```

---

## Architecture

```
+-------------+
|   User      |
| Enters Goal |
+-------------+
        |
        v
+------------------+
|  AutonomousAgent |
|    .run(goal)    |
+------------------+
        |
        v
+------------------+
|   REASONING LOOP |
+------------------+
        |
    +---v---+
    | PLAN  | ← Decide next step
    +---+---+
        |
    +---v---+
    |  ACT  | ← Execute tool
    +---+---+
        |
    +---v-------+
    | OBSERVE   | ← Check result
    +---+-------+
        |
    +---v------------------+
    | Goal Complete?       |
    | Yes → Exit           |
    | No  → Back to PLAN   |
    +----------------------+
```

---

## Step Lifecycle

```
Step 1: PENDING
   ↓
Step 2: RUNNING (executing tool)
   ↓
Step 3: SUCCESS or FAILED
   ↓
Step 4: OBSERVED (goal check)
```

---

## Testing

### Automated Testing

Run the included test suite:

```bash
python test_agent.py
```

This will test all functionality and report results:
- System info (single step)
- Calculator (single step)
- Organize Downloads (multi-step)
- Fix disk usage (adaptive)
- Unknown goal (fallback)

### Manual Testing

#### Test 1: Single-Step Tasks (Complete Immediately)

**System Info:**
```
🎯 Enter your goal: Check system status

Step 1: Gather system information
   ✓ Success
   📋 Running on Windows 10
👁️ OBSERVING...
✅ Goal complete! Stopping after 1 steps.
```

**Calculator:**
```
🎯 Enter your goal: Calculate 25 * 4

Step 1: Calculate: 25*4
   ✓ Success
   📋 25*4 = 100
👁️ OBSERVING...
✅ Goal complete! Stopping after 1 steps.
```

#### Test 2: Multi-Step Task (Plan → Act → Observe → Repeat)

**Organize Downloads:**
```
🎯 Enter your goal: Organize my Downloads folder

🔄 Iteration 1/5
🧠 PLANNING...
🔧 Step 1: Organize files in ~/Downloads by type.
   ✓ Success
   📋 Organized 4 files into 1 categories.
👁️ OBSERVING...

🔄 Iteration 2/5
🧠 PLANNING...
🔧 Step 2: Files organized. Re-checking disk usage to verify improvement.
   ✓ Success
   📋 Disk is healthy (72.9% used).
   📊 Status: good
👁️ OBSERVING...
✅ Goal complete! Stopping after 2 steps.
```

**Why 2 steps?**
1. First, it organizes the files
2. Then, it verifies by re-checking disk usage

#### Test 3: Adaptive Behavior (Depends on System State)

**Fix Disk Usage (Healthy Disk):**
```
🎯 Enter your goal: Fix high disk usage

Step 1: Check current disk usage
   ✓ Success
   📋 Disk is healthy (72.9% used).
   📊 Status: good
👁️ OBSERVING...
✅ Goal complete! Stopping after 1 steps.
```

*If your disk is already healthy, no action needed!*

**Fix Disk Usage (Warning - would be multi-step):**
```
🎯 Enter your goal: Fix high disk usage

Step 1: Check disk → WARNING (85% full)
Step 2: Identify large folders → Downloads (2.5GB)
Step 3: Organize Downloads → 150 files moved
Step 4: Re-check disk → GOOD (65% full) ✅
```

*If disk has warning status, agent takes corrective action*

#### Test 4: Goal Priority (Keyword Matching)

**Note:** Goals with multiple keywords match the first priority:

```
🎯 Enter your goal: Organize my Downloads folder and check disk space

Result: Checks disk first (keyword "disk" has priority)
```

To organize specifically:
```
🎯 Enter your goal: Organize my Downloads folder

Result: Organizes files, then re-checks (2 steps)
```

#### Test 5: Fallback Behavior

**Unknown Goal:**
```
🎯 Enter your goal: Do something helpful

Step 1: Gather basic system information to understand context.
   ✓ Success
   📋 Running on Windows 10
👁️ OBSERVING...
✅ Goal complete! Stopping after 1 steps.
```

*When goal doesn't match known patterns, falls back to system info*

### Understanding Test Results

| Goal | Expected Steps | Actual Depends On |
|------|----------------|-------------------|
| Check system status | 1 | Always 1 |
| Calculate X | 1 | Always 1 |
| Organize folder | 2 | Always 2+ (organize + verify) |
| Fix disk usage | 1-4 | Disk status (good=1, warning=4) |
| Unknown goal | 1 | Falls back to system_info |

### Troubleshooting

**Agent loops infinitely?**
- Check that `observe()` returns `True` for completed tools
- We fixed this for `system_info` and `calculator`

**Goal not completing?**
- The agent stops at `max_steps` (default 5)
- Check disk status or goal keywords

**Wrong tool selected?**
- Keyword priority: disk > organize > system
- Rephrase goal to emphasize desired action

---

## What You Just Built

This demonstrates:

- **Iterative execution** - Not one-shot
- **Conditional planning** - Next step depends on previous result
- **Goal verification** - Knows when to stop
- **Step tracking** - Complete execution history

This is the foundation for:

- **AutoGPT** - Autonomous task completion
- **ReAct pattern** - Reasoning + Acting
- **Multi-step workflows** - Complex task automation
- **Self-correcting agents** - Retry on failure

---

## Next Steps

Current: **Rule-based planning** (if/else logic)

Next: **LLM-based planning**

- Use Mistral to decide next steps
- Natural language goal understanding
- Adaptive planning
- Error recovery strategies

---

## No LLM Required!

This agent:
- ✅ Does NOT use Ollama/Mistral
- ✅ Works completely offline
- ✅ Uses only Python standard library
- ✅ Demonstrates core reasoning pattern

The planning logic is hardcoded for demonstration. In production, replace `plan()` with LLM calls!
