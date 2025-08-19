"""
File utilities
=============
"""

import pathlib
import re
from typing import Union


def safe_filename(filename: str) -> str:
    """Convert a string to a safe filename."""
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Strip leading/trailing spaces and underscores
    safe_name = safe_name.strip(' _')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"
    
    return safe_name


def ensure_directory(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Ensure a directory exists."""
    path = pathlib.Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path