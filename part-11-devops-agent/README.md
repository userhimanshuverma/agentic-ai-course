# DevOps Monitoring Agent

A simple AI-powered agent that monitors your system using local Mistral AI.

## What It Does

1. **Monitors** CPU, memory, disk, and processes
2. **Thinks** using Mistral AI via Ollama
3. **Shows** results in a clean format

## Prerequisites

- Python 3.8+
- Ollama installed: https://ollama.com
- Mistral model: `ollama pull mistral`

## Install

```bash
cd part-11-devops-agent
pip install psutil requests
```

## Run

Start Ollama in one terminal:
```bash
ollama serve
```

Run the agent in another:
```bash
python agent.py
```

## Example Goals

- `Check system health`
- `What processes are running?`
- `Check CPU usage`
- `Check memory`

## Example Output

```
🎯 Goal: What processes are running?
⚙️  Max steps: 10
──────────────────────────────────────────────────

🔄 Step 1
🧠 Action: get_process_metrics
🔧 Tool: get_process_metrics

📋 Top Processes:
----------------------------------------
Name                 CPU %      Memory %
----------------------------------------
ollama.exe           139.6      8.9
chrome.exe           13.5       2.8
python.exe           3.5        0.2
...

📊 Status: complete

✅ Goal complete!
```

## Files

- `agent.py` - Main agent
- `tools.py` - System monitoring
- `reasoning.py` - AI with Ollama
- `config.py` - Settings

## Test

```bash
python test_agent.py
```
