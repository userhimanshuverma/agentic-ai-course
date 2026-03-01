# Support Agent Example

A customer support agent using MCP.

## What It Does

- Creates support tickets
- Sends notifications
- Responds to customers
- Escalates issues

## Architecture

```
Support Agent
    │
    ├─→ MCP Client
    │
    ├─→ Jira Server (MCP)
    ├─→ Slack Server (MCP)
    └─→ Email Server (MCP)
```

## Quick Start

```bash
python agent.py
```

## Tools Used

- `jira_create_ticket` - Create tickets
- `slack_send_message` - Notify team
- `email_send` - Respond to customers
