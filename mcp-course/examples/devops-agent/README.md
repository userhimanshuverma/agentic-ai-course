# DevOps Agent Example

A production-ready DevOps agent using MCP.

## What It Does

- Monitors infrastructure
- Deploys applications
- Manages Git repositories
- Interacts with AWS

## Architecture

```
DevOps Agent
    │
    ├─→ MCP Client
    │
    ├─→ Git Server (MCP)
    ├─→ AWS Server (MCP)
    └─→ Docker Server (MCP)
```

## Quick Start

```bash
python agent.py
```

## Tools Used

- `git_status` - Check repository status
- `git_push` - Deploy code
- `aws_list_instances` - Monitor servers
- `docker_ps` - Check containers
