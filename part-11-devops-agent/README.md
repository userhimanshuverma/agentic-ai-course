# DevOps Monitoring Agent

A simple AI-powered DevOps agent that monitors your system and suggests actions.

## What It Does

1. **Monitors** your system (CPU, memory, disk, processes)
2. **Thinks** using AI (Mistral via Ollama)
3. **Suggests** what to do based on metrics

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed
- Mistral model: `ollama pull mistral`

## Installation

```bash
cd part-11-devops-agent
pip install -r requirements.txt
```

## Usage

### 1. Start Ollama

```bash
ollama serve
```

### 2. Run the Agent

```bash
python agent.py
```

Enter a goal like:
- `Check system health`
- `Monitor CPU`
- `Check memory`

### Example Output

```
🎯 Goal: Check system health
⚙️  Max steps: 10
──────────────────────────────────────────────────

🔄 Step 1
🧠 Action: Collect system metrics
🔧 Tool: get_all_metrics
📊 Status: complete

✅ Goal complete!

==================================================
📊 REPORT
==================================================
Goal: Check system health
Complete: Yes
Steps: 1
Time: 2.5s
==================================================
```

## Project Structure

```
part-11-devops-agent/
├── agent.py       # Main agent
├── tools.py       # System monitoring
├── reasoning.py   # AI with Ollama
├── config.py      # Settings
├── test_agent.py  # Tests
└── requirements.txt
```

## How It Works

```
User Goal → Collect Metrics → AI Analysis → Action
                ↑___________________________|
                    (loop until complete)
```

## Testing

```bash
python test_agent.py
```

## Customization

Edit `config.py`:

```python
@dataclass
class Config:
    max_steps: int = 10      # More/fewer steps
    max_time: int = 300      # Timeout in seconds
    ollama_url: str = "http://localhost:11434"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama error" | Start Ollama: `ollama serve` |
| "Model not found" | Install: `ollama pull mistral` |
| High CPU | Normal - AI is thinking |

## License

MIT
