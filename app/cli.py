"""
PyTerm CLI Module

Handles the REPL (Read-Eval-Print Loop), command parsing, dispatching,
and command history management.
"""

import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from .config import (
    PROMPT_SYMBOL, CONTINUATION_PROMPT, MAX_HISTORY_SIZE, 
    HISTORY_FILE, COMMAND_CATEGORIES, get_error_message, get_success_message
)
from .utils import (
    PyTermError, PathError, SecurityError, colorize, 
    format_path, truncate_text, ensure_directory,
    get_file_info, format_list, get_relative_path
)


class CommandRegistry:
    """Registry for managing available commands."""
    
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.command_help: Dict[str, str] = {}
        self.command_categories: Dict[str, List[str]] = {}
    
    def register(self, name: str, func: Callable, help_text: str = "", category: str = "general"):
        """
        Register a command function.
        
        Args:
            name: Command name
            func: Command function
            help_text: Help text for the command
            category: Command category
        """
        self.commands[name] = func
        self.command_help[name] = help_text
        
        if category not in self.command_categories:
            self.command_categories[category] = []
        self.command_categories[category].append(name)
    
    def get_command(self, name: str) -> Optional[Callable]:
        """Get a command function by name."""
        return self.commands.get(name)
    
    def list_commands(self, category: Optional[str] = None) -> List[str]:
        """List available commands, optionally filtered by category."""
        if category:
            return self.command_categories.get(category, [])
        return list(self.commands.keys())
    
    def get_help(self, command: str) -> str:
        """Get help text for a command."""
        return self.command_help.get(command, "No help available")


class CommandHistory:
    """Manages command history."""
    
    def __init__(self, max_size: int = MAX_HISTORY_SIZE):
        self.history: List[str] = []
        self.max_size = max_size
        self.current_index = 0
        self._load_history()
    
    def _load_history(self):
        """Load history from file."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f.readlines() if line.strip()]
                # Keep only the most recent entries
                self.history = self.history[-self.max_size:]
        except (OSError, UnicodeDecodeError):
            self.history = []
    
    def _save_history(self):
        """Save history to file."""
        try:
            ensure_directory(HISTORY_FILE.parent)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                for command in self.history:
                    f.write(command + '\n')
        except (OSError, UnicodeDecodeError):
            pass  # Silently fail if we can't save history
    
    def add(self, command: str):
        """Add a command to history."""
        if command.strip() and (not self.history or self.history[-1] != command):
            self.history.append(command)
            if len(self.history) > self.max_size:
                self.history.pop(0)
            self._save_history()
    
    def get_previous(self) -> Optional[str]:
        """Get the previous command in history."""
        if not self.history:
            return None
        
        if self.current_index > 0:
            self.current_index -= 1
        
        return self.history[self.current_index]
    
    def get_next(self) -> Optional[str]:
        """Get the next command in history."""
        if not self.history:
            return None
        
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        else:
            self.current_index = len(self.history)
            return ""
    
    def reset_index(self):
        """Reset history index to the end."""
        self.current_index = len(self.history)
    
    def list_history(self, limit: int = 20) -> List[str]:
        """List recent history entries."""
        return self.history[-limit:] if self.history else []


class PyTermCLI:
    """
    Main CLI class handling REPL loop and command dispatching.
    
    This is the heart of PyTerm - it's where everything comes together!
    I spent a lot of time getting the command parsing and execution just right.
    The natural language fallback was a nice touch that makes the whole thing
    feel more intelligent.
    """
    
    def __init__(self):
        self.registry = CommandRegistry()
        self.history = CommandHistory()
        self.current_dir = Path.cwd()
        self.running = True
        
        # Register built-in commands
        self._register_builtin_commands()
    
    def _register_builtin_commands(self):
        """Register built-in commands."""
        # Utility commands
        self.registry.register("help", self._cmd_help, "Show help information", "utility")
        self.registry.register("exit", self._cmd_exit, "Exit PyTerm", "utility")
        self.registry.register("quit", self._cmd_exit, "Exit PyTerm", "utility")
        self.registry.register("clear", self._cmd_clear, "Clear the screen", "utility")
        self.registry.register("history", self._cmd_history, "Show command history", "utility")
        
        # Basic filesystem commands (built into CLI)
        self.registry.register("pwd", self._cmd_pwd, "Print working directory", "filesystem")
        self.registry.register("cd", self._cmd_cd, "Change directory", "filesystem")
        self.registry.register("ls", self._cmd_ls, "List directory contents", "filesystem")
        
        # Advanced filesystem commands
        from .commands.fs import (
            cmd_mkdir, cmd_rm, cmd_touch, cmd_cat, cmd_cp, cmd_mv,
            cmd_find, cmd_wc, cmd_head, cmd_tail
        )
        
        self.registry.register("mkdir", cmd_mkdir, "Create directories", "filesystem")
        self.registry.register("rm", cmd_rm, "Remove files and directories", "filesystem")
        self.registry.register("touch", cmd_touch, "Create empty files or update timestamps", "filesystem")
        self.registry.register("cat", cmd_cat, "Display file contents", "filesystem")
        self.registry.register("cp", cmd_cp, "Copy files and directories", "filesystem")
        self.registry.register("mv", cmd_mv, "Move or rename files and directories", "filesystem")
        self.registry.register("find", cmd_find, "Find files and directories", "filesystem")
        self.registry.register("wc", cmd_wc, "Count lines, words, and characters", "filesystem")
        self.registry.register("head", cmd_head, "Display first lines of files", "filesystem")
        self.registry.register("tail", cmd_tail, "Display last lines of files", "filesystem")
        
        # System monitoring commands
        from .commands.sysmon import (
            cmd_cpu, cmd_mem, cmd_ps, cmd_disk, cmd_uptime, cmd_net
        )
        
        self.registry.register("cpu", cmd_cpu, "Display CPU usage information", "system")
        self.registry.register("mem", cmd_mem, "Display memory usage information", "system")
        self.registry.register("ps", cmd_ps, "Display running processes", "system")
        self.registry.register("disk", cmd_disk, "Display disk usage information", "system")
        self.registry.register("uptime", cmd_uptime, "Display system uptime", "system")
        self.registry.register("net", cmd_net, "Display network information", "system")
        
        # Natural language processing
        from .nlc import cmd_nlc, process_natural_language
        self.registry.register("nlc", cmd_nlc, "Process natural language commands", "natural")
        
        # CodeMate integration commands
        from .commands.codemate import (
            cmd_compile, cmd_analyze, cmd_optimize, cmd_debug, cmd_generate, cmd_refactor
        )
        
        self.registry.register("compile", cmd_compile, "Compile and analyze code with CodeMate", "codemate")
        self.registry.register("analyze", cmd_analyze, "Analyze code for issues and improvements", "codemate")
        self.registry.register("optimize", cmd_optimize, "Optimize code for better performance", "codemate")
        self.registry.register("debug", cmd_debug, "Debug code issues with AI assistance", "codemate")
        self.registry.register("generate", cmd_generate, "Generate code using AI", "codemate")
        self.registry.register("refactor", cmd_refactor, "Refactor code for better maintainability", "codemate")
    
    def _cmd_help(self, args: List[str]) -> str:
        """Show help information."""
        if not args:
            # Show general help
            help_text = f"{colorize('PyTerm - Python-Based Command Terminal', 'bold')}\n"
            help_text += f"Version: {colorize('1.0.0', 'cyan')}\n\n"
            help_text += f"Available commands:\n"
            
            for category, commands in COMMAND_CATEGORIES.items():
                help_text += f"\n{colorize(category.title(), 'yellow')}:\n"
                for cmd in commands:
                    if cmd in self.registry.commands:
                        help_text += f"  {colorize(cmd, 'green')} - {self.registry.get_help(cmd)}\n"
            
            help_text += f"\nType {colorize('help <command>', 'cyan')} for detailed help on a specific command.\n"
            help_text += f"Type {colorize('exit', 'cyan')} to quit PyTerm.\n"
            return help_text
        
        else:
            # Show help for specific command
            command = args[0]
            if command in self.registry.commands:
                help_text = f"Help for {colorize(command, 'green')}:\n"
                help_text += f"  {self.registry.get_help(command)}\n"
                return help_text
            else:
                return get_error_message("command_not_found", command=command)
    
    def _cmd_exit(self, args: List[str]) -> str:
        """Exit PyTerm."""
        self.running = False
        return "Goodbye!"
    
    def _cmd_clear(self, args: List[str]) -> str:
        """Clear the screen."""
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'cls'], check=False)
        else:
            subprocess.run(['clear'], check=False)
        return ""
    
    def _cmd_history(self, args: List[str]) -> str:
        """Show command history."""
        limit = 20
        if args and args[0].isdigit():
            limit = int(args[0])
        
        history_entries = self.history.list_history(limit)
        if not history_entries:
            return "No command history available."
        
        help_text = f"Command history (last {len(history_entries)} commands):\n"
        for i, cmd in enumerate(history_entries, 1):
            help_text += f"  {i:3d}: {cmd}\n"
        
        return help_text
    
    def _cmd_pwd(self, args: List[str]) -> str:
        """Print working directory."""
        return str(self.current_dir)
    
    def _cmd_cd(self, args: List[str]) -> str:
        """Change directory."""
        if not args:
            # Go to home directory
            new_dir = Path.home()
        else:
            new_dir = self.current_dir / args[0]
        
        try:
            new_dir = new_dir.resolve()
            if not new_dir.exists():
                return get_error_message("file_not_found", path=str(new_dir))
            
            if not new_dir.is_dir():
                return get_error_message("invalid_path", path=str(new_dir))
            
            self.current_dir = new_dir
            os.chdir(str(new_dir))
            return get_success_message("directory_changed", path=str(new_dir))
            
        except (OSError, PermissionError) as e:
            return get_error_message("permission_denied", path=str(new_dir))
    
    def _cmd_ls(self, args: List[str]) -> str:
        """List directory contents."""
        try:
            # Parse arguments
            show_hidden = False
            long_format = False
            target_dir = self.current_dir
            
            for arg in args:
                if arg.startswith('-'):
                    if 'a' in arg:
                        show_hidden = True
                    if 'l' in arg:
                        long_format = True
                else:
                    target_dir = self.current_dir / arg
            
            target_dir = target_dir.resolve()
            
            if not target_dir.exists():
                return get_error_message("file_not_found", path=str(target_dir))
            
            if not target_dir.is_dir():
                return get_error_message("invalid_path", path=str(target_dir))
            
            # Get directory contents
            items = []
            for item in target_dir.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                items.append(item)
            
            # Sort items (directories first, then files)
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            if not items:
                return "Directory is empty."
            
            # Format output
            if long_format:
                output_lines = []
                for item in items:
                    info = get_file_info(item)
                    item_type = "d" if info["is_dir"] else "-"
                    permissions = info["permissions"]
                    size = info["size_formatted"]
                    name = info["name"]
                    
                    if info["is_dir"]:
                        name = colorize(name, "blue")
                    elif info["is_executable"]:
                        name = colorize(name, "green")
                    
                    output_lines.append(f"{item_type}{permissions} {size:>8} {name}")
                
                return "\n".join(output_lines)
            else:
                # Simple list format
                names = []
                for item in items:
                    name = item.name
                    if item.is_dir():
                        name = colorize(name, "blue")
                    elif item.is_file() and os.access(item, os.X_OK):
                        name = colorize(name, "green")
                    names.append(name)
                
                return format_list(names, columns=3)
                
        except (OSError, PermissionError) as e:
            return get_error_message("permission_denied", path=str(target_dir))
    
    def parse_command(self, input_line: str) -> Tuple[str, List[str]]:
        """
        Parse a command line into command and arguments.
        
        Args:
            input_line: Raw input line
            
        Returns:
            Tuple of (command, arguments)
        """
        try:
            # Use shlex for proper shell-like parsing
            parts = shlex.split(input_line.strip())
            if not parts:
                return "", []
            
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            return command, args
            
        except ValueError as e:
            raise PyTermError(f"Invalid command syntax: {e}")
    
    def execute_command(self, command: str, args: List[str]) -> str:
        """
        Execute a command with given arguments.
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            Command output
        """
        try:
            # Get command function
            cmd_func = self.registry.get_command(command)
            if not cmd_func:
                # Try natural language processing as fallback
                return self._try_natural_language(command, args)
            
            # Execute command
            result = cmd_func(args)
            return result if result is not None else ""
            
        except PyTermError as e:
            return colorize(f"Error: {e.message}", "red")
        except Exception as e:
            return colorize(f"Unexpected error: {e}", "red")
    
    def _try_natural_language(self, command: str, args: List[str]) -> str:
        """
        Try to process input as natural language.
        
        Args:
            command: Command name (might be natural language)
            args: Command arguments
            
        Returns:
            Command output or error message
        """
        try:
            from .nlc import process_natural_language
            
            # Combine command and args for natural language processing
            input_text = f"{command} {' '.join(args)}".strip()
            
            # Try to parse as natural language
            parsed_command, parsed_args = process_natural_language(input_text)
            
            if parsed_command:
                # Show what was understood
                command_str = f"{parsed_command} {' '.join(parsed_args)}"
                explanation = f"Understood '{input_text}' as: {colorize(command_str, 'green')}"
                
                # Execute the parsed command
                cmd_func = self.registry.get_command(parsed_command)
                if cmd_func:
                    result = cmd_func(parsed_args)
                    return f"{explanation}\n{result}" if result else explanation
                else:
                    return f"{explanation}\nCommand '{parsed_command}' not found."
            else:
                return get_error_message("command_not_found", command=command)
                
        except Exception as e:
            return get_error_message("command_not_found", command=command)
    
    def get_prompt(self) -> str:
        """Get the current prompt string."""
        try:
            rel_path = get_relative_path(self.current_dir)
            if rel_path == ".":
                prompt = PROMPT_SYMBOL
            else:
                prompt = f"{rel_path}{PROMPT_SYMBOL}"
            
            return colorize(prompt, "cyan")
        except:
            return PROMPT_SYMBOL
    
    def run(self):
        """
        Main REPL loop.
        
        This is where the magic happens! The REPL loop is surprisingly simple
        for how much it can do. I'm proud of how clean and responsive it is.
        """
        print(f"{colorize('PyTerm - Python-Based Command Terminal', 'bold')}")
        print(f"Type {colorize('help', 'cyan')} for available commands or {colorize('exit', 'cyan')} to quit.")
        print("=" * 50)
        
        while self.running:
            try:
                # Get user input
                prompt = self.get_prompt()
                user_input = input(prompt).strip()
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Add to history
                self.history.add(user_input)
                self.history.reset_index()
                
                # Parse and execute command
                command, args = self.parse_command(user_input)
                if command:
                    output = self.execute_command(command, args)
                    if output:
                        print(output)
                
            except KeyboardInterrupt:
                print(f"\n{colorize('Use Ctrl+C twice or type exit to quit.', 'yellow')}")
                continue
            except EOFError:
                print(f"\n{colorize('Goodbye!', 'green')}")
                break
            except Exception as e:
                print(f"{colorize(f'Error: {e}', 'red')}")
                continue
