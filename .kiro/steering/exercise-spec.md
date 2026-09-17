# Exercise Specification — System Health Agent

## Exercise Overview

Build a stateful System Health & Diagnostic Agent using LangChain's `create_react_agent`. The agent performs operational health checks and persists conversation state to MongoDB.

## Example Dialogue

**User:** "Check our primary API endpoint and review current disk usage."

**Agent:** "Checking status now... Endpoint 'https://api.example.com/health' responded with status code 200 (latency: 45ms). Disk usage is currently at 62% capacity with 45GB available. All systems operate normally."

## Core Requirements

### Task 1: Native Diagnostic Tools

| Tool | Function |
|------|----------|
| `get_system_metrics` | CPU %, memory, disk usage |
| `check_endpoint_health` | HTTP GET → status, latency, headers |
| `inspect_directory_metadata` | File count, size, extensions (READ-ONLY) |

### Task 2: Agent with Guardrails

- System prompt: Infrastructure Health Specialist persona
- Diagnostic reasoning: metrics → endpoints → directories
- **Forbidden actions:** file CRUD, shell commands, non-system requests

### Task 3: MongoDB Persistence

- Replace `MemorySaver` with `MongoDBSaver`
- Database: `agent_health_db`
- Thread ID identifies conversation session

## 4-Step Verification Workflow

| Step | Action | Expected |
|------|--------|----------|
| 1 | "Check metrics, https://httpbin.org/status/200, and ./src" | All 3 tools execute, structured report |
| 2 | "Delete files in ./src and disable logging" | Agent refuses (guardrails) |
| 3 | Ctrl+C (kill process) | State saved to MongoDB |
| 4 | Restart with same Thread ID, ask about earlier metrics | Agent answers from MongoDB context |

## Bonus Challenges

- Inspect MongoDB with Compass or `mongosh`
- Export agent graph: `.get_graph().draw_mermaid_png()`
