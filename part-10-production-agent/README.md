# Part 10 — Production Autonomous Agent

A **production-grade** autonomous agent with safety controls, retry logic, and comprehensive error handling.

---

## What Makes It Production-Grade?

| Feature | Part 9 | Part 10 |
|---------|--------|---------|
| Basic loop | ✅ | ✅ |
| Real actions | ✅ | ✅ |
| **Retry logic** | ❌ | ✅ |
| **Timeout control** | ❌ | ✅ |
| **Error recovery** | ❌ | ✅ |
| **Execution logging** | ❌ | ✅ |
| **Safety limits** | Basic | Comprehensive |
| **Metrics tracking** | ❌ | ✅ |

---

## The Production Loop

```python
while not goal_complete and step < max_steps and not timeout:
    try:
        plan()
        result = act_with_retry_and_timeout()
        goal_complete = observe(result)
    except Exception:
        recovery_strategy()
```

### Safety Controls:
- **Step limit**: Max 10 steps (configurable)
- **Time limit**: Max 5 minutes (configurable)
- **Retry limit**: 3 retries with exponential backoff
- **Tool timeout**: 30 seconds per tool call
- **Comprehensive logging**: All actions logged

---

## Architecture

### High-Level Flow

```
User Goal
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION AGENT                          │
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │    PLAN     │───▶│     ACT     │───▶│   OBSERVE   │     │
│   │             │    │             │    │             │     │
│   │ Select tool │    │ Execute with│    │ Check goal  │     │
│   │ & params    │    │ retry logic │    │ completion  │     │
│   └─────────────┘    └──────┬──────┘    └──────┬──────┘     │
│                             │                  │            │
│                    ┌────────┴────────┐         │            │
│                    │  SAFETY LAYER   │         │            │
│                    │  • Step limit   │         │            │
│                    │  • Time limit   │         │            │
│                    │  • Tool timeout │         │            │
│                    │  • Max retries  │         │            │
│                    └─────────────────┘         │            │
│                                                │            │
│   ◄────────────────────────────────────────────┘            │
│   (Loop until goal_complete OR safety limit reached)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Execution Report (steps, metrics, conclusion)
```

### Component Layers

```
┌─────────────────────────────────────────┐
│         Production Agent                │
├─────────────────────────────────────────┤
│  SAFETY LAYER                           │
│  ├── Step limit (10 max)                │
│  ├── Time limit (300s max)              │
│  ├── Tool timeout (30s per call)        │
│  └── Retry limit (3 attempts)           │
├─────────────────────────────────────────┤
│  EXECUTION LAYER                        │
│  ├── Retry with exponential backoff     │
│  │   (1s → 2s → 4s → 8s)               │
│  ├── Timeout protection                 │
│  └── Error classification               │
├─────────────────────────────────────────┤
│  RECOVERY LAYER                         │
│  ├── Alternative tool strategies        │
│  ├── Graceful degradation               │
│  └── Partial success handling           │
├─────────────────────────────────────────┤
│  OBSERVABILITY LAYER                    │
│  ├── Execution logging (agent.log)      │
│  ├── Real-time metrics tracking         │
│  └── Performance monitoring             │
└─────────────────────────────────────────┘
```

---

## Project Structure

```
part-10-production-agent/
├── agent.py              # Production agent with safety controls
├── tools.py              # Safe, logging-enabled tools
├── agent_execution.log   # Auto-generated execution log
├── README.md             # This file
└── requirements.txt      # No dependencies needed
```

---

## Requirements

- Python 3.8+
- **No external dependencies!**

---

## Setup & Run

```bash
cd part-10-production-agent
python agent.py
```

---

## Features

### 1. Goal-Driven Autonomy

The agent doesn't stop until the goal is achieved:

```
Goal: "Reduce high disk usage"

Step 1: Check disk → WARNING (85%)
Step 2: Find large folders → Downloads (2.5GB)
Step 3: Organize Downloads → 150 files moved
Step 4: Re-check disk → GOOD (65%) ✅
```

### 2. Retry Logic with Exponential Backoff

If a tool fails, the agent retries:

```
Step 3: Organize files
   Attempt 1: Failed (Permission denied)
   ↻ Retrying in 1s...
   Attempt 2: Failed (Permission denied)
   ↻ Retrying in 2s...
   Attempt 3: Success! ✅
```

Backoff: 1s → 2s → 4s → 8s...

### 3. Timeout Protection

Every tool call has a timeout:

```python
# Tool timeout: 30 seconds
result = execute_with_timeout(tool, params, timeout=30)
```

Prevents hanging on slow operations.

### 4. Error Recovery

When a tool fails, the agent tries alternatives:

```
Step 2: File organizer failed
Recovery: Try suggest_organize instead
Step 3: Suggest organize → Success ✅
```

### 5. Execution Logging

All actions are logged to `agent_execution.log`:

```
2024-01-15 10:30:00 - INFO - Agent starting
2024-01-15 10:30:01 - INFO - Step 1: check_disk succeeded in 45ms
2024-01-15 10:30:02 - WARNING - Step 2: file_organizer failed, retrying...
2024-01-15 10:30:05 - INFO - Goal complete after 4 steps
```

### 6. Metrics Tracking

Real-time execution metrics:

```
Total Steps: 4
Successful: 4
Failed: 0
Retried: 1
Success Rate: 100%
Total Time: 2.3s
```

---

## Usage Examples

### Scenario 1: Simple Single-Step (System Info)

**Goal:** Check system status  
**Expected:** Completes in 1 step

```
🎯 Enter your goal: Check system status

🚀 Production Autonomous Agent
⚙️  Safety Limits: 10 steps, 300s timeout

🔄 Step 1/10
🧠 PLANNING...
   Action: Gather system information.
   Tool: system_info
⚡ EXECUTING...
   ✓ Success (95ms)
👁️  OBSERVING...
✅ GOAL COMPLETE! Stopping after 1 step.

📊 EXECUTION REPORT
===================
Goal: Check system status
Complete: ✅ Yes
Steps: 1/10
Time: 0.1s
Success Rate: 100%

Conclusion: System information gathered successfully.
```

---

### Scenario 2: Multi-Step with Verification (Disk Fix)

**Goal:** Fix high disk usage  
**Disk Status:** WARNING (85% full)  
**Expected:** 4 steps (check → suggest → organize → verify)

```
🎯 Enter your goal: Fix high disk usage

🔄 Step 1/4
🧠 PLANNING...
   Action: Check current disk usage to assess the situation.
   Tool: check_disk
⚡ EXECUTING...
   ✓ Success (45ms)
   Result: WARNING (85% used)
👁️  OBSERVING...
   Status: warning - need to take action

🔄 Step 2/4
🧠 PLANNING...
   Action: Disk status is warning. Identify large folders to organize.
   Tool: suggest_organize
⚡ EXECUTING...
   ✓ Success (120ms)
   Found: Downloads (2.5GB)
👁️  OBSERVING...
   Found folders to organize

🔄 Step 3/4
🧠 PLANNING...
   Action: Organize files in Downloads (2500 MB)
   Tool: file_organizer
⚡ EXECUTING...
   ✓ Success (850ms)
   Moved: 150 files organized
👁️  OBSERVING...
   Files organized, need verification

🔄 Step 4/4
🧠 PLANNING...
   Action: Files organized. Re-checking disk usage to verify improvement.
   Tool: check_disk
⚡ EXECUTING...
   ✓ Success (42ms)
   Result: GOOD (65% used)
👁️  OBSERVING...
✅ GOAL COMPLETE! Disk usage reduced from 85% to 65%.

📊 EXECUTION REPORT
===================
Goal: Fix high disk usage
Complete: ✅ Yes
Steps: 4/10
Time: 2.3s
Success Rate: 100%
```

---

### Scenario 3: Retry Logic in Action

**Goal:** Organize Downloads  
**Challenge:** Permission denied on first attempts  
**Expected:** Success after 3 retries

```
🎯 Enter your goal: Organize my Downloads

🔄 Step 1/10
🧠 PLANNING...
   Action: Organize files in Downloads folder.
   Tool: file_organizer
⚡ EXECUTING...
   Attempt 1: Failed (Permission denied)
   ↻ Retrying in 1.0s... (attempt 2/4)
   Attempt 2: Failed (Permission denied)
   ↻ Retrying in 2.0s... (attempt 3/4)
   Attempt 3: Success! ✅
   Execution time: 3200ms (with retries)
👁️  OBSERVING...
✅ GOAL COMPLETE!

📊 EXECUTION REPORT
===================
Goal: Organize my Downloads
Complete: ✅ Yes
Steps: 1/10
Retries: 2
Success Rate: 100%
```

**Retry Backoff Pattern:** 1s → 2s → 4s → 8s (exponential)

---

### Scenario 4: Timeout Protection

**Goal:** Check system status  
**Challenge:** Tool hangs  
**Expected:** Timeout and retry

```
🎯 Enter your goal: Check system status

🔄 Step 1/10
🧠 PLANNING...
   Action: Gather system information.
   Tool: system_info
⚡ EXECUTING...
   ⏱️ Timeout after 30s
   ↻ Retrying in 1.0s... (attempt 2/4)
   Attempt 2: Success! ✅ (45ms)
👁️  OBSERVING...
✅ GOAL COMPLETE!

📊 EXECUTION REPORT
===================
Goal: Check system status
Complete: ✅ Yes
Steps: 1/10
Retries: 1 (due to timeout)
Success Rate: 100%
```

---

### Scenario 5: Safety Limit Reached

**Goal:** Fix everything on my computer  
**Challenge:** Goal too broad, keeps finding issues  
**Expected:** Stops at max_steps (10)

```
🎯 Enter your goal: Fix everything on my computer

🔄 Step 1/10  [check_disk]     → WARNING
🔄 Step 2/10  [suggest_organize] → Found issues
🔄 Step 3/10  [file_organizer]   → Organized
🔄 Step 4/10  [check_disk]       → Still WARNING
🔄 Step 5/10  [suggest_organize] → More issues
🔄 Step 6/10  [file_organizer]   → Organized
🔄 Step 7/10  [check_disk]       → Still WARNING
🔄 Step 8/10  [suggest_organize] → More issues
🔄 Step 9/10  [file_organizer]   → Organized
🔄 Step 10/10 [check_disk]       → Still WARNING

⏹️  MAX STEPS REACHED: Stopping after 10 iterations

📊 EXECUTION REPORT
===================
Goal: Fix everything on my computer
Complete: ❌ No (safety limit reached)
Steps: 10/10
Success Rate: 100% (all steps executed)
Warning: Goal may be too broad or disk issues require manual intervention
```

---

### Scenario 6: Error Recovery

**Goal:** Organize nonexistent folder  
**Challenge:** Folder doesn't exist  
**Expected:** Graceful error handling

```
🎯 Enter your goal: Organize my NonExistent folder

🔄 Step 1/10
🧠 PLANNING...
   Action: Organize files in NonExistent folder.
   Tool: file_organizer
⚡ EXECUTING...
   ✗ Failed: Folder not found: /home/user/NonExistent
   Recovery: Trying fallback strategy...
   Fallback: Suggest alternative folders
   Tool: suggest_organize
   ✓ Success
   Found: Downloads, Documents
👁️  OBSERVING...
   Alternative strategy successful

🔄 Step 2/10
🧠 PLANNING...
   Action: Organize suggested Downloads folder.
   Tool: file_organizer
⚡ EXECUTING...
   ✓ Success (150 files moved)
👁️  OBSERVING...
✅ GOAL COMPLETE! (via recovery strategy)

📊 EXECUTION REPORT
===================
Goal: Organize my NonExistent folder
Complete: ✅ Yes (with recovery)
Steps: 2/10
Recovery: 1 fallback strategy used
Success Rate: 100%
```

---

## Configuration

```python
from agent import ProductionAgent, ExecutionConfig

config = ExecutionConfig(
    max_steps=10,              # Maximum iterations
    max_time_seconds=300,      # 5 minute timeout
    max_retries=3,             # Retry failed steps
    retry_delay_base=1.0,      # Initial retry delay (seconds)
    tool_timeout=30,           # Per-tool timeout
    log_level="INFO"           # DEBUG, INFO, WARNING, ERROR
)

agent = ProductionAgent(config=config)
result = agent.run("Your goal here")
```

---

## Testing

### Automated Testing

```bash
# Run with various goals
echo "Fix disk usage" | python agent.py
echo "Organize Downloads" | python agent.py
echo "Check system" | python agent.py
```

### Manual Testing

| Test | Goal | Expected |
|------|------|----------|
| 1 | `Fix high disk usage` | Multi-step with verification |
| 2 | `Organize Downloads` | 2 steps (organize + verify) |
| 3 | `Check system status` | 1 step, immediate complete |
| 4 | `Calculate 25 * 4` | 1 step, math result |
| 5 | `Unknown goal here` | Fallback to system_info |

### Stress Testing

```bash
# Test timeout
python -c "
from agent import ProductionAgent, ExecutionConfig
config = ExecutionConfig(max_time_seconds=5)
agent = ProductionAgent(config)
result = agent.run('Do something that takes time')
"
```

---

## Safety Features

### 1. Step Limit
```python
if step >= max_steps:
    stop("Max steps reached")
```

### 2. Time Limit
```python
if elapsed_time > max_time_seconds:
    stop("Timeout")
```

### 3. Retry Limit
```python
for attempt in range(max_retries + 1):
    try:
        execute()
        break
    except:
        if attempt == max_retries:
            raise  # Give up
        retry_with_backoff()
```

### 4. Tool Timeout
```python
signal.alarm(tool_timeout)  # Unix
# or
concurrent.futures.TimeoutError  # Cross-platform
```

---

## Error Handling

| Error Type | Response |
|------------|----------|
| Tool not found | Log error, try fallback |
| Permission denied | Retry with backoff |
| Timeout | Retry or skip |
| Unknown error | Log and continue |

---

## Monitoring

### Log Levels

- **DEBUG**: Detailed execution flow
- **INFO**: Step execution, retries
- **WARNING**: Recoverable errors
- **ERROR**: Failures after all retries

### Metrics

```python
{
    "total_steps": 4,
    "successful_steps": 4,
    "failed_steps": 0,
    "retried_steps": 1,
    "success_rate_percent": 100.0,
    "total_execution_time_ms": 2300.0
}
```

---

## What You Built

This is a **production-ready** autonomous agent with:

- ✅ **Goal-driven autonomy** - Loop until complete
- ✅ **Safety controls** - Limits on steps, time, retries
- ✅ **Self-healing** - Retry with exponential backoff
- ✅ **Observability** - Logging and metrics
- ✅ **Error recovery** - Alternative strategies
- ✅ **Timeout protection** - No hanging operations

This is the foundation for:

- **Production automation** - Reliable, monitored execution
- **DevOps agents** - Safe system management
- **Scheduled tasks** - Run with confidence
- **Multi-agent systems** - Robust building blocks

---

## Next Steps

- Add configuration files (YAML/JSON)
- Implement webhook notifications
- Add metrics export (Prometheus)
- Create Docker container
- Build REST API wrapper

---

## Quick Reference

### Goal → Tool Mapping

| Goal Keywords | Tool Used | Typical Steps |
|---------------|-----------|---------------|
| "check disk", "disk space" | check_disk | 1 (if good) or 4+ (if warning) |
| "organize", "clean up" | file_organizer | 2+ (organize + verify) |
| "system", "info", "status" | system_info | 1 |
| "calculate", "compute" | calculator | 1 |
| (anything else) | system_info | 1 (fallback) |

### Safety Limits (Default)

```python
max_steps = 10          # Stop after 10 iterations
max_time = 300s         # Stop after 5 minutes
max_retries = 3         # Retry failed steps 3 times
tool_timeout = 30s      # Each tool call times out after 30s
```

### Status Meanings

| Status | Meaning |
|--------|---------|
| `pending` | Step planned, not yet executed |
| `running` | Step currently executing |
| `retrying` | Step failed, attempting retry |
| `success` | Step completed successfully |
| `failed` | Step failed after all retries |
| `timeout` | Step exceeded time limit |

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Max steps reached" | Goal too broad or disk still critical | Be more specific or manually clean disk |
| "Timeout" | Tool taking too long | Increase `tool_timeout` in config |
| "Permission denied" | Insufficient privileges | Run with elevated permissions |
| "Goal not complete" | More steps needed | Increase `max_steps` in config |

---

## No External Dependencies!

- ✅ Pure Python standard library
- ✅ Works offline
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Zero install footprint
