# Part 11 — DevOps Monitoring Agent with Mistral AI

A full-fledged, beginner-friendly DevOps Monitoring Agent that uses AI-powered reasoning to monitor system health, detect anomalies, and suggest corrective actions.

---

## What This Agent Does

This agent acts like a **virtual DevOps engineer** that:

1. **Monitors** your system (CPU, memory, disk, network, processes)
2. **Thinks** about the metrics using AI (Mistral model)
3. **Detects** abnormal spikes and issues
4. **Suggests** corrective actions
5. **Operates autonomously** until the goal is achieved

---

## Architecture

```
User Goal
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                 DEVOPS MONITORING AGENT                      │
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │    PLAN     │───▶│     ACT     │───▶│   OBSERVE   │     │
│   │             │    │             │    │             │     │
│   │ AI analyzes │    │ Execute     │    │ Check if    │     │
│   │ metrics and │    │ monitoring  │    │ goal is     │     │
│   │ decides     │    │ tools       │    │ complete    │     │
│   │ next action │    │             │    │             │     │
│   └─────────────┘    └──────┬──────┘    └──────┬──────┘     │
│                             │                  │            │
│                    ┌────────┴────────┐         │            │
│                    │  SAFETY LAYER   │         │            │
│                    │  • Step limit   │         │            │
│                    │  • Time limit   │         │            │
│                    │  • Retry logic  │         │            │
│                    │  • Timeout      │         │            │
│                    └─────────────────┘         │            │
│                                                │            │
│   ◄────────────────────────────────────────────┘            │
│   (Loop until goal_complete OR safety limit reached)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Execution Report with AI recommendations
```

### Module Structure

```
part-11-devops-agent/
│
├── agent.py          # Main agent with goal-driven loop
├── tools.py          # System monitoring tools (psutil)
├── reasoning.py      # AI reasoning with Mistral
├── config.py         # Configuration management
├── test_agent.py     # Test suite
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## Features

### 1. System Monitoring
- **CPU Usage**: Real-time CPU percentage per core
- **Memory**: RAM usage, available memory
- **Disk**: Storage usage by mount point
- **Network**: I/O statistics
- **Processes**: Top CPU-consuming processes

### 2. AI-Powered Reasoning
- **Three modes**: Local model, HuggingFace API, or Mock (for testing)
- **Smart analysis**: AI understands metrics context
- **Action recommendations**: Specific next steps
- **Anomaly detection**: Identifies unusual patterns

### 3. Safety Controls
- **Step limit**: Max 10 iterations (configurable)
- **Time limit**: Max 5 minutes (configurable)
- **Retry logic**: 3 retries with exponential backoff
- **Tool timeout**: 30 seconds per tool call

### 4. Production-Ready
- **Comprehensive logging**: All actions logged
- **Error handling**: Graceful failure recovery
- **Metrics tracking**: Success rates, execution times
- **Modular design**: Easy to extend

---

## Installation

### 1. Clone or Navigate to the Project

```bash
cd part-11-devops-agent
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: For the mock mode (default), you only need:
```bash
pip install psutil
```

### 4. For AI Mode (Optional)

To use real AI reasoning, choose one:

**Option A: HuggingFace Inference API**
```bash
export HF_API_TOKEN="your_token_here"  # Linux/Mac
set HF_API_TOKEN=your_token_here       # Windows
```

**Option B: Local Model**
```bash
pip install transformers torch
```

---

## Usage

### Quick Start (Mock Mode - No AI Required)

```bash
python agent.py
```

Then enter a goal like:
- `Check system health`
- `Monitor CPU usage`
- `Check memory status`

### Example Run

```
============================================================
🖥️  DevOps Monitoring Agent
============================================================

🎯 Goal: Check system health
⚙️  Safety Limits: 10 steps, 300s timeout
🧠 Reasoning: mock

────────────────────────────────────────────────────────────

🔄 Step 1/10
────────────────────────────────────────────────────────────
🧠 PLANNING...
   Action: Collect comprehensive system metrics
   Tool: get_all_metrics
⚡ EXECUTING...
   ✅ Success (145ms)
👁️  OBSERVING...
   ✅ Goal achieved!

✅ GOAL COMPLETE! Stopping after 1 steps.

============================================================
📊 EXECUTION REPORT
============================================================
Goal: Check system health
Complete: ✅ Yes
Steps: 1/10
Time: 0.3s
Success Rate: 100.0%

Conclusion: ✅ Goal 'Check system health' was successfully 
            achieved in 1 steps.
============================================================
```

### Using Different Reasoning Modes

```python
from agent import DevOpsAgent
from config import AgentConfig

# Mock mode (default, no AI required)
config = AgentConfig(reasoning_mode="mock")
agent = DevOpsAgent(config)

# Local AI model (requires transformers)
config = AgentConfig(reasoning_mode="local")
agent = DevOpsAgent(config)

# HuggingFace API (requires token)
config = AgentConfig(
    reasoning_mode="api",
    hf_api_token="your_token"
)
agent = DevOpsAgent(config)

# Run the agent
result = agent.run("Check CPU usage")
print(result['conclusion'])
```

---

## Example Scenarios

### Scenario 1: High CPU Detection

```
🎯 Goal: Monitor CPU usage

🔄 Step 1/3
🧠 PLANNING...
   Action: Investigate high CPU usage
   Reasoning: CPU is at 85%, above the 80% threshold
   Tool: get_process_metrics
⚡ EXECUTING...
   ✅ Success (50ms)
   Top processes: python (45%), chrome (20%)

✅ GOAL COMPLETE!

💡 AI Suggestions:
   - Identify and terminate high-CPU processes
   - Check for runaway applications
   - Consider scaling up CPU resources
```

### Scenario 2: Memory Spike

```
🎯 Goal: Check memory status

🔄 Step 1/3
🧠 PLANNING...
   Action: Check for memory-intensive processes
   Reasoning: Memory at 92%, approaching critical
   Tool: get_process_metrics
⚡ EXECUTING...
   ✅ Success (45ms)

🔄 Step 2/3
🧠 PLANNING...
   Action: Memory still high, suggest fixes
   Tool: suggest_fix
⚡ EXECUTING...
   ✅ Success

💡 AI Suggestions:
   - Restart memory-intensive applications
   - Check for memory leaks
   - Clear system cache
   - Consider adding more RAM
```

### Scenario 3: Full System Check

```
🎯 Goal: Full system diagnostic

🔄 Step 1/5 - Collect all metrics
🔄 Step 2/5 - Analyze CPU (normal)
🔄 Step 3/5 - Analyze memory (warning)
🔄 Step 4/5 - Check processes
🔄 Step 5/5 - Generate recommendations

📊 FINAL REPORT:
   CPU: 35% (normal)
   Memory: 82% (warning)
   Disk: 67% (normal)
   
⚠️  Issues Found:
   - Memory usage above 80%
   
✅ Recommendations:
   - Restart applications using >500MB RAM
   - Monitor memory trend over next hour
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_MAX_STEPS` | 10 | Maximum iterations |
| `AGENT_MAX_TIME` | 300 | Timeout in seconds |
| `AGENT_MAX_RETRIES` | 3 | Retry attempts |
| `AGENT_REASONING_MODE` | mock | mock/local/api |
| `HF_API_TOKEN` | None | HuggingFace token |
| `CPU_WARNING` | 70 | CPU warning threshold % |
| `CPU_CRITICAL` | 90 | CPU critical threshold % |
| `MEMORY_WARNING` | 80 | Memory warning threshold % |
| `MEMORY_CRITICAL` | 95 | Memory critical threshold % |

### Programmatic Configuration

```python
from agent import DevOpsAgent
from config import AgentConfig

config = AgentConfig(
    max_steps=5,
    max_time_seconds=60,
    reasoning_mode="mock",
    cpu_warning=60.0,
    cpu_critical=80.0
)

agent = DevOpsAgent(config)
result = agent.run("Check system")
```

---

## Testing

Run the test suite:

```bash
python test_agent.py
```

Expected output:
```
============================================================
🚀 DEVOPS MONITORING AGENT - TEST SUITE
============================================================

🧪 Testing: 1. CPU Metrics
✅ PASS: CPU: 23.5% (normal)

🧪 Testing: 2. Memory Metrics
✅ PASS: Memory: 45.2% (normal)
...

📊 TEST SUMMARY
============================================================
Total Tests: 14
✅ Passed: 14
❌ Failed: 0
Success Rate: 100.0%
============================================================

🎉 ALL TESTS PASSED!
```

---

## How It Works (For Beginners)

### The Goal-Driven Loop

```python
while not goal_complete and step < max_steps and not timeout:
    # 1. PLAN: AI analyzes metrics and decides next action
    metrics = collect_metrics()
    decision = ai.analyze(metrics, goal)
    
    # 2. ACT: Execute the monitoring tool
    result = execute_tool(decision.tool, decision.parameters)
    
    # 3. OBSERVE: Check if goal is achieved
    goal_complete = check_completion(result)
```

### Retry Logic with Exponential Backoff

If a tool fails, the agent retries:

```
Attempt 1: Failed
Wait: 1 second

Attempt 2: Failed  
Wait: 2 seconds (1 × 2)

Attempt 3: Failed
Wait: 4 seconds (2 × 2)

Attempt 4: Success! ✅
```

### AI Reasoning Flow

```
Raw Metrics          AI Analysis           Action
───────────          ───────────           ──────
CPU: 85%     ──▶    "High CPU detected"  ──▶  Check processes
Memory: 92%  ──▶    "Critical memory"    ──▶  Suggest fixes
Disk: 45%    ──▶    "Normal"             ──▶  Continue monitoring
```

---

## Extending the Agent

### Add a New Tool

```python
# In tools.py
class SystemMonitor:
    def get_temperature(self):
        """Get CPU temperature"""
        # Your implementation
        return {"temperature": 45.5, "status": "normal"}
```

### Add a New Reasoning Pattern

```python
# In reasoning.py
def _generate_mock(self, prompt):
    # Add your custom logic
    if "temperature" in prompt.lower():
        return json.dumps({
            "action": "Check cooling system",
            "tool_to_use": "get_temperature",
            ...
        })
```

---

## Troubleshooting

### Issue: "Module not found"
```bash
pip install psutil
```

### Issue: "Permission denied" on Windows
Run PowerShell/Command Prompt as Administrator

### Issue: "Model loading takes too long"
The default uses mock mode. For real AI:
- Use a smaller model like `SmolLM-135M`
- Or use HuggingFace API instead of local

### Issue: High CPU during monitoring
The CPU monitoring itself uses some CPU. Use shorter intervals:
```python
monitor.get_cpu_metrics(interval=0.1)  # Faster, less accurate
```

---

## Next Steps

- [ ] Add webhook notifications (Slack/Discord)
- [ ] Create a web dashboard
- [ ] Add historical data storage
- [ ] Implement predictive alerting
- [ ] Add more AI models (GPT, Claude)

---

## License

MIT License - Free for personal and commercial use

---

## Credits

- **psutil**: System monitoring library
- **Mistral AI**: Language model for reasoning
- **HuggingFace**: Model hosting and inference API

---

**Happy Monitoring! 🖥️🤖**
