#!/usr/bin/env python3
"""
PyTerm Live Demo

Direct demonstration of PyTerm features.
"""

import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.cli import PyTermCLI
from app.config import ensure_config_dir

def run_live_demo():
    """Run a live demonstration of PyTerm."""
    print("=" * 60)
    print(" PyTerm Live Demo - CodeMate Hackathon")
    print("=" * 60)
    
    # Ensure config directory exists
    ensure_config_dir()
    
    # Initialize CLI
    cli = PyTermCLI()
    
    # Demo commands showcasing different features
    demo_commands = [
        ("help", "Show available commands"),
        ("pwd", "Show current directory"),
        ("mkdir demo_folder", "Create a demo folder"),
        ("touch demo_file.txt", "Create a demo file"),
        ("ls -la", "List files with details"),
        ("cpu", "Show CPU usage"),
        ("mem", "Show memory usage"),
        ("ps -n 5", "Show top 5 processes"),
        ("create folder nlc_demo", "Natural language: create folder"),
        ("show me the files", "Natural language: list files"),
        ("where am i", "Natural language: show current directory"),
        ("how much cpu usage", "Natural language: show CPU usage"),
        ("rm -r demo_folder", "Remove demo folder"),
        ("rm -r nlc_demo", "Remove NLC demo folder"),
        ("rm demo_file.txt", "Remove demo file"),
    ]
    
    print("\nRunning PyTerm demonstration...")
    print("-" * 40)
    
    for i, (cmd, description) in enumerate(demo_commands, 1):
        print(f"\n[{i:2d}] {description}")
        print(f"Command: {cmd}")
        print("-" * 30)
        
        try:
            command, args = cli.parse_command(cmd)
            if command:
                output = cli.execute_command(command, args)
                if output:
                    print(output)
            else:
                print("Command not recognized")
        except Exception as e:
            print(f"Error: {e}")
        
        # Small delay for demo effect
        time.sleep(0.8)
    
    print("\n" + "=" * 60)
    print(" Demo completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_live_demo()
