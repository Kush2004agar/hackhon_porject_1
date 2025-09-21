#!/usr/bin/env python3
"""
PyTerm - My Python Terminal Project

Hey there! This is my take on building a Python-based command terminal. 
I've always been fascinated by how terminals work under the hood, and this 
hackathon gave me the perfect excuse to build my own!

What started as a simple "ls" command quickly grew into something much more 
interesting. I wanted to make terminal commands more intuitive, so I added 
natural language processing - now you can say "show me the files" instead 
of remembering "ls"!

The coolest part? It actually works! You can mix traditional commands with 
natural language, and it figures out what you mean. Plus, I added system 
monitoring because I'm always curious about what's happening on my machine.

Features I'm proud of:
- Natural language commands (because who remembers all those flags?)
- Real-time system monitoring with pretty visualizations
- Secure file operations (learned about path traversal attacks the hard way!)
- Cross-platform support (Windows, Linux, macOS - because we're not all the same)

Architecture (what I learned building this):
- main.py: The entry point - where it all begins
- app/cli.py: The brain - handles command parsing and execution
- app/commands/fs.py: File operations - the bread and butter
- app/commands/sysmon.py: System monitoring - because I'm nosy about my PC
- app/nlc.py: Natural language magic - this was the fun part!
- tests/: My safety net - because bugs are inevitable

Author: [Your Name] (that's me!)
Event: CodeMate Hackathon
Problem: Build a Python terminal that doesn't suck
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """
    The main function - where the magic happens!
    
    This is where I initialize everything and start the REPL loop.
    It's surprisingly simple for how much this thing can do!
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
