import os
from pathlib import Path
from typing import Union
from configs import app_config


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_replace_base() -> Path:
    """
    Get REPLACE_BASE path from config
    
    Returns:
        Path object for REPLACE_BASE
    """
    return Path(app_config.REPLACE_BASE)


def get_output_dir() -> Path:
    """
    Get output directory path from config
    
    Returns:
        Path object for output directory
    """
    return Path(app_config.OUTPUT_DIR)


def join_paths(*paths: Union[str, Path]) -> Path:
    """
    Join multiple path components
    
    Args:
        *paths: Path components to join
        
    Returns:
        Joined path
    """
    result = Path(paths[0])
    for path in paths[1:]:
        result = result / path
    return result


def get_relative_path(full_path: Union[str, Path], base_path: Union[str, Path]) -> str:
    """
    Get relative path from base path
    
    Args:
        full_path: Full path
        base_path: Base path
        
    Returns:
        Relative path string
    """
    full = Path(full_path).resolve()
    base = Path(base_path).resolve()
    try:
        return str(full.relative_to(base))
    except ValueError:
        return str(full)


def ensure_output_dir() -> Path:
    """
    Ensure output directory exists
    
    Returns:
        Path object for output directory
    """
    output_dir = get_output_dir()
    ensure_dir(output_dir)
    return output_dir
