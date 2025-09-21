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

## 🎬 Demo & Screenshots

### Quick Demo
```bash
$ python main.py
PyTerm - Python-Based Command Terminal
Type help for available commands or exit to quit.
==================================================
pyterm> show me the files
app/  main.py  README.md  requirements.txt  tests/
pyterm> create a folder called demo
Created directory: demo
pyterm> what processes are running?
PID    Name                    CPU%    Memory%   Status
1234   python.exe              2.5     1.2       running
5678   chrome.exe              15.3    8.7       running
pyterm> how much memory am I using?
Memory Usage: 45.2% (7.2 GB / 16 GB)
pyterm> exit
```

### Natural Language Magic ✨
```
Traditional Commands → Natural Language
ls                   → "show me the files"
mkdir logs           → "create a folder called logs"
cd Desktop           → "go to the desktop"
ps                   → "what processes are running?"
mem                  → "how much memory am I using?"
cpu                  → "show me CPU usage"
```

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

## 📋 Complete Command Reference

### File System Commands
| Command | Natural Language | Description |
|---------|------------------|-------------|
| `ls` | "show me the files" | List directory contents |
| `cd <dir>` | "go to <dir>" | Change directory |
| `pwd` | "where am I" | Show current directory |
| `mkdir <name>` | "create a folder called <name>" | Create directory |
| `rm <file>` | "delete <file>" | Remove file/directory |
| `cat <file>` | "show me <file>" | Display file contents |
| `touch <file>` | "create <file>" | Create empty file |
| `cp <src> <dst>` | "copy <src> to <dst>" | Copy file |
| `mv <src> <dst>` | "move <src> to <dst>" | Move/rename file |
| `find <pattern>` | "find <pattern>" | Search for files |
| `wc <file>` | "count words in <file>" | Word count |
| `head <file>` | "show first lines of <file>" | Show first lines |
| `tail <file>` | "show last lines of <file>" | Show last lines |

### System Monitoring Commands
| Command | Natural Language | Description |
|---------|------------------|-------------|
| `cpu` | "show me CPU usage" | CPU information and usage |
| `mem` | "how much memory am I using?" | Memory usage statistics |
| `ps [limit]` | "what processes are running?" | Process list |
| `disk` | "show disk usage" | Disk space information |
| `uptime` | "how long has system been up?" | System uptime |
| `net` | "show network info" | Network interface information |

### Built-in Commands
| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `clear` | Clear the screen |
| `history` | Show command history |
| `nlc <text>` | Process natural language command |
| `exit` | Exit PyTerm |

## 🧪 Natural Language Examples

PyTerm understands various ways to express the same command:

### File Operations
```
"show me the files" → ls
"list everything" → ls
"what's in here" → ls
"create a folder called logs" → mkdir logs
"make a directory named test" → mkdir test
"go to the desktop" → cd Desktop
"navigate to home" → cd ~
"where am I" → pwd
"what directory am I in" → pwd
```

### System Monitoring
```
"what processes are running?" → ps
"show me running processes" → ps
"how much memory am I using?" → mem
"what's my memory usage?" → mem
"show me CPU usage" → cpu
"how's my CPU doing?" → cpu
"show disk usage" → disk
"how much disk space?" → disk
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Quick Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd PyTerm

# Install dependencies
pip install -r requirements.txt

# Run PyTerm
python main.py
```

### Dependencies
- `psutil` - System monitoring (CPU, memory, processes)
- `colorama` - Cross-platform colored terminal output
- `pytest` - Testing framework

## Usage

### Basic Usage
```bash
python main.py
```

### Interactive Mode
Once PyTerm starts, you can:
1. Use traditional commands: `ls`, `cd`, `mkdir`, etc.
2. Use natural language: "show me the files", "create a folder called test"
3. Mix both approaches seamlessly
4. Type `help` for available commands
5. Type `exit` to quit

### Command Line Arguments
```bash
python main.py --help          # Show help
python main.py --version       # Show version
python main.py --demo          # Run demo mode
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
pytest tests/test_cli.py       # CLI functionality
pytest tests/test_nlc.py       # Natural language processing
pytest tests/test_sysmon.py    # System monitoring
pytest tests/test_fs.py        # File system operations
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html
```

## 🔮 Future Roadmap

### Planned Features
- **Plugin System**: Allow third-party command extensions
- **Command Aliases**: User-defined command shortcuts
- **Scripting Support**: Run multiple commands in sequence
- **GUI Configuration**: Graphical settings interface
- **Remote Execution**: Run commands on remote machines
- **Command History Search**: Search through command history
- **Auto-completion**: Tab completion for commands and paths
- **Themes**: Customizable color schemes and themes

### Potential Integrations
- **Git Integration**: Built-in git commands and status
- **Docker Support**: Container management commands
- **Cloud Integration**: AWS, Azure, GCP command shortcuts
- **Database Commands**: SQL query execution and management

## 🤝 Contributing

I'd love to see contributions! Here's how you can help:

### Bug Reports
- Use the issue tracker to report bugs
- Include steps to reproduce the issue
- Specify your operating system and Python version

### Feature Requests
- Suggest new natural language patterns
- Propose new command categories
- Request system monitoring improvements

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Submit a pull request

### Areas for Contribution
- **Natural Language Patterns**: Add more ways to express commands
- **New Commands**: Implement additional file system or system commands
- **Cross-Platform**: Improve Windows/Linux/macOS compatibility
- **Documentation**: Improve README, add tutorials, create examples
- **Testing**: Add more test cases, improve coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Libraries & Tools
- **psutil** - Amazing system monitoring library
- **colorama** - Cross-platform colored output
- **pytest** - Robust testing framework
- **pathlib** - Modern path handling

### Inspiration
- **Unix Philosophy** - "Do one thing and do it well"
- **Modern Terminal Emulators** - iTerm2, Windows Terminal, etc.
- **Natural Language Interfaces** - Voice assistants and chatbots
- **Developer Experience** - Making tools more intuitive

### Learning Resources
- Python documentation and tutorials
- Security best practices for file operations
- Cross-platform development techniques
- Natural language processing concepts

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/PyTerm/issues)
- **Email**: your.email@example.com
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

## 🏆 Hackathon Details

**Event**: CodeMate Hackathon  
**Category**: Developer Tools  
**Duration**: 48 hours  
**Team**: Solo project  
**Technologies**: Python, psutil, natural language processing, cross-platform development

### What I Learned
- **Security**: Path traversal attacks and prevention
- **Architecture**: Modular design and separation of concerns
- **Testing**: Comprehensive test coverage and cross-platform testing
- **UX**: Making technical tools more intuitive and user-friendly
- **Cross-Platform**: Handling different operating systems gracefully

---

**Built with ❤️ and a lot of coffee ☕**

*This project represents my journey from idea to working terminal, combining technical excellence with personal passion for making developer tools more intuitive and fun to use.*