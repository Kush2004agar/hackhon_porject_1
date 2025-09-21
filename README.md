# PyTerm - Python-Based Command Terminal

A hackathon project for CodeMate Hackathon that implements a Python-based command terminal with natural language processing capabilities.

## Features

- Interactive REPL with command history
- File system operations (ls, cd, pwd, mkdir, rm)
- System monitoring (CPU, memory, process information)
- Natural language to command mapping
- Cross-platform compatibility

## Architecture

```
app/
├── __init__.py
├── cli.py              # REPL, parser, dispatcher
├── commands/
│   ├── __init__.py
│   ├── fs.py           # ls, cd, pwd, mkdir, rm
│   └── sysmon.py       # cpu, mem, ps
├── nlc.py              # NL→command rules
├── utils.py            # path jail, formatting, errors
└── config.py           # ROOT_DIR, history file, constants
main.py                 # thin entrypoint
tests/                  # pytest unit tests
```

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
