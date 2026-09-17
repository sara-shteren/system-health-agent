# Project Overview — System Health Agent

## Purpose

Stateful System Health & Diagnostic Agent for the MOJ Advanced Training course (Lesson 2). Uses LangChain's `create_react_agent` with MongoDB persistence.

## Domain

Training exercise — operational health checks, endpoint monitoring, and read-only directory inspection.

## What This Agent Does

1. **System Metrics** — CPU, memory, disk usage via `psutil`
2. **Endpoint Health** — HTTP GET with status code, latency, headers
3. **Directory Inspection** — Structural metadata only (READ-ONLY, no file contents)

## Key Constraints

- **Read-only** — agent cannot create, modify, or delete files
- **No shell commands** — only predefined tools
- **Guardrails enforced** — refuses non-diagnostic requests

## Persistence

MongoDB checkpointer saves conversation state across restarts. Thread ID identifies the session.

## Repository Layout

```
system-health-agent/
├── src/
│   ├── tools/           # 3 diagnostic tools
│   └── agent/           # Agent creation + prompts
├── cli.py               # Entry point
├── docker-compose.yml   # MongoDB
└── .env                 # API keys
```

## External Dependencies

- Google Gemini API (via `langchain-google-genai`)
- MongoDB (local Docker or Atlas)
- No other services
