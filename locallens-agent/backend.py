"""LocalLens - Multimodal Document Search Agent Backend."""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

load_dotenv(Path(__file__).parent / "config" / "local.env")

memory = MemorySaver()

SYSTEM_PROMPT = """You are LocalLens, a private desktop document search assistant.
Your job is to help the user find files, inspect specifications, and answer questions based on the allowed directory.

Workflow:
1. Locate relevant files using `glob` (by name/extension) or `grep` (by keyword in text).
2. For specific files (including PDFs and images), use `read_file` to view their contents.
3. Always cite the relative file path and specific details in your final answer.

STRICT RULES:
- You can ONLY access files within the allowed directory
- You are READ-ONLY - no file creation, modification, or deletion
- If asked to access files outside the directory, politely refuse
"""


def create_locallens_agent(folder_path: str):
    """Create a sandboxed document search agent for the given folder."""
    abs_folder = str(Path(folder_path).resolve())
    
    # 1. Sandbox backend to the chosen folder
    backend = FilesystemBackend(root_dir=abs_folder, virtual_mode=True)
    
    # 2. Expose search & inspection tools (read-only)
    fs_middleware = FilesystemMiddleware(
        backend=backend,
        tools=["ls", "glob", "grep", "read_file"]
    )
    
    # 3. Initialize multimodal LLM
    llm = init_chat_model(
        "gemini-flash-lite-latest",
        model_provider="google_genai",
        temperature=0.1
    )
    
    # 4. Create agent with middleware
    return create_agent(
        model=llm,
        middleware=[fs_middleware],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory
    )


# Global agent - will be set when user chooses folder
_agent = None
_current_folder = None


def set_folder(folder_path: str):
    """Set the folder and create a new agent."""
    global _agent, _current_folder
    _current_folder = folder_path
    _agent = create_locallens_agent(folder_path)
    return f"LocalLens initialized for: {folder_path}"


def get_current_folder():
    """Get the currently configured folder."""
    return _current_folder


def stream(text: str, thread_id: str):
    """Stream agent response."""
    if _agent is None:
        raise ValueError("No folder set. Call set_folder() first.")
    
    config = {"configurable": {"thread_id": thread_id}}
    for chunk in _agent.stream(
        {"messages": [{"role": "user", "content": text}]},
        config=config,
        stream_mode="updates"
    ):
        yield chunk


def save_graph_png():
    """Save agent graph visualization."""
    if _agent:
        _agent.get_graph().draw_mermaid_png(output_file_path="locallens_graph.png")


if __name__ == '__main__':
    # Test with sample folder
    set_folder("./my_vault")
    save_graph_png()
