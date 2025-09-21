"""
Tests for CLI module

Tests REPL loop, command parsing, and dispatching functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.cli import PyTermCLI, CommandRegistry, CommandHistory


class TestCommandRegistry:
    """Test CommandRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = CommandRegistry()
        assert registry.commands == {}
        assert registry.command_help == {}
        assert registry.command_categories == {}
    
    def test_register_command(self):
        """Test command registration."""
        registry = CommandRegistry()
        
        def test_func(args):
            return "test output"
        
        registry.register("test", test_func, "Test command", "test_category")
        
        assert "test" in registry.commands
        assert registry.commands["test"] == test_func
        assert registry.command_help["test"] == "Test command"
        assert "test" in registry.command_categories["test_category"]
    
    def test_get_command(self):
        """Test getting registered command."""
        registry = CommandRegistry()
        
        def test_func(args):
            return "test output"
        
        registry.register("test", test_func, "Test command")
        
        retrieved_func = registry.get_command("test")
        assert retrieved_func == test_func
        
        # Test nonexistent command
        assert registry.get_command("nonexistent") is None
    
    def test_list_commands(self):
        """Test listing commands."""
        registry = CommandRegistry()
        
        def test_func(args):
            return "test output"
        
        registry.register("test1", test_func, "Test 1", "category1")
        registry.register("test2", test_func, "Test 2", "category1")
        registry.register("test3", test_func, "Test 3", "category2")
        
        # List all commands
        all_commands = registry.list_commands()
        assert len(all_commands) == 3
        assert "test1" in all_commands
        assert "test2" in all_commands
        assert "test3" in all_commands
        
        # List commands by category
        cat1_commands = registry.list_commands("category1")
        assert len(cat1_commands) == 2
        assert "test1" in cat1_commands
        assert "test2" in cat1_commands


class TestCommandHistory:
    """Test CommandHistory class."""
    
    def test_history_initialization(self):
        """Test history initialization."""
        history = CommandHistory(max_size=10)
        assert history.history == []
        assert history.max_size == 10
        assert history.current_index == 0
    
    def test_add_command(self):
        """Test adding commands to history."""
        history = CommandHistory(max_size=5)
        
        history.add("ls")
        assert len(history.history) == 1
        assert history.history[0] == "ls"
        
        history.add("mkdir test")
        assert len(history.history) == 2
        assert history.history[1] == "mkdir test"
        
        # Test duplicate prevention
        history.add("ls")
        assert len(history.history) == 2  # Should not add duplicate
    
    def test_add_empty_command(self):
        """Test adding empty commands."""
        history = CommandHistory()
        
        history.add("")
        history.add("   ")
        assert len(history.history) == 0
    
    def test_max_size_limit(self):
        """Test maximum size limit."""
        history = CommandHistory(max_size=3)
        
        history.add("cmd1")
        history.add("cmd2")
        history.add("cmd3")
        history.add("cmd4")  # Should remove cmd1
        
        assert len(history.history) == 3
        assert history.history[0] == "cmd2"
        assert history.history[2] == "cmd4"


class TestPyTermCLI:
    """Test PyTermCLI class."""
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = PyTermCLI()
        assert cli.registry is not None
        assert cli.history is not None
        assert cli.running == True
        assert cli.current_dir is not None
    
    def test_parse_command(self):
        """Test command parsing."""
        cli = PyTermCLI()
        
        command, args = cli.parse_command("ls -la")
        assert command == "ls"
        assert args == ["-la"]
        
        command, args = cli.parse_command("mkdir testdir")
        assert command == "mkdir"
        assert args == ["testdir"]
        
        command, args = cli.parse_command("")
        assert command == ""
        assert args == []
    
    def test_execute_command_builtin(self):
        """Test executing built-in commands."""
        cli = PyTermCLI()
        
        # Test help command
        result = cli.execute_command("help", [])
        assert "PyTerm" in result
        assert "Available commands" in result
        
        # Test pwd command
        result = cli.execute_command("pwd", [])
        assert str(cli.current_dir) in result
        
        # Test exit command
        result = cli.execute_command("exit", [])
        assert "Goodbye!" in result
        assert cli.running == False
    
    def test_execute_command_nonexistent(self):
        """Test executing nonexistent command."""
        cli = PyTermCLI()
        
        result = cli.execute_command("nonexistent", [])
        assert "not found" in result
    
    def test_get_prompt(self):
        """Test getting prompt string."""
        cli = PyTermCLI()
        
        prompt = cli.get_prompt()
        assert isinstance(prompt, str)
        assert "pyterm>" in prompt
    
    def test_builtin_commands_registered(self):
        """Test that built-in commands are registered."""
        cli = PyTermCLI()
        
        # Check that essential commands are registered
        assert cli.registry.get_command("help") is not None
        assert cli.registry.get_command("exit") is not None
        assert cli.registry.get_command("pwd") is not None
        assert cli.registry.get_command("ls") is not None
        assert cli.registry.get_command("cd") is not None
        assert cli.registry.get_command("clear") is not None
        assert cli.registry.get_command("history") is not None
    
    def test_filesystem_commands_registered(self):
        """Test that filesystem commands are registered."""
        cli = PyTermCLI()
        
        # Check that filesystem commands are registered
        assert cli.registry.get_command("mkdir") is not None
        assert cli.registry.get_command("rm") is not None
        assert cli.registry.get_command("touch") is not None
        assert cli.registry.get_command("cat") is not None
        assert cli.registry.get_command("cp") is not None
        assert cli.registry.get_command("mv") is not None
    
    def test_system_commands_registered(self):
        """Test that system monitoring commands are registered."""
        cli = PyTermCLI()
        
        # Check that system commands are registered
        assert cli.registry.get_command("cpu") is not None
        assert cli.registry.get_command("mem") is not None
        assert cli.registry.get_command("ps") is not None
        assert cli.registry.get_command("disk") is not None
        assert cli.registry.get_command("uptime") is not None
        assert cli.registry.get_command("net") is not None
    
    def test_natural_language_command_registered(self):
        """Test that natural language command is registered."""
        cli = PyTermCLI()
        
        # Check that nlc command is registered
        assert cli.registry.get_command("nlc") is not None


class TestCLIIntegration:
    """Integration tests for CLI."""
    
    def test_cli_handles_errors_gracefully(self):
        """Test that CLI handles errors gracefully."""
        cli = PyTermCLI()
        
        # Test with invalid command syntax
        try:
            result = cli.parse_command('invalid "unclosed quote')
            # Should not raise exception
        except Exception:
            pytest.fail("CLI should handle invalid syntax gracefully")
    
    def test_cli_works_with_temp_directory(self):
        """Test CLI functionality in temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                cli = PyTermCLI()
                
                # Test directory operations
                result = cli.execute_command("mkdir", ["testdir"])
                assert "created successfully" in result
                assert Path("testdir").exists()
                
                result = cli.execute_command("ls", [])
                assert "testdir" in result
                
            finally:
                os.chdir(original_dir)
    
    def test_cli_command_categories(self):
        """Test that commands are properly categorized."""
        cli = PyTermCLI()
        
        # Check command categories
        filesystem_commands = cli.registry.list_commands("filesystem")
        assert "ls" in filesystem_commands
        assert "mkdir" in filesystem_commands
        assert "rm" in filesystem_commands
        
        system_commands = cli.registry.list_commands("system")
        assert "cpu" in system_commands
        assert "mem" in system_commands
        assert "ps" in system_commands
        
        utility_commands = cli.registry.list_commands("utility")
        assert "help" in utility_commands
        assert "exit" in utility_commands
        assert "clear" in utility_commands
