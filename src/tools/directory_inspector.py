"""Directory metadata inspection tool (READ-ONLY)."""

import os
from typing import Any
from langchain_core.tools import tool


@tool
def inspect_directory_metadata(dir_path: str) -> dict[str, Any]:
    """
    Inspects structural metadata of a local directory.
    Returns total size, file/subdirectory counts, and extension breakdown.
    
    STRICT READ-ONLY: Only returns metadata; does NOT open or view file contents.
    
    Args:
        dir_path: Local folder path to inspect (e.g., './src')
    """
    if not os.path.exists(dir_path):
        return {"dir_path": dir_path, "error": f"Directory does not exist: {dir_path}", "exists": False}
    
    if not os.path.isdir(dir_path):
        return {"dir_path": dir_path, "error": f"Path is not a directory: {dir_path}", "exists": False}
    
    total_size = 0
    file_count = 0
    subdir_count = 0
    extensions = {}
    
    for root, dirs, files in os.walk(dir_path):
        subdir_count += len(dirs)
        for file in files:
            file_count += 1
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except OSError:
                pass
            ext = os.path.splitext(file)[1].lower() or "(no extension)"
            extensions[ext] = extensions.get(ext, 0) + 1
    
    # Format size
    if total_size < 1024:
        size_str = f"{total_size} bytes"
    elif total_size < 1024 * 1024:
        size_str = f"{round(total_size / 1024, 2)} KB"
    else:
        size_str = f"{round(total_size / (1024 * 1024), 2)} MB"
    
    return {
        "dir_path": dir_path,
        "exists": True,
        "total_size_formatted": size_str,
        "file_count": file_count,
        "subdirectory_count": subdir_count,
        "extension_breakdown": extensions
    }
