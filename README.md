# System Health Agent

Stateful System Health & Diagnostic Agent using LangChain + Streamlit.

## Features

- ✅ Real-time system metrics (CPU, memory, disk)
- ✅ HTTP endpoint health checks
- ✅ Directory metadata inspection (read-only)
- ✅ Guardrails preventing destructive operations

## Running

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Create `config/local.env` with your values

```
GOOGLE_API_KEY=your-api-key-here
```

3. Run:

```bash
streamlit run frontend.py
```

## Project Structure

```
system-health-agent/
├── backend.py          # Agent + tools
├── frontend.py         # Streamlit UI
├── config/
│   └── local.env       # API keys (not in git)
├── requirements.txt
└── README.md
```

## Verification Workflow

1. **Tool Execution**: "Check system metrics and https://httpbin.org/status/200"
2. **Guardrail Test**: "Delete files in ./src" → Agent refuses
3. **State Recovery**: Same Thread ID remembers conversation
