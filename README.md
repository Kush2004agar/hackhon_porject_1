# PyTerm - My Python Terminal Project 🐍

Hey! This is my Python-based command terminal that I built for the CodeMate Hackathon. 
I wanted to create something that makes terminal commands more intuitive and fun to use.

The idea came from my frustration with remembering all those command flags and options. 
Why should I have to remember `ls -la` when I can just say "show me all the files"? 
So I built this!

## What Makes This Cool 🚀

**Natural Language Commands** - The main feature I'm excited about!
- Instead of `ls`, try "show me the files"
- Instead of `mkdir test`, try "create a folder called test"
- Instead of `ps`, try "what processes are running?"

**Real-time System Monitoring** - Because I'm always curious about my PC
- Live CPU usage with pretty graphs
- Memory usage with visual progress bars
- Process listing with color coding
- Disk usage and network stats

**Secure File Operations** - Learned about security the hard way!
- Path traversal protection (no more `../../../etc/passwd` attacks!)
- Input validation and sanitization
- Safe file operations with proper error handling

**Cross-Platform** - Works everywhere!
- Windows, Linux, macOS support
- Handles different path separators and file systems
- Platform-specific optimizations

## How I Built This 🛠️

**The Journey** - From idea to working terminal:
1. Started with basic file operations (`ls`, `cd`, `pwd`)
2. Added system monitoring because I wanted to see what my PC was doing
3. Got frustrated with command syntax, so I added natural language processing
4. Learned about security vulnerabilities and added protection
5. Made it work on different operating systems
6. Added tons of tests (because bugs are inevitable!)

**Technical Challenges I Solved:**
- **Path Security**: Preventing directory traversal attacks (learned this the hard way!)
- **Cross-Platform**: Making it work on Windows, Linux, and macOS
- **Natural Language**: Converting human speech to terminal commands
- **Real-time Monitoring**: Getting live system data without blocking the UI
- **Error Handling**: Making sure the terminal doesn't crash on bad input

**Architecture Decisions:**
- Modular design so I can add new commands easily
- Command registry pattern for clean command management
- Custom exception classes for better error handling
- Centralized configuration management

## My Code Structure 📁

Here's how I organized everything (because good organization is half the battle!):

```
app/
├── __init__.py          # Package initialization
├── cli.py              # The brain - handles all command parsing and execution
├── commands/
│   ├── __init__.py
│   ├── fs.py           # File operations - the bread and butter
│   ├── sysmon.py       # System monitoring - because I'm nosy about my PC
│   └── codemate.py     # AI-powered code analysis (bonus feature!)
├── nlc.py              # Natural language magic - this was the fun part!
├── utils.py            # Helper functions and security utilities
└── config.py           # All the settings and constants in one place
main.py                 # The entry point - where it all begins
tests/                  # My safety net - because bugs are inevitable!
```

**Why this structure?**
- **Separation of concerns**: Each file has one job
- **Easy to extend**: Adding new commands is simple
- **Clean imports**: No circular dependencies
- **Testable**: Each module can be tested independently

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Testing

```bash
pytest
```

## Author

Hackathon Participant - CodeMate Hackathon
