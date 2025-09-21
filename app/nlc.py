"""
Natural Language Command Parser

Converts natural language input to terminal commands using regex-based rules.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from .config import NL_PATTERNS, get_error_message
from .utils import PyTermError, colorize


class NaturalLanguageParser:
    """Parser for converting natural language to terminal commands."""
    
    def __init__(self):
        self.patterns = NL_PATTERNS.copy()
        self._build_extended_patterns()
    
    def _build_extended_patterns(self):
        """Build extended natural language patterns."""
        # File system operations
        self.patterns.update({
            # Directory operations
            r"create\s+(?:a\s+)?(?:new\s+)?(?:directory|folder|dir)\s+(.+)": "mkdir",
            r"make\s+(?:a\s+)?(?:new\s+)?(?:directory|folder|dir)\s+(.+)": "mkdir",
            r"new\s+(?:directory|folder|dir)\s+(.+)": "mkdir",
            
            r"remove\s+(?:the\s+)?(?:directory|folder|dir)\s+(.+)": "rm -r",
            r"delete\s+(?:the\s+)?(?:directory|folder|dir)\s+(.+)": "rm -r",
            r"erase\s+(?:the\s+)?(?:directory|folder|dir)\s+(.+)": "rm -r",
            
            # File operations
            r"create\s+(?:a\s+)?(?:new\s+)?file\s+(.+)": "touch",
            r"make\s+(?:a\s+)?(?:new\s+)?file\s+(.+)": "touch",
            r"new\s+file\s+(.+)": "touch",
            
            r"remove\s+(?:the\s+)?file\s+(.+)": "rm",
            r"delete\s+(?:the\s+)?file\s+(.+)": "rm",
            r"erase\s+(?:the\s+)?file\s+(.+)": "rm",
            
            # Navigation
            r"go\s+to\s+(.+)": "cd",
            r"navigate\s+to\s+(.+)": "cd",
            r"enter\s+(.+)": "cd",
            r"open\s+(.+)": "cd",
            
            r"where\s+am\s+i": "pwd",
            r"current\s+directory": "pwd",
            r"show\s+current\s+path": "pwd",
            r"what\s+directory\s+am\s+i\s+in": "pwd",
            
            # Listing
            r"show\s+(?:me\s+)?(?:the\s+)?files?": "ls",
            r"list\s+(?:the\s+)?(?:files?|directory)": "ls",
            r"what\s+files\s+are\s+here": "ls",
            r"display\s+(?:the\s+)?files?": "ls",
            r"see\s+(?:the\s+)?files?": "ls",
            
            r"show\s+(?:me\s+)?(?:all\s+)?files?": "ls -a",
            r"list\s+(?:all\s+)?files?": "ls -a",
            r"show\s+hidden\s+files?": "ls -a",
            
            # File content
            r"show\s+(?:me\s+)?(?:the\s+)?contents?\s+of\s+(.+)": "cat",
            r"display\s+(?:the\s+)?contents?\s+of\s+(.+)": "cat",
            r"read\s+(?:the\s+)?file\s+(.+)": "cat",
            r"view\s+(?:the\s+)?file\s+(.+)": "cat",
            r"open\s+(?:the\s+)?file\s+(.+)": "cat",
            
            # Copy and move
            r"copy\s+(.+)": "cp",
            r"duplicate\s+(.+)": "cp",
            r"backup\s+(.+)": "cp",
            
            r"move\s+(.+)": "mv",
            r"rename\s+(.+)": "mv",
            r"relocate\s+(.+)": "mv",
            
            # Search
            r"find\s+(?:files?\s+)?(?:named\s+)?(.+)": "find -name",
            r"search\s+for\s+(.+)": "find -name",
            r"look\s+for\s+(.+)": "find -name",
            r"locate\s+(.+)": "find -name",
            
            # System monitoring
            r"how\s+(?:much\s+)?(?:cpu|processor)\s+(?:usage|load)": "cpu",
            r"cpu\s+(?:usage|load|performance)": "cpu",
            r"processor\s+(?:usage|load)": "cpu",
            r"show\s+(?:me\s+)?(?:the\s+)?cpu": "cpu",
            
            r"how\s+(?:much\s+)?(?:memory|ram)\s+(?:usage|used)": "mem",
            r"memory\s+(?:usage|used|consumption)": "mem",
            r"ram\s+(?:usage|used|consumption)": "mem",
            r"show\s+(?:me\s+)?(?:the\s+)?memory": "mem",
            
            r"show\s+(?:me\s+)?(?:running\s+)?processes?": "ps",
            r"list\s+(?:running\s+)?processes?": "ps",
            r"what\s+processes?\s+are\s+running": "ps",
            r"running\s+programs?": "ps",
            r"active\s+processes?": "ps",
            
            r"disk\s+(?:usage|space|free)": "disk",
            r"how\s+much\s+disk\s+space": "disk",
            r"storage\s+(?:usage|space)": "disk",
            r"show\s+(?:me\s+)?(?:the\s+)?disk": "disk",
            
            r"uptime": "uptime",
            r"how\s+long\s+has\s+(?:the\s+)?system\s+been\s+running": "uptime",
            r"system\s+uptime": "uptime",
            
            r"network\s+(?:info|status|statistics)": "net",
            r"show\s+(?:me\s+)?(?:the\s+)?network": "net",
            r"internet\s+(?:info|status)": "net",
            
            # Help and utility
            r"help\s+me": "help",
            r"what\s+can\s+i\s+do": "help",
            r"show\s+(?:me\s+)?(?:the\s+)?help": "help",
            r"commands?": "help",
            r"available\s+commands?": "help",
            
            r"clear\s+(?:the\s+)?screen": "clear",
            r"clean\s+(?:the\s+)?screen": "clear",
            r"wipe\s+(?:the\s+)?screen": "clear",
            
            r"exit\s+(?:the\s+)?program": "exit",
            r"quit\s+(?:the\s+)?program": "exit",
            r"close\s+(?:the\s+)?terminal": "exit",
            r"bye": "exit",
            r"goodbye": "exit",
        })
    
    def parse(self, input_text: str) -> Tuple[str, List[str]]:
        """
        Parse natural language input and convert to command and arguments.
        
        Args:
            input_text: Natural language input
            
        Returns:
            Tuple of (command, arguments)
        """
        if not input_text or not input_text.strip():
            return "", []
        
        # Normalize input
        text = input_text.strip().lower()
        
        # Try to match against patterns
        for pattern, command in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract arguments from the match
                args = []
                if match.groups():
                    # Extract the captured group and clean it up
                    arg_text = match.group(1).strip()
                    if arg_text:
                        # Split arguments if there are multiple
                        args = [arg.strip() for arg in arg_text.split() if arg.strip()]
                
                return command, args
        
        # If no pattern matches, try keyword-based parsing
        return self._keyword_parse(text)
    
    def _keyword_parse(self, text: str) -> Tuple[str, List[str]]:
        """
        Fallback keyword-based parsing for unmatched input.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (command, arguments)
        """
        words = text.split()
        if not words:
            return "", []
        
        # Keyword mapping
        keyword_map = {
            # File operations
            "create": "mkdir",
            "make": "mkdir", 
            "new": "mkdir",
            "remove": "rm",
            "delete": "rm",
            "erase": "rm",
            
            # Navigation
            "go": "cd",
            "navigate": "cd",
            "enter": "cd",
            "open": "cd",
            "where": "pwd",
            "current": "pwd",
            
            # Listing
            "show": "ls",
            "list": "ls",
            "display": "ls",
            "see": "ls",
            "files": "ls",
            
            # File content
            "read": "cat",
            "view": "cat",
            "contents": "cat",
            
            # System
            "cpu": "cpu",
            "memory": "mem",
            "ram": "mem",
            "processes": "ps",
            "disk": "disk",
            "uptime": "uptime",
            "network": "net",
            
            # Utility
            "help": "help",
            "clear": "clear",
            "exit": "exit",
            "quit": "exit",
        }
        
        # Find the first keyword
        for i, word in enumerate(words):
            if word in keyword_map:
                command = keyword_map[word]
                args = words[i+1:] if i+1 < len(words) else []
                return command, args
        
        # If no keyword found, return empty
        return "", []
    
    def get_suggestions(self, input_text: str) -> List[str]:
        """
        Get command suggestions based on partial input.
        
        Args:
            input_text: Partial input text
            
        Returns:
            List of suggested commands
        """
        if not input_text:
            return []
        
        text = input_text.lower().strip()
        suggestions = []
        
        # Check for partial matches
        for pattern, command in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append(command)
        
        # Add keyword-based suggestions
        words = text.split()
        if words:
            first_word = words[0]
            keyword_map = {
                "cre": "mkdir",
                "mak": "mkdir",
                "new": "mkdir",
                "rem": "rm",
                "del": "rm",
                "go": "cd",
                "sho": "ls",
                "lis": "ls",
                "rea": "cat",
                "cpu": "cpu",
                "mem": "mem",
                "pro": "ps",
                "dis": "disk",
                "net": "net",
                "hel": "help",
                "cle": "clear",
                "exi": "exit",
            }
            
            for prefix, command in keyword_map.items():
                if first_word.startswith(prefix):
                    suggestions.append(command)
        
        return list(set(suggestions))  # Remove duplicates
    
    def explain_translation(self, input_text: str, command: str, args: List[str]) -> str:
        """
        Explain how natural language was translated to command.
        
        Args:
            input_text: Original natural language input
            command: Translated command
            args: Command arguments
            
        Returns:
            Explanation string
        """
        if not command:
            return f"I didn't understand '{input_text}'. Try using specific commands like 'ls', 'mkdir', 'cpu', etc."
        
        args_str = " ".join(args) if args else ""
        full_command = f"{command} {args_str}".strip()
        
        explanation = f"Understood '{input_text}' as: {colorize(full_command, 'green')}"
        
        # Add helpful context
        if command == "mkdir":
            explanation += f"\nThis will create a new directory."
        elif command == "rm":
            explanation += f"\nThis will remove files or directories."
        elif command == "ls":
            explanation += f"\nThis will list directory contents."
        elif command == "cd":
            explanation += f"\nThis will change to the specified directory."
        elif command == "cpu":
            explanation += f"\nThis will show CPU usage information."
        elif command == "mem":
            explanation += f"\nThis will show memory usage information."
        elif command == "ps":
            explanation += f"\nThis will show running processes."
        
        return explanation


def cmd_nlc(args: List[str]) -> str:
    """
    Natural language command processor.
    
    Usage: nlc <natural language command>
    """
    if not args:
        return "Usage: nlc <natural language command>\nExample: nlc 'create folder test'"
    
    # Join all arguments to form the natural language input
    input_text = " ".join(args)
    
    try:
        parser = NaturalLanguageParser()
        command, cmd_args = parser.parse(input_text)
        
        if not command:
            suggestions = parser.get_suggestions(input_text)
            if suggestions:
                return f"I didn't understand '{input_text}'. Did you mean: {', '.join(suggestions)}?"
            else:
                return f"I didn't understand '{input_text}'. Try using specific commands like 'ls', 'mkdir', 'cpu', etc."
        
        # Return the explanation
        return parser.explain_translation(input_text, command, cmd_args)
        
    except Exception as e:
        return f"Error processing natural language: {e}"


def process_natural_language(input_text: str) -> Tuple[str, List[str]]:
    """
    Process natural language input and return command and arguments.
    
    Args:
        input_text: Natural language input
        
    Returns:
        Tuple of (command, arguments)
    """
    parser = NaturalLanguageParser()
    return parser.parse(input_text)
