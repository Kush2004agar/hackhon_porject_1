"""
Tests for Utility Functions

Tests path jail, formatting, error handling, and other utility functions.
"""

import pytest
import tempfile
import os
from pathlib import Path
from app.utils import (
    PyTermError, PathError, SecurityError,
    safe_join, path_in_jail, format_path, format_size,
    format_percentage, colorize, format_list, format_table,
    truncate_text, validate_filename, get_relative_path,
    ensure_directory, is_executable, get_file_info
)


class TestExceptions:
    """Test custom exception classes."""
    
    def test_pyterm_error(self):
        """Test PyTermError creation."""
        error = PyTermError("Test error", "test_code")
        assert error.message == "Test error"
        assert error.error_code == "test_code"
        assert str(error) == "Test error"
    
    def test_path_error(self):
        """Test PathError inheritance."""
        error = PathError("Path error")
        assert isinstance(error, PyTermError)
        assert error.message == "Path error"
    
    def test_security_error(self):
        """Test SecurityError inheritance."""
        error = SecurityError("Security error")
        assert isinstance(error, PyTermError)
        assert error.message == "Security error"


class TestPathSecurity:
    """Test path security functions."""
    
    def test_safe_join_basic(self):
        """Test basic safe path joining."""
        result = safe_join("/safe/base", "subdir", "file.txt")
        assert str(result).endswith("subdir/file.txt")
    
    def test_safe_join_traversal_attack(self):
        """Test that directory traversal attacks are blocked."""
        with pytest.raises(SecurityError):
            safe_join("/safe/base", "../../etc/passwd")
    
    def test_safe_join_absolute_path(self):
        """Test that absolute paths are blocked."""
        with pytest.raises(SecurityError):
            safe_join("/safe/base", "/absolute/path")
    
    def test_path_in_jail_valid(self):
        """Test path in jail with valid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "subdir" / "file.txt"
            test_path.parent.mkdir(parents=True)
            test_path.touch()
            
            # Mock ROOT_DIR for testing
            import app.utils
            original_root = app.utils.ROOT_DIR
            app.utils.ROOT_DIR = Path(temp_dir)
            
            try:
                assert path_in_jail(str(test_path)) == True
            finally:
                app.utils.ROOT_DIR = original_root
    
    def test_path_in_jail_invalid(self):
        """Test path in jail with invalid path."""
        assert path_in_jail("/etc/passwd") == False


class TestFormatting:
    """Test formatting functions."""
    
    def test_format_path_short(self):
        """Test formatting short paths."""
        result = format_path("/short/path", 50)
        assert result == "/short/path"
    
    def test_format_path_long(self):
        """Test formatting long paths with truncation."""
        long_path = "/very/long/path/that/exceeds/the/maximum/length/limit"
        result = format_path(long_path, 20)
        assert len(result) <= 20
        assert "..." in result
    
    def test_format_size_bytes(self):
        """Test size formatting for bytes."""
        assert format_size(0) == "0 B"
        assert format_size(1023) == "1023 B"
    
    def test_format_size_kb(self):
        """Test size formatting for kilobytes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"
    
    def test_format_size_mb(self):
        """Test size formatting for megabytes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 1.5) == "1.5 MB"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0, 100) == "0.0%"
        assert format_percentage(50, 100) == "50.0%"
        assert format_percentage(25, 0) == "0.0%"
    
    def test_colorize(self):
        """Test text colorization."""
        result = colorize("test", "red")
        assert "test" in result
        assert "\033[31m" in result  # Red ANSI code
        assert "\033[0m" in result   # Reset ANSI code
    
    def test_format_list_empty(self):
        """Test formatting empty list."""
        assert format_list([]) == ""
    
    def test_format_list_single(self):
        """Test formatting single item list."""
        assert format_list(["item"]) == "item"
    
    def test_format_list_multiple(self):
        """Test formatting multiple items."""
        items = ["item1", "item2", "item3"]
        result = format_list(items, columns=2)
        assert "item1" in result
        assert "item2" in result
        assert "item3" in result
    
    def test_format_table_empty(self):
        """Test formatting empty table."""
        assert format_table([]) == ""
    
    def test_format_table_with_headers(self):
        """Test formatting table with headers."""
        data = [["row1col1", "row1col2"], ["row2col1", "row2col2"]]
        headers = ["Header1", "Header2"]
        result = format_table(data, headers)
        assert "Header1" in result
        assert "Header2" in result
        assert "row1col1" in result
    
    def test_truncate_text_short(self):
        """Test truncating short text."""
        assert truncate_text("short", 10) == "short"
    
    def test_truncate_text_long(self):
        """Test truncating long text."""
        long_text = "This is a very long text that should be truncated"
        result = truncate_text(long_text, 20)
        assert len(result) <= 20
        assert result.endswith("...")


class TestValidation:
    """Test validation functions."""
    
    def test_validate_filename_valid(self):
        """Test validating valid filenames."""
        assert validate_filename("test.txt") == True
        assert validate_filename("my_file") == True
        assert validate_filename("file-123") == True
    
    def test_validate_filename_invalid_chars(self):
        """Test validating filenames with invalid characters."""
        assert validate_filename("test<file") == False
        assert validate_filename("test>file") == False
        assert validate_filename("test:file") == False
        assert validate_filename("test/file") == False
        assert validate_filename("test\\file") == False
        assert validate_filename("test|file") == False
        assert validate_filename("test?file") == False
        assert validate_filename("test*file") == False
    
    def test_validate_filename_reserved(self):
        """Test validating reserved filenames."""
        assert validate_filename("CON") == False
        assert validate_filename("PRN") == False
        assert validate_filename("AUX") == False
        assert validate_filename("NUL") == False
        assert validate_filename("COM1") == False
        assert validate_filename("LPT1") == False
    
    def test_validate_filename_empty(self):
        """Test validating empty filenames."""
        assert validate_filename("") == False
        assert validate_filename("   ") == False


class TestFileOperations:
    """Test file operation utilities."""
    
    def test_get_relative_path(self):
        """Test getting relative path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            target = base / "subdir" / "file.txt"
            target.parent.mkdir(parents=True)
            target.touch()
            
            result = get_relative_path(str(target), str(base))
            assert result == "subdir/file.txt"
    
    def test_ensure_directory(self):
        """Test ensuring directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new" / "nested" / "directory"
            ensure_directory(str(new_dir))
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_is_executable(self):
        """Test checking if file is executable."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("#!/bin/bash\necho 'test'")
            f.flush()
            os.chmod(f.name, 0o755)
            
            try:
                assert is_executable(f.name) == True
            finally:
                os.unlink(f.name)
    
    def test_get_file_info(self):
        """Test getting file information."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            
            try:
                info = get_file_info(f.name)
                assert info["name"] == Path(f.name).name
                assert info["size"] > 0
                assert info["is_file"] == True
                assert info["is_dir"] == False
                assert "size_formatted" in info
                assert "permissions" in info
            finally:
                os.unlink(f.name)


class TestErrorHandling:
    """Test error handling in utility functions."""
    
    def test_safe_join_error_handling(self):
        """Test error handling in safe_join."""
        with pytest.raises(PathError):
            safe_join("", "invalid/path/with/../traversal")
    
    def test_get_file_info_nonexistent(self):
        """Test get_file_info with nonexistent file."""
        info = get_file_info("/nonexistent/file")
        assert info["name"] == "/nonexistent/file"
        assert info["size"] == 0
        assert info["is_file"] == False
        assert info["is_dir"] == False
