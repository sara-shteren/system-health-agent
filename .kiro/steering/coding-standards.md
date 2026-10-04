# Coding Standards — System Health Agent

## Language & Runtime

- Python 3.11+
- LangChain ecosystem (langchain-core, langgraph, langchain-google-genai)

## Project Style Reference

**Philosophy: Simple but scalable** — start flat, expand when needed.

This project follows the style of `moj-adv-training` (tax_agent):
- Start simple: `backend.py` + `frontend.py` at root
- Streamlit for UI
- `create_agent` with `middleware` for dynamic prompts

**When to expand:**
- Multiple tools → move to `src/tools/` folder
- Complex agent logic → move to `src/agent/` folder  
- Multiple services → follow `moj-dc-chat` structure

Reference `moj-dc-chat` for production patterns:
- Folder organization (`src/`, `endpoints/`, `helpers/`, `services/`)
- Environment file patterns (`config/local.env`)
- Launch.json structure for VS Code
- Error handling patterns

## File Structure (Current)

```
system-health-agent/
├── backend.py              # Agent + tools + LLM setup
├── frontend.py             # Streamlit UI
├── waiting_messages.py     # Funny waiting messages (no LLM)
├── config/
│   └── local.env           # API keys (gitignored)
├── .kiro/steering/         # Project rules
└── requirements.txt
```

## Key Patterns Learned

1. **Model selection**: Use `gemini-flash-lite-latest` (working model for Google AI Studio free tier)
2. **Environment loading**: `load_dotenv(Path(__file__).parent / "config" / "local.env")`
3. **Dynamic prompt**: Use `@dynamic_prompt` decorator with `middleware=[dynamic_system_prompt]`
4. **Tool enforcement**: Add "ALWAYS USE TOOLS" in system prompt to prevent hallucination
5. **Waiting UX**: Bouncing emoji + funny messages during processing (no LLM cost)

## Naming Conventions

- Files: `snake_case.py`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Tools

- Use `@tool` decorator from `langchain_core.tools`
- Docstring = tool description
- Return `dict` with structured data
- Handle errors gracefully — return error dict, don't raise

## Type Hints

Always use type hints:

```python
def check_endpoint_health(url: str) -> dict:
```

## Imports

Group order:
1. Standard library
2. Third-party (langchain, psutil, httpx, streamlit)
3. Local (`from backend import stream`)
