"""
Configuration Module

Contains constants, configuration settings, and paths:
- ROOT_DIR
- History file location
- Application constants
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project root directory (where main.py is located)
ROOT_DIR = Path(__file__).parent.parent

# Application configuration
APP_NAME = "PyTerm"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Python-Based Command Terminal"

# File paths
HISTORY_FILE = ROOT_DIR / ".pyterm_history"
CONFIG_FILE = ROOT_DIR / ".pyterm_config"

# CLI settings
MAX_HISTORY_SIZE = 1000
PROMPT_SYMBOL = "pyterm> "
CONTINUATION_PROMPT = "... "

# Security settings
MAX_PATH_DEPTH = 50  # Maximum directory depth for security
ALLOWED_PROTOCOLS = ["file"]  # Only allow file:// protocol

# Display settings
PAGE_SIZE = 20  # Number of items to show per page
MAX_OUTPUT_LINES = 1000  # Maximum lines to display at once

# Command categories
COMMAND_CATEGORIES = {
    "filesystem": ["ls", "cd", "pwd", "mkdir", "rm", "cat", "touch"],
    "system": ["cpu", "mem", "ps", "uptime", "disk"],
    "utility": ["help", "exit", "clear", "history"],
    "natural": ["show", "list", "create", "delete", "go", "where"]
}

# Natural language patterns (basic regex patterns)
NL_PATTERNS = {
    r"show\s+(?:me\s+)?(?:the\s+)?files?": "ls",
    r"list\s+(?:the\s+)?(?:files?|directory)": "ls",
    r"go\s+to\s+(.+)": "cd",
    r"where\s+am\s+i": "pwd",
    r"create\s+(?:a\s+)?(?:directory|folder)\s+(.+)": "mkdir",
    r"delete\s+(?:the\s+)?(?:file|directory)\s+(.+)": "rm",
    r"how\s+(?:much\s+)?(?:cpu|memory|ram)": "cpu",
    r"show\s+(?:me\s+)?(?:running\s+)?processes?": "ps"
}

# Error messages
ERROR_MESSAGES = {
    "command_not_found": "Command '{command}' not found. Type 'help' for available commands.",
    "permission_denied": "Permission denied: {path}",
    "file_not_found": "File or directory not found: {path}",
    "invalid_path": "Invalid path: {path}",
    "path_too_deep": "Path exceeds maximum depth limit",
    "unsafe_operation": "Unsafe operation detected: {operation}",
    "history_error": "Error accessing command history",
    "config_error": "Configuration error: {error}"
}

# Success messages
SUCCESS_MESSAGES = {
    "directory_created": "Directory '{path}' created successfully",
    "file_deleted": "File '{path}' deleted successfully",
    "directory_deleted": "Directory '{path}' deleted successfully",
    "directory_changed": "Changed directory to '{path}'"
}

# Color codes for terminal output (ANSI escape sequences)
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m"
}

def get_config() -> Dict[str, Any]:
    """
    Get the current configuration as a dictionary.
    
    Returns:
        Dict containing all configuration settings
    """
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "root_dir": str(ROOT_DIR),
        "history_file": str(HISTORY_FILE),
        "config_file": str(CONFIG_FILE),
        "max_history_size": MAX_HISTORY_SIZE,
        "prompt_symbol": PROMPT_SYMBOL,
        "max_path_depth": MAX_PATH_DEPTH,
        "page_size": PAGE_SIZE,
        "max_output_lines": MAX_OUTPUT_LINES,
        "command_categories": COMMAND_CATEGORIES,
        "nl_patterns": NL_PATTERNS
    }

def ensure_config_dir() -> None:
    """
    Ensure that the configuration directory exists.
    Creates necessary directories if they don't exist.
    """
    try:
        # Ensure ROOT_DIR exists
        ROOT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create history file if it doesn't exist
        if not HISTORY_FILE.exists():
            HISTORY_FILE.touch()
            
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create config directory: {e}")

def is_safe_path(path: str) -> bool:
    """
    Check if a path is safe to use (prevents directory traversal attacks).
    
    Args:
        path: The path to check
        
    Returns:
        True if the path is safe, False otherwise
    """
    try:
        # Convert to absolute path
        abs_path = Path(path)
        if not abs_path.is_absolute():
            abs_path = abs_path.resolve()
        
        # Check if path is within ROOT_DIR
        try:
            abs_path.relative_to(ROOT_DIR.resolve())
        except ValueError:
            return False
            
        # Check path depth
        path_parts = abs_path.parts
        if len(path_parts) > MAX_PATH_DEPTH:
            return False
            
        return True
        
    except (OSError, ValueError):
        return False

def get_error_message(error_key: str, **kwargs) -> str:
    """
    Get a formatted error message.
    
    Args:
        error_key: The error message key
        **kwargs: Format parameters
        
    Returns:
        Formatted error message
    """
    template = ERROR_MESSAGES.get(error_key, "Unknown error: {error}")
    return template.format(**kwargs)

def get_success_message(success_key: str, **kwargs) -> str:
    """
    Get a formatted success message.
    
    Args:
        success_key: The success message key
        **kwargs: Format parameters
        
    Returns:
        Formatted success message
    """
    template = SUCCESS_MESSAGES.get(success_key, "Operation completed successfully")
    return template.format(**kwargs)
