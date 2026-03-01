# Agentic AI Platform - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENTIC AI PLATFORM                                │
│                    (MCP-Enabled, Local LLM, Production-Ready)               │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐      ┌──────────────┐      ┌────────────────────────┐    │
│   │     CLI      │      │   FastAPI    │      │    MCP Client (stdio)  │    │
│   │   (main.py)  │      │    Server    │      │                        │    │
│   │              │      │   (Port 8000)│      │  Connects to external  │    │
│   │ • Interactive│      │              │      │  MCP servers           │    │
│   │ • One-shot   │      │ • REST API   │      │                        │    │
│   │ • Health chk │      │ • Async      │      │                        │    │
│   └──────┬───────┘      └──────┬───────┘      └───────────┬────────────┘    │
│          │                     │                          │                 │
└──────────┼─────────────────────┼──────────────────────────┼─────────────────┘
           │                     │                          │
           └─────────────────────┴──────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AGENT CORE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         PLANNER                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐   │   │
│   │  │  Input: Goal (e.g., "Calculate circle area")                │   │   │
│   │  │  Process:                                                   │   │   │
│   │  │    1. Send goal + available tools to LLM                    │   │   │
│   │  │    2. LLM generates structured plan (JSON)                  │   │   │
│   │  │    3. Parse plan into Plan object with steps                │   │   │
│   │  │  Output: Plan with steps and tool calls                     │   │   │
│   │  └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        EXECUTOR                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐   │   │
│   │  │  Input: Plan with steps                                     │   │   │
│   │  │  Process:                                                   │   │   │
│   │  │    For each step:                                           │   │   │
│   │  │      1. Log step start                                      │   │   │
│   │  │      2. If tool_call exists:                                │   │   │
│   │  │         - Call MCP tool via registry                        │   │   │
│   │  │         - Get result                                        │   │   │
│   │  │      3. Log step completion                                 │   │   │
│   │  │      4. Store result in memory                              │   │   │
│   │  │  Output: List of StepResults                                │   │   │
│   │  └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                       REFLECTOR                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐   │   │
│   │  │  Input: Goal, Plan, Results                                 │   │   │
│   │  │  Process:                                                   │   │   │
│   │  │    1. Send execution summary to LLM                         │   │   │
│   │  │    2. LLM analyzes success/failure                          │   │   │
│   │  │    3. Generate insights and lessons learned                 │   │   │
│   │  │  Output: Reflection with summary and improvements           │   │   │
│   │  └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│         LLM LAYER            │    │       MEMORY SYSTEM          │
├──────────────────────────────┤    ├──────────────────────────────┤
│                              │    │                              │
│  ┌────────────────────────┐  │    │  ┌────────────────────────┐  │
│  │       Ollama Client    │  │    │  │   SHORT-TERM MEMORY    │  │
│  │                        │  │    │  │                        │  │
│  │  • HTTP API to Ollama  │  │    │  │  • In-memory buffer    │  │
│  │  • Model: Mistral      │  │    │  │  • Last 10 items       │  │
│  │  • Timeout handling    │  │    │  │  • Fast access         │  │
│  │  • Retry logic         │  │    │  │  • Conversation hist   │  │
│  │  • Token tracking      │  │    │  └────────────────────────┘  │
│  │                        │  │    │                              │
│  │  generate()            │  │    │  ┌────────────────────────┐  │
│  │  generate_structured() │  │    │  │   LONG-TERM MEMORY     │  │
│  │                        │  │    │  │                        │  │
│  └────────────────────────┘  │    │  │  • ChromaDB storage    │  │
│                              │    │  │  • Vector embeddings   │  │
│  Features:                   │    │  │  • Semantic search     │  │
│  • Structured JSON output    │    │  │  • Persistent storage  │  │
│  • Schema validation         │    │  │                        │  │
│  • Error recovery            │    │  └────────────────────────┘  │
│                              │    │                              │
└──────────────────────────────┘    └──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER / TOOLS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │ CALCULATOR  │  │   CODE      │  │    FILE     │  │    WEB      │       │
│   │             │  │  EXECUTOR   │  │    TOOL     │  │   SEARCH    │       │
│   │ • Math expr │  │             │  │             │  │             │       │
│   │ • sqrt()    │  │ • Sandbox   │  │ • Read      │  │ • Mock      │       │
│   │ • sin()     │  │ • print()   │  │ • Write     │  │ • Search    │       │
│   │ • pi, e     │  │ • Safe exec │  │ • List      │  │ • Results   │       │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                              │
│   ┌─────────────┐  ┌──────────────────────────────────────────────────┐     │
│   │   SYSTEM    │  │              TOOL REGISTRY                        │     │
│   │    INFO     │  │                                                   │     │
│   │             │  │  • Register tools                                 │     │
│   │ • Platform  │  │  • List available tools                           │     │
│   │ • CPU       │  │  • Execute tool by name                           │     │
│   │ • Memory    │  │  • JSON-RPC interface                             │     │
│   └─────────────┘  └──────────────────────────────────────────────────┘     │
│                                                                              │
│   TRANSPORT:                                                                 │
│   • stdio (for subprocess communication)                                    │
│   • HTTP (for REST API)                                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVABILITY                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         LOGGER                                      │   │
│   │                                                                     │   │
│   │  Structured JSON Logging:                                           │   │
│   │  {                                                                  │   │
│   │    "timestamp": "2026-03-01T12:00:00",                              │   │
│   │    "level": "INFO",                                                 │   │
│   │    "logger": "agentic_ai",                                          │   │
│   │    "message": "Step completed",                                     │   │
│   │    "goal_id": "uuid-here",                                          │   │
│   │    "step_number": 1,                                                │   │
│   │    "event_type": "step_complete"                                    │   │
│   │  }                                                                  │   │
│   │                                                                     │   │
│   │  Log Destinations:                                                  │   │
│   │  • Console (stdout)                                                 │   │
│   │  • File (logs/agent.log)                                            │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Events Tracked:                                                            │
│   • goal_start, goal_complete                                                │
│   • plan_created                                                             │
│   • step_start, step_complete                                                │
│   • tool_call, tool_result                                                   │
│   • llm_call                                                                 │
│   • memory_store, memory_retrieve                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Goal Execution Flow

```
User Input
    │
    ▼
┌─────────────┐
│  Parse Goal │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────┐
│   PLANNER   │────▶│  LLM    │
│             │     │ (Mistral)│
│ Create Plan │◀────│         │
└──────┬──────┘     └─────────┘
       │
       ▼
┌─────────────┐
│   EXECUTOR  │─────────────────────────┐
│             │                         │
│ For each    │    ┌─────────┐         │
│ step:       │───▶│  Tool   │         │
│ - Call tool │    │ Registry│         │
│ - Log       │◀───│         │         │
│ - Store     │    └────┬────┘         │
└──────┬──────┘         │              │
       │                ▼              │
       │           ┌─────────┐         │
       │           │  Tool   │         │
       │           │ Execute │         │
       │           └────┬────┘         │
       │                │              │
       └────────────────┴──────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Results   │
                   │   List      │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐     ┌─────────┐
                   │  REFLECTOR  │────▶│  LLM    │
                   │             │     │         │
                   │  Analyze    │◀────│ Reflect │
                   └──────┬──────┘     └─────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   REPORT    │
                   │  (JSON)     │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   OUTPUT    │
                   │  (User)     │
                   └─────────────┘
```

### 2. Tool Execution Flow

```
Executor
    │
    │ call_tool("calculator", {"expression": "2+2"})
    ▼
┌─────────────────┐
│  Tool Registry  │
│                 │
│  Lookup:        │
│  "calculator"   │
│  ────────────▶  │
│  CalculatorTool │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Security Check │
│  (Validation)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tool.execute() │
│                 │
│  1. Parse args  │
│  2. Execute     │
│  3. Format      │
│  4. Return      │
└────────┬────────┘
         │
         │ {"content": [{"text": "4"}], "isError": false}
         ▼
      Result
```

### 3. Memory Storage Flow

```
Agent Action
    │
    ├─────────────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────┐                 ┌──────────────┐
│ SHORT-TERM   │                 │ LONG-TERM    │
│ MEMORY       │                 │ MEMORY       │
│              │                 │              │
│ In-memory    │                 │ ChromaDB     │
│ list (10)    │                 │ Vector DB    │
│              │                 │              │
│ Fast access  │                 │ Embeddings   │
│ Recent only  │                 │ Persistent   │
└──────────────┘                 └──────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Input Validation                                   │
│  ├── JSON schema validation for all inputs                   │
│  ├── Type checking with Pydantic                             │
│  └── Range validation for numeric values                     │
│                                                              │
│  Layer 2: Tool Sandboxing                                    │
│  ├── Calculator: Restricted eval() with allowed chars        │
│  ├── Code Executor: AST analysis + restricted builtins       │
│  ├── File Tool: Path traversal prevention + allowed exts     │
│  └── Web Search: Mock results (no actual HTTP calls)         │
│                                                              │
│  Layer 3: Resource Limits                                    │
│  ├── Code execution timeout (30s default)                    │
│  ├── File size limits                                        │
│  └── Memory usage monitoring                                 │
│                                                              │
│  Layer 4: Error Handling                                     │
│  ├── Graceful degradation                                    │
│  ├── No sensitive info in errors                             │
│  └── Structured error responses                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Interactions

```
┌─────────────┐     HTTP      ┌─────────────┐
│    User     │◀─────────────▶│  FastAPI    │
│   Client    │               │   Server    │
└─────────────┘               └──────┬──────┘
                                     │
                                     │ calls
                                     ▼
                              ┌─────────────┐
                              │    Agent    │
                              │    Core     │
                              └──────┬──────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │    LLM      │       │   Memory    │       │    MCP      │
       │  (Ollama)   │       │  (Chroma)   │       │   Server    │
       └─────────────┘       └─────────────┘       └──────┬──────┘
                                                          │
                              ┌───────────────────────────┼───┐
                              │                           │   │
                              ▼                           ▼   ▼
                       ┌──────────┐              ┌──────────┐
                       │ Calculator│             │  File    │
                       └──────────┘              │  Tool    │
                       ┌──────────┐              └──────────┘
                       │  Code    │              ┌──────────┐
                       │ Executor │              │  System  │
                       └──────────┘              │  Info    │
                                                  └──────────┘
```

## Configuration Architecture

```
Environment Variables
        │
        ▼
┌───────────────┐
│  Config Class │
│  (Pydantic)   │
└───────┬───────┘
        │
        ├──▶ LLM Config (Ollama URL, Model, Timeout)
        ├──▶ API Config (Host, Port)
        ├──▶ Memory Config (ChromaDB path)
        ├──▶ Logging Config (Level, File)
        └──▶ Security Config (Safe directory)
```

## Deployment Options

### 1. Local Development

```
┌─────────────────────────────────────┐
│           Local Machine             │
│                                     │
│  ┌─────────┐  ┌─────────┐          │
│  │  Agent  │  │ Ollama  │          │
│  │  (CLI)  │  │(Mistral)│          │
│  └─────────┘  └─────────┘          │
│                                     │
└─────────────────────────────────────┘
```

### 2. Docker Compose (Full Stack)

```
┌─────────────────────────────────────────────────────┐
│                 Docker Network                       │
│                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │  Agent  │◀──▶│ Ollama  │    │ ChromaDB│         │
│  │  (API)  │    │(Mistral)│    │         │         │
│  └────┬────┘    └─────────┘    └─────────┘         │
│       │                                             │
│       │ Port 8000                                   │
└───────┼─────────────────────────────────────────────┘
        │
        ▼
   External Client
```

### 3. Production (Kubernetes)

```
┌─────────────────────────────────────────────────────┐
│              Kubernetes Cluster                      │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           Ingress Controller                 │   │
│  │         (SSL, Rate Limiting)                 │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                               │
│  ┌──────────────────┼──────────────────────────┐   │
│  │                  ▼                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │ Agent   │  │ Agent   │  │ Agent   │    │   │
│  │  │ Pod 1   │  │ Pod 2   │  │ Pod 3   │    │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘    │   │
│  │       └─────────────┴─────────────┘        │   │
│  │                  Service                    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Ollama  │  │ ChromaDB│  │  Redis  │            │
│  │ Service │  │ Service │  │ (Cache) │            │
│  └─────────┘  └─────────┘  └─────────┘            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                   PERFORMANCE OPTIMIZATIONS                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. LLM Caching                                              │
│     └── Cache identical prompts (future enhancement)         │
│                                                              │
│  2. Memory Indexing                                          │
│     └── ChromaDB vector indexing for fast retrieval          │
│                                                              │
│  3. Async Execution                                          │
│     └── FastAPI async endpoints for concurrent requests      │
│                                                              │
│  4. Tool Timeouts                                            │
│     └── Configurable timeouts prevent hanging                │
│                                                              │
│  5. Streaming Responses                                      │
│     └── Future: Stream LLM responses for faster UX           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Extension Points

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTENSION POINTS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Add New Tool                                             │
│     └── Create class in mcp_server/tools/                    │
│     └── Register in registry.py                              │
│                                                              │
│  2. Add New LLM Provider                                     │
│     └── Implement LLMClient interface in agent/llm.py        │
│                                                              │
│  3. Custom Memory Backend                                    │
│     └── Implement MemoryBackend interface in agent/memory.py │
│                                                              │
│  4. Custom Planner/Executor/Reflector                        │
│     └── Override methods in respective classes               │
│                                                              │
│  5. Additional API Endpoints                                 │
│     └── Add routes in api/server.py                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
