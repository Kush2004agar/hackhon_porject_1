"""
Tests for Natural Language Command Parser

Tests NL→command conversion rules and parsing logic.
"""

import pytest
from app.nlc import NaturalLanguageParser, cmd_nlc, process_natural_language


class TestNaturalLanguageParser:
    """Test NaturalLanguageParser class."""
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = NaturalLanguageParser()
        assert parser.patterns is not None
        assert len(parser.patterns) > 0
    
    def test_parse_file_operations(self):
        """Test parsing file operation commands."""
        parser = NaturalLanguageParser()
        
        # Directory operations
        command, args = parser.parse("create folder testdir")
        assert command == "mkdir"
        assert args == ["testdir"]
        
        command, args = parser.parse("make a new directory mydir")
        assert command == "mkdir"
        assert args == ["mydir"]
        
        command, args = parser.parse("delete the file old.txt")
        assert command == "rm"
        assert args == ["old.txt"]
        
        command, args = parser.parse("remove the directory tempdir")
        assert command == "rm -r"
        assert args == ["tempdir"]
    
    def test_parse_navigation_commands(self):
        """Test parsing navigation commands."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("go to documents")
        assert command == "cd"
        assert args == ["documents"]
        
        command, args = parser.parse("navigate to home")
        assert command == "cd"
        assert args == ["home"]
        
        command, args = parser.parse("where am i")
        assert command == "pwd"
        assert args == []
        
        command, args = parser.parse("current directory")
        assert command == "pwd"
        assert args == []
    
    def test_parse_listing_commands(self):
        """Test parsing listing commands."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("show me the files")
        assert command == "ls"
        assert args == []
        
        command, args = parser.parse("list the directory")
        assert command == "ls"
        assert args == []
        
        command, args = parser.parse("show all files")
        assert command == "ls -a"
        assert args == []
        
        command, args = parser.parse("list all files")
        assert command == "ls -a"
        assert args == []
    
    def test_parse_system_monitoring_commands(self):
        """Test parsing system monitoring commands."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("how much cpu usage")
        assert command == "cpu"
        assert args == []
        
        command, args = parser.parse("show me the memory")
        assert command == "mem"
        assert args == []
        
        command, args = parser.parse("show me running processes")
        assert command == "ps"
        assert args == []
        
        command, args = parser.parse("how much disk space")
        assert command == "disk"
        assert args == []
    
    def test_parse_help_commands(self):
        """Test parsing help commands."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("help me")
        assert command == "help"
        assert args == []
        
        command, args = parser.parse("what can i do")
        assert command == "help"
        assert args == []
    
    def test_parse_exit_commands(self):
        """Test parsing exit commands."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("exit the program")
        assert command == "exit"
        assert args == []
        
        command, args = parser.parse("bye")
        assert command == "exit"
        assert args == []
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case insensitive."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("CREATE FOLDER TESTDIR")
        assert command == "mkdir"
        assert args == ["TESTDIR"]
        
        command, args = parser.parse("Show Me The Files")
        assert command == "ls"
        assert args == []
    
    def test_parse_unrecognized_input(self):
        """Test parsing unrecognized input."""
        parser = NaturalLanguageParser()
        
        command, args = parser.parse("random gibberish text")
        assert command == ""  # Should fall back to keyword parsing
        assert args == []
    
    def test_keyword_fallback(self):
        """Test keyword-based fallback parsing."""
        parser = NaturalLanguageParser()
        
        # Test keyword parsing
        command, args = parser.parse("create something")
        assert command == "mkdir"
        assert args == ["something"]
        
        command, args = parser.parse("show something")
        assert command == "ls"
        assert args == ["something"]
    
    def test_get_suggestions(self):
        """Test getting command suggestions."""
        parser = NaturalLanguageParser()
        
        suggestions = parser.get_suggestions("cre")
        assert "mkdir" in suggestions
        
        suggestions = parser.get_suggestions("sho")
        assert "ls" in suggestions
        
        suggestions = parser.get_suggestions("")
        assert suggestions == []
    
    def test_explain_translation(self):
        """Test explanation of translations."""
        parser = NaturalLanguageParser()
        
        explanation = parser.explain_translation("create folder test", "mkdir", ["test"])
        assert "Understood 'create folder test' as:" in explanation
        assert "mkdir test" in explanation
        assert "This will create a new directory" in explanation


class TestCmdNlc:
    """Test cmd_nlc function."""
    
    def test_cmd_nlc_basic(self):
        """Test basic nlc command."""
        result = cmd_nlc(["create folder testdir"])
        assert "Understood" in result
        assert "mkdir testdir" in result
    
    def test_cmd_nlc_no_args(self):
        """Test nlc command with no arguments."""
        result = cmd_nlc([])
        assert "Usage:" in result
        assert "Example:" in result
    
    def test_cmd_nlc_unrecognized(self):
        """Test nlc command with unrecognized input."""
        result = cmd_nlc(["random gibberish"])
        assert "I didn't understand" in result


class TestProcessNaturalLanguage:
    """Test process_natural_language function."""
    
    def test_process_natural_language_basic(self):
        """Test basic natural language processing."""
        command, args = process_natural_language("create folder testdir")
        assert command == "mkdir"
        assert args == ["testdir"]
    
    def test_process_natural_language_empty(self):
        """Test processing empty input."""
        command, args = process_natural_language("")
        assert command == ""
        assert args == []
    
    def test_process_natural_language_unrecognized(self):
        """Test processing unrecognized input."""
        command, args = process_natural_language("random text")
        assert command == ""
        assert args == []
