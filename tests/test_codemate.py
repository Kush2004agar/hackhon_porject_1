"""
Tests for CodeMate Integration Commands

Tests CodeMate compiler service integration functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.commands.codemate import (
    CodeMateAPI, cmd_compile, cmd_analyze, cmd_optimize, 
    cmd_debug, cmd_generate, cmd_refactor
)


class TestCodeMateAPI:
    """Test CodeMateAPI class."""
    
    def test_api_initialization_with_key(self):
        """Test API initialization with API key."""
        with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
            api = CodeMateAPI()
            assert api.api_key == 'test-key'
            assert api.base_url == 'https://api.codemate.ai/v1'
            assert api.timeout == 30
    
    def test_api_initialization_without_key(self):
        """Test API initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            api = CodeMateAPI()
            assert api.api_key is None
    
    def test_check_api_key_with_key(self):
        """Test API key check with key present."""
        with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
            api = CodeMateAPI()
            # Should not raise exception
            api._check_api_key()
    
    def test_check_api_key_without_key(self):
        """Test API key check without key."""
        with patch.dict(os.environ, {}, clear=True):
            api = CodeMateAPI()
            with pytest.raises(Exception):  # PyTermError
                api._check_api_key()
    
    def test_validate_file_valid(self):
        """Test file validation with valid file."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("hello world")')
            f.flush()
            
            try:
                api = CodeMateAPI()
                language = api._validate_file(Path(f.name))
                assert language == 'python'
            finally:
                os.unlink(f.name)
    
    def test_validate_file_nonexistent(self):
        """Test file validation with nonexistent file."""
        api = CodeMateAPI()
        with pytest.raises(Exception):  # PathError
            api._validate_file(Path('/nonexistent/file.py'))
    
    def test_validate_file_too_large(self):
        """Test file validation with file too large."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            # Create a large file (simulate)
            f.write(b'x' * (1024 * 1024 + 1))  # 1MB + 1 byte
            f.flush()
            
            try:
                api = CodeMateAPI()
                with pytest.raises(Exception):  # PyTermError
                    api._validate_file(Path(f.name))
            finally:
                os.unlink(f.name)
    
    @patch('requests.Session.post')
    def test_analyze_code_success(self, mock_post):
        """Test successful code analysis."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'summary': 'Code analysis complete',
            'issues': [],
            'suggestions': ['Add comments'],
            'metrics': {'complexity': 'low'}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(b'print("hello")')
                f.flush()
                
                try:
                    api = CodeMateAPI()
                    result = api.analyze_code(Path(f.name))
                    assert 'summary' in result
                    assert result['summary'] == 'Code analysis complete'
                finally:
                    os.unlink(f.name)
    
    @patch('requests.Session.post')
    def test_analyze_code_timeout(self, mock_post):
        """Test code analysis timeout."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(b'print("hello")')
                f.flush()
                
                try:
                    api = CodeMateAPI()
                    with pytest.raises(Exception):  # PyTermError
                        api.analyze_code(Path(f.name))
                finally:
                    os.unlink(f.name)


class TestCompileCommand:
    """Test compile command."""
    
    def test_compile_no_args(self):
        """Test compile command with no arguments."""
        result = cmd_compile([])
        assert "Usage:" in result
    
    def test_compile_no_file(self):
        """Test compile command with no file specified."""
        result = cmd_compile(['-a', 'comprehensive'])
        assert "Error: No file specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.analyze_code')
    def test_compile_success(self, mock_analyze):
        """Test successful compilation."""
        mock_analyze.return_value = {
            'summary': 'Analysis complete',
            'issues': [],
            'suggestions': ['Add comments'],
            'metrics': {'complexity': 'low'}
        }
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("hello")')
            f.flush()
            
            try:
                with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
                    result = cmd_compile([f.name])
                    assert "CodeMate Compilation Results" in result
                    assert "Analysis complete" in result
            finally:
                os.unlink(f.name)
    
    def test_compile_nonexistent_file(self):
        """Test compile command with nonexistent file."""
        result = cmd_compile(['nonexistent.py'])
        assert "Error:" in result


class TestAnalyzeCommand:
    """Test analyze command."""
    
    def test_analyze_no_args(self):
        """Test analyze command with no arguments."""
        result = cmd_analyze([])
        assert "Usage:" in result
    
    def test_analyze_no_file(self):
        """Test analyze command with no file specified."""
        result = cmd_analyze(['-t', 'security'])
        assert "Error: No file specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.analyze_code')
    def test_analyze_success(self, mock_analyze):
        """Test successful analysis."""
        mock_analyze.return_value = {
            'detailed_analysis': 'Detailed analysis results',
            'security': {
                'vulnerabilities': ['Potential SQL injection'],
                'recommendations': ['Use parameterized queries']
            },
            'performance': {
                'bottlenecks': ['Slow database query'],
                'optimizations': ['Add database index']
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("hello")')
            f.flush()
            
            try:
                with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
                    result = cmd_analyze(['-d', f.name])
                    assert "CodeMate Analysis Results" in result
                    assert "Detailed analysis results" in result
            finally:
                os.unlink(f.name)


class TestOptimizeCommand:
    """Test optimize command."""
    
    def test_optimize_no_args(self):
        """Test optimize command with no arguments."""
        result = cmd_optimize([])
        assert "Usage:" in result
    
    def test_optimize_no_file(self):
        """Test optimize command with no file specified."""
        result = cmd_optimize(['-l', 'aggressive'])
        assert "Error: No file specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.optimize_code')
    def test_optimize_success(self, mock_optimize):
        """Test successful optimization."""
        mock_optimize.return_value = {
            'summary': 'Optimization complete',
            'optimized_code': 'print("optimized hello")',
            'improvements': ['Reduced complexity'],
            'performance_gains': ['Faster execution']
        }
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("hello")')
            f.flush()
            
            try:
                with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
                    result = cmd_optimize([f.name])
                    assert "CodeMate Optimization Results" in result
                    assert "Optimization complete" in result
            finally:
                os.unlink(f.name)


class TestDebugCommand:
    """Test debug command."""
    
    def test_debug_no_args(self):
        """Test debug command with no arguments."""
        result = cmd_debug([])
        assert "Usage:" in result
    
    def test_debug_no_file(self):
        """Test debug command with no file specified."""
        result = cmd_debug(['-e', 'SyntaxError'])
        assert "Error: No file specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.debug_code')
    def test_debug_success(self, mock_debug):
        """Test successful debugging."""
        mock_debug.return_value = {
            'issues': [{'description': 'Syntax error', 'line': 1, 'code': 'print('}],
            'fixes': [{'description': 'Add closing parenthesis', 'code': 'print("hello")'}],
            'root_cause': 'Missing closing parenthesis',
            'prevention_tips': ['Use IDE with syntax highlighting']
        }
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("hello")')
            f.flush()
            
            try:
                with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
                    result = cmd_debug([f.name])
                    assert "CodeMate Debug Results" in result
                    assert "Syntax error" in result
            finally:
                os.unlink(f.name)


class TestGenerateCommand:
    """Test generate command."""
    
    def test_generate_no_args(self):
        """Test generate command with no arguments."""
        result = cmd_generate([])
        assert "Usage:" in result
    
    def test_generate_no_prompt(self):
        """Test generate command with no prompt."""
        result = cmd_generate(['-l', 'python'])
        assert "Error: No prompt specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.generate_code')
    def test_generate_success(self, mock_generate):
        """Test successful code generation."""
        mock_generate.return_value = {
            'generated_code': 'def hello():\n    print("Hello, World!")',
            'explanation': 'This function prints a greeting',
            'usage_examples': ['hello()']
        }
        
        with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
            result = cmd_generate(['-l', 'python', 'create a hello function'])
            assert "CodeMate Code Generation" in result
            assert "def hello():" in result


class TestRefactorCommand:
    """Test refactor command."""
    
    def test_refactor_no_args(self):
        """Test refactor command with no arguments."""
        result = cmd_refactor([])
        assert "Usage:" in result
    
    def test_refactor_no_file(self):
        """Test refactor command with no file specified."""
        result = cmd_refactor(['-t', 'performance'])
        assert "Error: No file specified" in result
    
    @patch('app.commands.codemate.CodeMateAPI.refactor_code')
    def test_refactor_success(self, mock_refactor):
        """Test successful refactoring."""
        mock_refactor.return_value = {
            'summary': 'Refactoring complete',
            'refactored_code': 'def optimized_function():\n    return "optimized"',
            'changes': ['Renamed function', 'Simplified logic'],
            'benefits': ['Better readability', 'Improved performance']
        }
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'def old_function():\n    return "old"')
            f.flush()
            
            try:
                with patch.dict(os.environ, {'CODEMATE_API_KEY': 'test-key'}):
                    result = cmd_refactor([f.name])
                    assert "CodeMate Refactoring Results" in result
                    assert "Refactoring complete" in result
            finally:
                os.unlink(f.name)


class TestCodeMateIntegration:
    """Integration tests for CodeMate commands."""
    
    def test_all_commands_return_strings(self):
        """Test that all CodeMate commands return strings."""
        commands = [cmd_compile, cmd_analyze, cmd_optimize, cmd_debug, cmd_generate, cmd_refactor]
        
        for cmd in commands:
            result = cmd([])  # Test with no args (should return usage)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_commands_handle_missing_api_key(self):
        """Test that commands handle missing API key gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(b'print("hello")')
                f.flush()
                
                try:
                    result = cmd_compile([f.name])
                    assert "Error:" in result
                    assert "API key" in result
                finally:
                    os.unlink(f.name)
    
    def test_commands_handle_invalid_args(self):
        """Test that commands handle invalid arguments gracefully."""
        result = cmd_compile(['-a', 'invalid_type'])
        assert isinstance(result, str)
        
        result = cmd_optimize(['-l', 'invalid_level'])
        assert isinstance(result, str)
        
        result = cmd_debug(['-l', 'invalid'])
        assert "Error:" in result
