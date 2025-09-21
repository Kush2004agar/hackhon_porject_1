"""
Configuration Module

This is where I keep all the settings and constants for PyTerm.
I learned that having everything in one place makes the code much easier
to maintain and modify. Plus, it's easier to see what can be configured!

Contains constants, configuration settings, and paths:
- ROOT_DIR - where everything lives
- History file location - so you don't lose your commands
- Application constants - all the magic numbers in one place
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
CODEMATE_CONFIG_FILE = ROOT_DIR / ".codemate_config"

# CLI settings
MAX_HISTORY_SIZE = 1000
PROMPT_SYMBOL = "pyterm> "
CONTINUATION_PROMPT = "... "

# Security settings
MAX_PATH_DEPTH = 50  # Maximum directory depth for security
ALLOWED_PROTOCOLS = ["file"]  # Only allow file:// protocol

# CodeMate settings
CODEMATE_API_BASE_URL = "https://api.codemate.ai/v1"
CODEMATE_TIMEOUT = 30  # seconds
CODEMATE_MAX_FILE_SIZE = 1024 * 1024  # 1MB max file size for analysis
CODEMATE_SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "c"]
CODEMATE_DEFAULT_MODEL = "gpt-4"

# Display settings
PAGE_SIZE = 20  # Number of items to show per page
MAX_OUTPUT_LINES = 1000  # Maximum lines to display at once

# Command categories
COMMAND_CATEGORIES = {
    "filesystem": ["ls", "cd", "pwd", "mkdir", "rm", "cat", "touch"],
    "system": ["cpu", "mem", "ps", "uptime", "disk"],
    "utility": ["help", "exit", "clear", "history"],
    "natural": ["show", "list", "create", "delete", "go", "where"],
    "codemate": ["compile", "analyze", "optimize", "debug", "generate", "refactor"]
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
    "config_error": "Configuration error: {error}",
    "codemate_api_error": "CodeMate API error: {error}",
    "codemate_timeout": "CodeMate request timed out",
    "codemate_file_too_large": "File too large for CodeMate analysis (max {max_size} bytes)",
    "codemate_unsupported_language": "Unsupported language for CodeMate: {language}",
    "codemate_no_api_key": "CodeMate API key not configured. Set CODEMATE_API_KEY environment variable."
}

# Success messages
SUCCESS_MESSAGES = {
    "directory_created": "Directory '{path}' created successfully",
    "file_deleted": "File '{path}' deleted successfully",
    "directory_deleted": "Directory '{path}' deleted successfully",
    "directory_changed": "Changed directory to '{path}'",
    "codemate_analysis_complete": "CodeMate analysis completed for '{file}'",
    "codemate_optimization_complete": "CodeMate optimization completed for '{file}'",
    "codemate_generation_complete": "CodeMate code generation completed",
    "codemate_refactor_complete": "CodeMate refactoring completed for '{file}'"
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
