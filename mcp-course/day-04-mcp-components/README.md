# Day 4: MCP Components

## 🎯 What We're Learning

MCP is made up of specific building blocks. Today we learn what they are and how they fit together.

Think of it like LEGO: Individual bricks that snap together to build a system.

## 🧩 The Four Main Components

```
┌─────────────────────────────────────────────────────────┐
│            MCP SYSTEM COMPONENTS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐             │
│  │MCP CLIENT    │◄────────│MCP SERVER    │             │
│  │              │         │              │             │
│  │(Requestor)   │────────►│(Provider)    │             │
│  └──────────────┘         └───────┬──────┘             │
│                                   │                    │
│                         ┌─────────▼────────┐           │
│                         │  TOOLS           │           │
│                         │  RESOURCES       │           │
│                         │  PROMPTS         │           │
│                         └──────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1️⃣ MCP Client

**What It Is:** The part that makes requests.

Usually your AI agent (Claude, ChatGPT, custom agent).

```
MCP Client
├── Your Agent
├── Your Application
└── Any tool that needs external capabilities
```

**What It Does:**
- Connects to MCP Server
- Sends tool requests
- Receives results
- Handles responses

**Example:**

```python
# This is an MCP Client
from mcp import MCPClient

class Agent:
    def __init__(self):
        # Connect to server
        self.client = MCPClient("mcp://localhost:3000")
    
    def work(self):
        # Make a request to server
        result = self.client.call_tool(
            tool="git",
            name="list_branches"
        )
        print(f"Result: {result}")
```

### 2️⃣ MCP Server

**What It Is:** The part that fulfills requests.

Runs on a machine and exposes tools, resources, and prompts.

```
MCP Server
├── Manages Tools
├── Manages Resources
├── Manages Prompts
└── Communicates with Clients
```

**What It Does:**
- Listens for client requests
- Validates requests
- Executes the right operation
- Returns standardized responses

**Example:**

```python
# This is an MCP Server
from mcp import MCPServer

server = MCPServer()

@server.tool
def list_branches():
    """List all Git branches"""
    repo = Repo('/path/to/repo')
    return {"branches": repo.git.branch('-a')}

@server.tool
def create_branch(name: str):
    """Create a new branch"""
    repo = Repo('/path/to/repo')
    repo.create_head(name)
    return {"status": "created", "name": name}

server.start()
```

### 3️⃣ Tools

**What It Is:** Capabilities that the server offers.

Functions that the server can execute.

```python
Tools are like this:
┌─────────────────────┐
│  list_branches      │
│  create_branch      │
│  commit_changes     │
│  push_to_remote     │
│  get_commit_log     │
└─────────────────────┘
```

**Properties of a Tool:**
- **Name:** Unique identifier (e.g., "list_branches")
- **Input Schema:** What parameters it needs (e.g., {"branch_name": str})
- **Output Schema:** What it returns (e.g., {list of branches})
- **Description:** What it does (e.g., "List all available branches")

**Example Tool Definition:**

```python
tool = {
    "name": "list_branches",
    "description": "List all Git branches in the repository",
    "inputSchema": {
        "type": "object",
        "properties": {
            "remote": {
                "type": "boolean",
                "description": "Show remote branches (default: false)"
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "branches": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
}
```

### 4️⃣ Resources

**What It Is:** Read-only data that the server exposes.

NOT executable (unlike tools), just readable.

```python
Resources are like this:
┌─────────────────────┐
│  /config.json       │
│  /README.md         │
│  /deployment.log    │
│  /team_docs.txt     │
└─────────────────────┘
```

**Example Resource:**

```python
resource = {
    "uri": "git://main/README.md",
    "description": "Main README file",
    "mimeType": "text/markdown",
    "content": "# Project Documentation\n..."
}
```

**Use Resources For:**
- Configuration files
- Documentation
- Read-only data
- Logs
- Reports

**Don't Use Resources For:**
- Anything that changes state
- Operations
- Actions (use tools instead!)

## 🔍 Detailed Deep Dive: Tools

### Tool Structure

```
┌─────────────────────────────────────────────┐
│              A TOOL DEFINITION              │
├─────────────────────────────────────────────┤
│                                             │
│  name: "clone_repo"                         │
│  description: "Clone a Git repository"      │
│  inputSchema: {                             │
│    type: "object"                           │
│    properties: {                            │
│      "url": {                               │
│        type: "string"                       │
│        description: "Repository URL"        │
│      }                                      │
│      "path": {                              │
│        type: "string"                       │
│        description: "Where to clone"        │
│      }                                      │
│    }                                        │
│    required: ["url"]                        │
│  }                                          │
│                                             │
└─────────────────────────────────────────────┘
```

### Tool Lifecycle

```
Step 1: Server Exposes Tool
┌────────────────────┐
│   MCP Server       │
│  ├─ Tool 1         │
│  ├─ Tool 2         │
│  └─ Tool 3         │
└────────────────────┘

Step 2: Client Discovers Tools
┌────────────────────┐     GET /tools      ┌────────────────────┐
│   MCP Client       │ ──────────────────→ │   MCP Server       │
│                    │ ←────────────────── │  [tool list]       │
│                    │                    │                    │
└────────────────────┘                    └────────────────────┘

Step 3: Client Requests Tool Execution
┌────────────────────┐     CALL tool1     ┌────────────────────┐
│   MCP Client       │ ──────────────────→ │   MCP Server       │
│                    │ ←────────────────── │  [result]          │
│                    │                    │                    │
└────────────────────┘                    └────────────────────┘
```

## 🔍 Detailed Deep Dive: Resources

### Resource Types

**1. File Resources**

```
uri: "file:///config/app.yaml"
Contains: Application configuration
```

**2. Documentation Resources**

```
uri: "docs://api/endpoints"
Contains: API documentation
```

**3. Log Resources**

```
uri: "logs://app/runtime.log"
Contains: Application logs
```

**4. Template Resources**

```
uri: "templates://email/welcome"
Contains: Email template
```

### Resource Discovery

```
Client                          Server
  │                               │
  ├──── LIST RESOURCES ──────────→│
  │                               │
  │←──── RESOURCE LIST ───────────┤
  │   ├─ file://config            │
  │   ├─ docs://readme            │
  │   └─ logs://recent            │
  │                               │
  ├──── READ RESOURCE ───────────→│ (request specific resource)
  │     (file://config)           │
  │                               │
  │←──── RESOURCE CONTENT ────────┤
  │     {...config data...}       │
  │                               │
```

## 🎨 Prompts (Bonus Component)

**What It Is:** Pre-written prompts that the server suggests to clients.

Think of them as "smart templates" that help you ask better questions.

```python
Prompts are like this:
┌─────────────────────────────────────────┐
│  "create_deployment_plan"                │
│  "review_code_changes"                   │
│  "analyze_performance_report"            │
│  "generate_release_notes"                │
└─────────────────────────────────────────┘
```

**Example:**

```python
prompt = {
    "name": "code_review_prompt",
    "description": "Prompt for reviewing code changes",
    "arguments": [
        {
            "name": "file_path",
            "description": "Path to file to review",
            "required": True
        }
    ],
    "prompt_template": """
    Please review the code changes in {file_path}.
    Look for:
    1. Security issues
    2. Performance problems
    3. Code style violations
    """
}
```

## 🏗️ How Components Work Together

### Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   COMPLETE MCP WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CLIENT CONNECTS                                         │
│     ┌──────────────┐                                        │
│     │ MCP Client   │                                        │
│     └──────┬───────┘                                        │
│            │ "Connect to server"                            │
│            ▼                                                │
│     ┌──────────────┐                                        │
│     │ MCP Server   │                                        │
│     │ (starts up)  │                                        │
│     └──────────────┘                                        │
│                                                             │
│  2. CLIENT DISCOVERS CAPABILITIES                           │
│     ┌──────────────┐          ┌──────────────┐             │
│     │ MCP Client   │          │ MCP Server   │             │
│     │ "What tools? │─────────→│ Tools: [1,2] │             │
│     │  Resources?" │←─────────│ Resources:[1]│             │
│     └──────────────┘          └──────────────┘             │
│                                                             │
│  3. CLIENT CALLS TOOL                                       │
│     ┌──────────────┐          ┌──────────────┐             │
│     │ MCP Client   │          │ MCP Server   │             │
│     │ "Execute     │─────────→│ Executes     │             │
│     │  tool1"      │          │ tool1()      │             │
│     │ ← receives   │←─────────│ Returns:     │             │
│     │   result     │          │ {data}       │             │
│     └──────────────┘          └──────────────┘             │
│                                                             │
│  4. CLIENT READS RESOURCE                                  │
│     ┌──────────────┐          ┌──────────────┐             │
│     │ MCP Client   │          │ MCP Server   │             │
│     │ "Read        │─────────→│ Loads        │             │
│     │  resource1"  │          │ resource1    │             │
│     │ ← receives   │←─────────│ Returns:     │             │
│     │   content    │          │ {...}        │             │
│     └──────────────┘          └──────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Component Checklist

### When Building an MCP Server, Include:

```
[ ] MCP Server Implementation
    ├─ [ ] Connection handler
    ├─ [ ] Request handler
    └─ [ ] Response formatter

[ ] Tools
    ├─ [ ] Define at least 2-3 tools
    ├─ [ ] Input schema for each
    └─ [ ] Output schema for each

[ ] Resources (Optional but recommended)
    ├─ [ ] Configuration files
    ├─ [ ] Documentation
    └─ [ ] Usage examples

[ ] Prompts (Optional)
    └─ [ ] Helper prompts for clients
```

### When Building an MCP Client, Include:

```
[ ] MCP Client Implementation
    ├─ [ ] Connection logic
    ├─ [ ] Tool discovery
    └─ [ ] Error handling

[ ] Tool Execution
    ├─ [ ] Call discovered tools
    ├─ [ ] Handle responses
    └─ [ ] Present results to agent
```

## 🎯 Component Responsibilities

| Component | Responsibility | Example |
|-----------|-----------------|---------|
| **Client** | Ask questions, use results | "Run git status" |
| **Server** | Listen, execute, respond | Host git tools |
| **Tools** | Do work, return results | git.status() |
| **Resources** | Provide read data | config.yaml |

## 💡 Real-World Example

### Git MCP System

```
CLIENT SIDE (Your Agent):
┌────────────────────────────────────┐
│ class DevOpsAgent:                 │
│   def __init__(self):              │
│     self.client = MCPClient(        │
│       "git-server"                 │
│     )                              │
│   def deploy(self):                │
│     branches = self.client.        │
│       call_tool("git",             │
│         "list_branches")           │
└────────────────────────────────────┘

SERVER SIDE (Git Tools):
┌────────────────────────────────────┐
│ server = MCPServer()                │
│                                    │
│ @server.tool                       │
│ def list_branches():               │
│   return get_git_branches()        │
│                                    │
│ @server.tool                       │
│ def create_branch(name):           │
│   return create_git_branch(name)   │
│                                    │
│ @server.resource                   │
│ def get_config():                  │
│   return load_git_config()         │
└────────────────────────────────────┘
```

## 🎓 Key Takeaway

**MCP is built from reusable components:**

1. **Client** - Makes requests
2. **Server** - Fulfills requests
3. **Tools** - Actions the server can perform
4. **Resources** - Data the server can share

They snap together like LEGO to build flexible, scalable systems.

## 🚀 What's Next?

Tomorrow: **Message Flow** - We'll trace exactly what happens when a client calls a tool, step by step, with full JSON payloads.

---

**Remember:** A tool is an action. A resource is data. A server hosts them. A client uses them. That's the whole MCP system!
