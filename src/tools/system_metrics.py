"""System metrics diagnostic tool."""

from typing import Any
import psutil
from langchain_core.tools import tool


@tool
def get_system_metrics() -> dict[str, Any]:
    """
    Gathers real-time host performance metrics.
    Returns CPU usage %, memory consumption/available, and disk space details.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": {"usage_percent": cpu_percent},
        "memory": {
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "usage_percent": memory.percent
        },
        "disk": {
            "used_gb": round(disk.used / (1024**3), 2),
            "available_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "usage_percent": disk.percent
        }
    }
