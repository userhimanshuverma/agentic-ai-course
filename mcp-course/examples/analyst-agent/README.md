# Analyst Agent Example

A data analyst agent using MCP.

## What It Does

- Queries databases
- Generates reports
- Creates visualizations
- Exports data

## Architecture

```
Analyst Agent
    │
    ├─→ MCP Client
    │
    ├─→ SQL Server (MCP)
    ├─→ Chart Server (MCP)
    └─→ Export Server (MCP)
```

## Quick Start

```bash
python agent.py
```

## Tools Used

- `sql_query` - Query databases
- `chart_generate` - Create charts
- `report_export` - Export reports
