#!/usr/bin/env python3
"""
PyTerm - Python-Based Command Terminal

A hackathon project for CodeMate Hackathon that implements a Python-based command terminal
with natural language processing capabilities. PyTerm provides a REPL (Read-Eval-Print Loop)
interface for executing file system operations, system monitoring commands, and basic terminal
functionality with intelligent command interpretation.

Features:
- Interactive REPL with command history
- File system operations (ls, cd, pwd, mkdir, rm)
- System monitoring (CPU, memory, process information)
- Natural language to command mapping
- Cross-platform compatibility

Architecture:
- main.py: Entry point and application initialization
- app/cli.py: REPL loop, command parser, and dispatcher
- app/commands/fs.py: File system command implementations
- app/commands/sysmon.py: System monitoring command implementations
- app/nlc.py: Natural language command parser
- tests/: Unit tests using pytest

Author: Hackathon Participant
Event: CodeMate Hackathon
Problem Statement: Problem 1 - Python-Based Command Terminal
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """
    Main entry point for PyTerm application.
    
    Initializes the command terminal and starts the REPL loop.
    """
    try:
        from app.cli import PyTermCLI
        from app.config import ensure_config_dir
        
        # Ensure configuration directory exists
        ensure_config_dir()
        
        # Initialize and run CLI
        cli = PyTermCLI()
        cli.run()
        
    except ImportError as e:
        print(f"Error importing PyTerm modules: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting PyTerm: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
