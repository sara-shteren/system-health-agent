"""Endpoint health check tool."""

import time
from typing import Any
import httpx
from langchain_core.tools import tool


@tool
def check_endpoint_health(url: str) -> dict[str, Any]:
    """
    Checks the health of an HTTP endpoint.
    Sends GET request and reports status code, latency (ms), and headers.
    
    Args:
        url: Target URL to check (e.g., 'https://api.example.com/health')
    """
    try:
        start_time = time.time()
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "url": url,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "headers": dict(response.headers),
            "is_healthy": 200 <= response.status_code < 400
        }
    except httpx.TimeoutException:
        return {"url": url, "error": "Request timed out", "is_healthy": False}
    except httpx.RequestError as e:
        return {"url": url, "error": str(e), "is_healthy": False}
