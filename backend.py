"""System Health Agent Backend with HITL & Summarization Middleware."""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from langchain.agents.middleware import (
    dynamic_prompt, 
    ModelRequest,
    HumanInTheLoopMiddleware,
    SummarizationMiddleware,
)
from langgraph.types import Command

# Load env from config folder
env_path = Path(__file__).parent / "config" / "local.env"
load_dotenv(env_path)

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

memory = MemorySaver()

# ============== TOOLS ==============

import psutil
import time
import httpx


@tool
def get_system_metrics() -> dict:
    """
    Gathers real-time host performance metrics.
    Returns CPU usage %, memory consumption/available, and disk space details.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": {"usage_percent": cpu_percent},
        "memory": {
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "usage_percent": mem.percent
        },
        "disk": {
            "used_gb": round(disk.used / (1024**3), 2),
            "available_gb": round(disk.free / (1024**3), 2),
            "usage_percent": disk.percent
        }
    }


@tool
def check_endpoint_health(url: str) -> dict:
    """
    Checks the health of an HTTP endpoint.
    Sends GET request and reports status code, latency (ms), and headers.
    
    Args:
        url: Target URL to check (e.g., 'https://httpbin.org/status/200')
    """
    try:
        start = time.time()
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
        latency = round((time.time() - start) * 1000, 2)
        
        return {
            "url": url,
            "status_code": resp.status_code,
            "latency_ms": latency,
            "is_healthy": 200 <= resp.status_code < 400
        }
    except Exception as e:
        return {"url": url, "error": str(e), "is_healthy": False}


@tool
def inspect_directory_metadata(dir_path: str) -> dict:
    """
    Inspects structural metadata of a local directory.
    Returns total size, file/subdirectory counts, and extension breakdown.
    READ-ONLY: Does NOT open or view file contents.
    
    Args:
        dir_path: Local folder path to inspect (e.g., './src')
    """
    import os as _os
    
    if not _os.path.exists(dir_path):
        return {"dir_path": dir_path, "error": "Directory does not exist", "exists": False}
    
    if not _os.path.isdir(dir_path):
        return {"dir_path": dir_path, "error": "Path is not a directory", "exists": False}
    
    total_size = 0
    file_count = 0
    subdir_count = 0
    extensions = {}
    
    for root, dirs, files in _os.walk(dir_path):
        subdir_count += len(dirs)
        for f in files:
            file_count += 1
            try:
                total_size += _os.path.getsize(_os.path.join(root, f))
            except:
                pass
            ext = _os.path.splitext(f)[1].lower() or "(no ext)"
            extensions[ext] = extensions.get(ext, 0) + 1
    
    size_str = f"{round(total_size / 1024, 2)} KB" if total_size < 1024*1024 else f"{round(total_size / (1024*1024), 2)} MB"
    
    return {
        "dir_path": dir_path,
        "exists": True,
        "total_size": size_str,
        "file_count": file_count,
        "subdirectory_count": subdir_count,
        "extensions": extensions
    }


tools = [get_system_metrics, check_endpoint_health, inspect_directory_metadata]

# ============== SYSTEM PROMPT ==============

SYSTEM_PROMPT = """You are an Infrastructure Health Specialist agent. Your role is to perform operational health checks and diagnostics.

## Capabilities:
1. **System Metrics**: CPU, memory, disk usage
2. **Endpoint Health**: HTTP status, latency, availability  
3. **Directory Inspection**: Structural metadata only (READ-ONLY)

## IMPORTANT: ALWAYS USE TOOLS
When asked about system metrics, endpoints, or directories - you MUST call the appropriate tool.
Never guess or make up data. Always use the tools to get real information.

## STRICT RULES - REFUSE THESE:
❌ File creation, deletion, or modification
❌ Executing shell commands
❌ Reading file contents (only metadata allowed)
❌ Any non-diagnostic requests

## Response Format:
- ✅ healthy | ⚠️ warning | ❌ critical
- Specific metrics and values
- Brief analysis if issues detected
"""


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"{SYSTEM_PROMPT}\n\nToday's date is: {current_date}."


# ============== AGENT ==============

# Human-in-the-Loop: require approval only for inspect_directory_metadata
hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "get_system_metrics": False,           # Auto-approve - safe read-only
        "check_endpoint_health": False,        # Auto-approve - safe read-only
        "inspect_directory_metadata": {        # Requires human approval
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Directory inspection requires approval before accessing local filesystem"
        },
    },
    description_prefix="⚠️ HITL Required"
)

# Summarization: condense history when reaching 6 messages
summarization_middleware = SummarizationMiddleware(
    model="google_genai:gemini-flash-lite-latest",
    trigger=("messages", 6),   # Trigger summarization at 6 messages
    keep=("messages", 2),      # Keep last 2 messages intact
    verbose=True,              # Debug: log when summarization happens
)

health_agent = create_agent(
    llm,
    tools,
    middleware=[
        dynamic_system_prompt,
        hitl_middleware,
        summarization_middleware,
    ],
    checkpointer=memory  # Required for HITL to persist state across interrupts
)


def stream(text: str, thread_id: str):
    """Stream agent response. Returns chunks including potential HITL interrupts."""
    config = {"configurable": {"thread_id": thread_id}}
    for chunk in health_agent.stream(
        {"messages": [{"role": "user", "content": text}]},
        config=config,
        stream_mode="updates"
    ):
        yield chunk


def resume_with_decision(thread_id: str, decisions: list[dict]):
    """
    Resume paused agent with human decisions.
    
    Args:
        thread_id: Same thread_id used in original invoke
        decisions: List of decision dicts, e.g.:
            [{"type": "approve"}]
            [{"type": "reject", "message": "Not allowed"}]
            [{"type": "edit", "edited_action": {"name": "inspect_directory_metadata", "args": {"dir_path": "./src/tools"}}}]
    """
   
    
    config = {"configurable": {"thread_id": thread_id}}
    result = health_agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2"
    )
    return result


def save_graph_png():
    health_agent.get_graph().draw_mermaid_png(output_file_path="graph.png")


if __name__ == '__main__':
    save_graph_png()
