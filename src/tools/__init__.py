"""Diagnostic tools for System Health Agent."""

from .system_metrics import get_system_metrics
from .endpoint_health import check_endpoint_health
from .directory_inspector import inspect_directory_metadata

ALL_TOOLS = [get_system_metrics, check_endpoint_health, inspect_directory_metadata]
