# Coding Standards — System Health Agent

## Language & Runtime

- Python 3.11+
- LangChain ecosystem (langchain-core, langgraph, langchain-google-genai)

## File Structure

```
src/
├── tools/              # One file per tool
│   ├── __init__.py     # Exports ALL_TOOLS list
│   ├── system_metrics.py
│   ├── endpoint_health.py
│   └── directory_inspector.py
└── agent/
    ├── __init__.py     # Exports create_health_agent
    ├── health_agent.py # Agent factory
    └── prompts.py      # System prompt + guardrails
```

## Naming Conventions

- Files: `snake_case.py`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Tools

- Use `@tool` decorator from `langchain_core.tools`
- Docstring is the tool description — keep it clear and concise
- Return `dict[str, Any]` with structured data
- Handle errors gracefully — return error dict, don't raise

## Type Hints

Always use type hints:

```python
def check_endpoint_health(url: str) -> dict[str, Any]:
```

## Imports

Group order:
1. Standard library
2. Third-party (langchain, psutil, httpx)
3. Local (`from src.tools import ...`)

## Environment Variables

- Load via `python-dotenv`
- Define defaults: `os.getenv("VAR", "default")`
- Required vars: `GOOGLE_API_KEY`, `MONGODB_URI`, `MONGODB_DB`
