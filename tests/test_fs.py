"""
Tests for File System Commands

Tests ls, cd, pwd, mkdir, rm command implementations.
"""

import pytest
import tempfile
import os
from pathlib import Path
from app.commands.fs import (
    cmd_mkdir, cmd_rm, cmd_touch, cmd_cat, cmd_cp, cmd_mv,
    cmd_find, cmd_wc, cmd_head, cmd_tail
)


class TestMkdir:
    """Test mkdir command."""
    
    def test_mkdir_basic(self):
        """Test basic directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_mkdir(["testdir"])
            assert "created successfully" in result
            assert Path("testdir").exists()
            assert Path("testdir").is_dir()
    
    def test_mkdir_with_parents(self):
        """Test directory creation with parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_mkdir(["-p", "parent/child/grandchild"])
            assert "created successfully" in result
            assert Path("parent/child/grandchild").exists()
    
    def test_mkdir_multiple(self):
        """Test creating multiple directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_mkdir(["dir1", "dir2", "dir3"])
            assert Path("dir1").exists()
            assert Path("dir2").exists()
            assert Path("dir3").exists()
    
    def test_mkdir_existing(self):
        """Test creating existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("existing").mkdir()
            result = cmd_mkdir(["existing"])
            assert "already exists" in result
    
    def test_mkdir_no_args(self):
        """Test mkdir with no arguments."""
        result = cmd_mkdir([])
        assert "Usage:" in result


class TestTouch:
    """Test touch command."""
    
    def test_touch_basic(self):
        """Test basic file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_touch(["testfile.txt"])
            assert "Created" in result or "Touched" in result
            assert Path("testfile.txt").exists()
            assert Path("testfile.txt").is_file()
    
    def test_touch_multiple(self):
        """Test creating multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_touch(["file1.txt", "file2.txt", "file3.txt"])
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            assert Path("file3.txt").exists()
    
    def test_touch_existing(self):
        """Test touching existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("existing.txt").touch()
            result = cmd_touch(["existing.txt"])
            assert "Touched" in result
    
    def test_touch_no_args(self):
        """Test touch with no arguments."""
        result = cmd_touch([])
        assert "Usage:" in result


class TestRm:
    """Test rm command."""
    
    def test_rm_file(self):
        """Test removing a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("testfile.txt").touch()
            result = cmd_rm(["testfile.txt"])
            assert "deleted successfully" in result
            assert not Path("testfile.txt").exists()
    
    def test_rm_directory_without_recursive(self):
        """Test removing directory without -r flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("testdir").mkdir()
            result = cmd_rm(["testdir"])
            assert "use -r for recursive removal" in result
            assert Path("testdir").exists()
    
    def test_rm_directory_recursive(self):
        """Test removing directory with -r flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("testdir").mkdir()
            result = cmd_rm(["-r", "testdir"])
            assert "deleted successfully" in result
            assert not Path("testdir").exists()
    
    def test_rm_nonexistent(self):
        """Test removing nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_rm(["nonexistent.txt"])
            assert "not found" in result
    
    def test_rm_no_args(self):
        """Test rm with no arguments."""
        result = cmd_rm([])
        assert "Usage:" in result


class TestCat:
    """Test cat command."""
    
    def test_cat_basic(self):
        """Test basic file reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("line1\nline2\nline3")
            
            result = cmd_cat(["testfile.txt"])
            assert "line1" in result
            assert "line2" in result
            assert "line3" in result
    
    def test_cat_with_line_numbers(self):
        """Test cat with line numbers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("line1\nline2")
            
            result = cmd_cat(["-n", "testfile.txt"])
            assert "1:" in result
            assert "2:" in result
    
    def test_cat_multiple_files(self):
        """Test cat with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("file1.txt", "w") as f:
                f.write("content1")
            with open("file2.txt", "w") as f:
                f.write("content2")
            
            result = cmd_cat(["file1.txt", "file2.txt"])
            assert "content1" in result
            assert "content2" in result
    
    def test_cat_nonexistent(self):
        """Test cat with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_cat(["nonexistent.txt"])
            assert "not found" in result
    
    def test_cat_empty_file(self):
        """Test cat with empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("empty.txt").touch()
            result = cmd_cat(["empty.txt"])
            assert "empty" in result


class TestCp:
    """Test cp command."""
    
    def test_cp_file(self):
        """Test copying a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("source.txt", "w") as f:
                f.write("test content")
            
            result = cmd_cp(["source.txt", "dest.txt"])
            assert "Copied" in result
            assert Path("dest.txt").exists()
            assert Path("dest.txt").read_text() == "test content"
    
    def test_cp_directory_without_recursive(self):
        """Test copying directory without -r flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("sourcedir").mkdir()
            result = cmd_cp(["sourcedir", "destdir"])
            assert "use -r for recursive copy" in result
    
    def test_cp_directory_recursive(self):
        """Test copying directory with -r flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("sourcedir").mkdir()
            with open("sourcedir/file.txt", "w") as f:
                f.write("content")
            
            result = cmd_cp(["-r", "sourcedir", "destdir"])
            assert "Copied" in result
            assert Path("destdir").exists()
            assert Path("destdir/file.txt").exists()


class TestMv:
    """Test mv command."""
    
    def test_mv_file(self):
        """Test moving a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("source.txt", "w") as f:
                f.write("test content")
            
            result = cmd_mv(["source.txt", "dest.txt"])
            assert "Moved" in result
            assert not Path("source.txt").exists()
            assert Path("dest.txt").exists()
            assert Path("dest.txt").read_text() == "test content"
    
    def test_mv_nonexistent(self):
        """Test moving nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_mv(["nonexistent.txt", "dest.txt"])
            assert "not found" in result


class TestFind:
    """Test find command."""
    
    def test_find_basic(self):
        """Test basic file finding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("testfile.txt").touch()
            Path("otherfile.log").touch()
            
            result = cmd_find(["-name", "testfile.txt"])
            assert "testfile.txt" in result
    
    def test_find_pattern(self):
        """Test finding files with pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            Path("test1.txt").touch()
            Path("test2.txt").touch()
            Path("other.log").touch()
            
            result = cmd_find(["-name", "test"])
            assert "test1.txt" in result
            assert "test2.txt" in result
            assert "other.log" not in result
    
    def test_find_nonexistent(self):
        """Test finding in nonexistent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = cmd_find(["nonexistent", "-name", "test"])
            assert "not found" in result


class TestWc:
    """Test wc command."""
    
    def test_wc_basic(self):
        """Test basic word count."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("line1\nline2\nline3")
            
            result = cmd_wc(["testfile.txt"])
            assert "3" in result  # lines
            assert "3" in result  # words
            assert "testfile.txt" in result
    
    def test_wc_lines_only(self):
        """Test word count with lines only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("line1\nline2")
            
            result = cmd_wc(["-l", "testfile.txt"])
            assert "2" in result  # lines
    
    def test_wc_words_only(self):
        """Test word count with words only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("word1 word2 word3")
            
            result = cmd_wc(["-w", "testfile.txt"])
            assert "3" in result  # words
    
    def test_wc_characters_only(self):
        """Test word count with characters only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                f.write("abc")
            
            result = cmd_wc(["-c", "testfile.txt"])
            assert "3" in result  # characters


class TestHead:
    """Test head command."""
    
    def test_head_basic(self):
        """Test basic head command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                for i in range(20):
                    f.write(f"line{i}\n")
            
            result = cmd_head(["testfile.txt"])
            assert "line0" in result
            assert "line9" in result
            assert "line19" not in result  # Default 10 lines
    
    def test_head_custom_lines(self):
        """Test head with custom number of lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                for i in range(20):
                    f.write(f"line{i}\n")
            
            result = cmd_head(["-n", "5", "testfile.txt"])
            assert "line0" in result
            assert "line4" in result
            assert "line5" not in result


class TestTail:
    """Test tail command."""
    
    def test_tail_basic(self):
        """Test basic tail command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                for i in range(20):
                    f.write(f"line{i}\n")
            
            result = cmd_tail(["testfile.txt"])
            assert "line10" in result
            assert "line19" in result
            assert "line0" not in result  # Default 10 lines
    
    def test_tail_custom_lines(self):
        """Test tail with custom number of lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            with open("testfile.txt", "w") as f:
                for i in range(20):
                    f.write(f"line{i}\n")
            
            result = cmd_tail(["-n", "5", "testfile.txt"])
            assert "line15" in result
            assert "line19" in result
            assert "line14" not in result
