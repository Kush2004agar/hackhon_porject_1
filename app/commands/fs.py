"""
File System Commands Module

Implements file system operations: ls, cd, pwd, mkdir, rm, cat, touch
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from ..config import get_error_message, get_success_message
from ..utils import (
    PyTermError, PathError, SecurityError, safe_join, path_in_jail,
    colorize, format_size, format_path, validate_filename, 
    get_file_info, format_list, format_table, truncate_text
)


def cmd_mkdir(args: List[str]) -> str:
    """
    Create directories.
    
    Usage: mkdir [options] <directory>...
    Options:
        -p    Create parent directories as needed
    """
    if not args:
        return "Usage: mkdir [options] <directory>...\nUse -p to create parent directories."
    
    create_parents = False
    directories = []
    
    # Parse arguments
    for arg in args:
        if arg == '-p':
            create_parents = True
        elif not arg.startswith('-'):
            directories.append(arg)
    
    if not directories:
        return "Error: No directories specified."
    
    results = []
    for directory in directories:
        try:
            # Validate filename
            if not validate_filename(directory):
                results.append(get_error_message("invalid_path", path=directory))
                continue
            
            # Create directory path
            dir_path = safe_join(".", directory)
            
            # Create directory
            dir_path.mkdir(parents=create_parents, exist_ok=False)
            results.append(get_success_message("directory_created", path=str(dir_path)))
            
        except FileExistsError:
            results.append(f"Directory '{directory}' already exists.")
        except (OSError, PermissionError) as e:
            results.append(get_error_message("permission_denied", path=directory))
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error creating directory '{directory}': {e}")
    
    return "\n".join(results)


def cmd_rm(args: List[str]) -> str:
    """
    Remove files and directories.
    
    Usage: rm [options] <file>...
    Options:
        -r    Remove directories recursively
        -f    Force removal (no confirmation)
    """
    if not args:
        return "Usage: rm [options] <file>...\nUse -r for directories, -f to force."
    
    recursive = False
    force = False
    targets = []
    
    # Parse arguments
    for arg in args:
        if arg == '-r':
            recursive = True
        elif arg == '-f':
            force = True
        elif not arg.startswith('-'):
            targets.append(arg)
    
    if not targets:
        return "Error: No files or directories specified."
    
    results = []
    for target in targets:
        try:
            # Create target path
            target_path = safe_join(".", target)
            
            if not target_path.exists():
                results.append(get_error_message("file_not_found", path=str(target_path)))
                continue
            
            # Check if it's a directory
            if target_path.is_dir():
                if not recursive:
                    results.append(f"Cannot remove directory '{target}': use -r for recursive removal")
                    continue
                
                # Remove directory
                shutil.rmtree(target_path)
                results.append(get_success_message("directory_deleted", path=str(target_path)))
            else:
                # Remove file
                target_path.unlink()
                results.append(get_success_message("file_deleted", path=str(target_path)))
                
        except (OSError, PermissionError) as e:
            results.append(get_error_message("permission_denied", path=target))
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error removing '{target}': {e}")
    
    return "\n".join(results)


def cmd_touch(args: List[str]) -> str:
    """
    Create empty files or update timestamps.
    
    Usage: touch <file>...
    """
    if not args:
        return "Usage: touch <file>..."
    
    results = []
    for filename in args:
        try:
            # Validate filename
            if not validate_filename(filename):
                results.append(get_error_message("invalid_path", path=filename))
                continue
            
            # Create file path
            file_path = safe_join(".", filename)
            
            # Create file or update timestamp
            file_path.touch(exist_ok=True)
            
            if file_path.exists():
                results.append(f"Touched '{filename}'")
            else:
                results.append(f"Created '{filename}'")
                
        except (OSError, PermissionError) as e:
            results.append(get_error_message("permission_denied", path=filename))
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error touching '{filename}': {e}")
    
    return "\n".join(results)


def cmd_cat(args: List[str]) -> str:
    """
    Display file contents.
    
    Usage: cat <file>...
    Options:
        -n    Number the output lines
    """
    if not args:
        return "Usage: cat [options] <file>...\nUse -n to number lines."
    
    number_lines = False
    files = []
    
    # Parse arguments
    for arg in args:
        if arg == '-n':
            number_lines = True
        elif not arg.startswith('-'):
            files.append(arg)
    
    if not files:
        return "Error: No files specified."
    
    results = []
    for filename in files:
        try:
            # Create file path
            file_path = safe_join(".", filename)
            
            if not file_path.exists():
                results.append(get_error_message("file_not_found", path=str(file_path)))
                continue
            
            if not file_path.is_file():
                results.append(get_error_message("invalid_path", path=str(file_path)))
                continue
            
            # Read file contents
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if not lines:
                    results.append(f"'{filename}' is empty")
                    continue
                
                # Format output
                if number_lines:
                    for i, line in enumerate(lines, 1):
                        results.append(f"{i:6d}: {line.rstrip()}")
                else:
                    for line in lines:
                        results.append(line.rstrip())
                
                # Add separator between files
                if len(files) > 1:
                    results.append("")
                    
            except UnicodeDecodeError:
                results.append(f"Cannot read '{filename}': file contains binary data")
            except PermissionError:
                results.append(get_error_message("permission_denied", path=filename))
                
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error reading '{filename}': {e}")
    
    return "\n".join(results)


def cmd_cp(args: List[str]) -> str:
    """
    Copy files and directories.
    
    Usage: cp [options] <source> <destination>
    Options:
        -r    Copy directories recursively
    """
    if len(args) < 2:
        return "Usage: cp [options] <source> <destination>\nUse -r for directories."
    
    recursive = False
    sources = []
    destination = None
    
    # Parse arguments
    for arg in args:
        if arg == '-r':
            recursive = True
        elif not arg.startswith('-'):
            if destination is None:
                sources.append(arg)
            else:
                destination = arg
                break
    
    if not sources or not destination:
        return "Error: Source and destination must be specified."
    
    if len(sources) > 1 and not Path(destination).is_dir():
        return "Error: Multiple sources require destination to be a directory."
    
    results = []
    for source in sources:
        try:
            # Create paths
            source_path = safe_join(".", source)
            dest_path = safe_join(".", destination)
            
            if not source_path.exists():
                results.append(get_error_message("file_not_found", path=str(source_path)))
                continue
            
            # Handle multiple sources
            if len(sources) > 1:
                dest_path = dest_path / source_path.name
            
            # Copy file or directory
            if source_path.is_dir():
                if not recursive:
                    results.append(f"Cannot copy directory '{source}': use -r for recursive copy")
                    continue
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, dest_path)
            
            results.append(f"Copied '{source}' to '{dest_path}'")
            
        except (OSError, PermissionError) as e:
            results.append(get_error_message("permission_denied", path=source))
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error copying '{source}': {e}")
    
    return "\n".join(results)


def cmd_mv(args: List[str]) -> str:
    """
    Move or rename files and directories.
    
    Usage: mv <source> <destination>
    """
    if len(args) < 2:
        return "Usage: mv <source> <destination>"
    
    source = args[0]
    destination = args[1]
    
    try:
        # Create paths
        source_path = safe_join(".", source)
        dest_path = safe_join(".", destination)
        
        if not source_path.exists():
            return get_error_message("file_not_found", path=str(source_path))
        
        # Move file or directory
        shutil.move(str(source_path), str(dest_path))
        return f"Moved '{source}' to '{destination}'"
        
    except (OSError, PermissionError) as e:
        return get_error_message("permission_denied", path=source)
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error moving '{source}': {e}"


def cmd_find(args: List[str]) -> str:
    """
    Find files and directories.
    
    Usage: find [path] -name <pattern>
    """
    if len(args) < 2 or args[0] != '-name':
        return "Usage: find [path] -name <pattern>"
    
    search_path = "."
    pattern = args[1]
    
    if len(args) > 2:
        search_path = args[0]
        pattern = args[2]
    
    try:
        # Create search path
        search_path = safe_join(".", search_path)
        
        if not search_path.exists() or not search_path.is_dir():
            return get_error_message("file_not_found", path=str(search_path))
        
        # Find files matching pattern
        matches = []
        for root, dirs, files in os.walk(search_path):
            root_path = Path(root)
            
            # Check directories
            for dir_name in dirs:
                if pattern in dir_name:
                    matches.append(str(root_path / dir_name))
            
            # Check files
            for file_name in files:
                if pattern in file_name:
                    matches.append(str(root_path / file_name))
        
        if not matches:
            return f"No files or directories found matching '{pattern}'"
        
        return "\n".join(sorted(matches))
        
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error searching: {e}"


def cmd_wc(args: List[str]) -> str:
    """
    Count lines, words, and characters in files.
    
    Usage: wc [options] <file>...
    Options:
        -l    Count lines only
        -w    Count words only
        -c    Count characters only
    """
    if not args:
        return "Usage: wc [options] <file>...\nOptions: -l (lines), -w (words), -c (characters)"
    
    count_lines = False
    count_words = False
    count_chars = False
    files = []
    
    # Parse arguments
    for arg in args:
        if arg == '-l':
            count_lines = True
        elif arg == '-w':
            count_words = True
        elif arg == '-c':
            count_chars = True
        elif not arg.startswith('-'):
            files.append(arg)
    
    # If no specific count requested, count all
    if not any([count_lines, count_words, count_chars]):
        count_lines = count_words = count_chars = True
    
    if not files:
        return "Error: No files specified."
    
    results = []
    total_lines = total_words = total_chars = 0
    
    for filename in files:
        try:
            # Create file path
            file_path = safe_join(".", filename)
            
            if not file_path.exists():
                results.append(f"wc: '{filename}': No such file")
                continue
            
            if not file_path.is_file():
                results.append(f"wc: '{filename}': Is a directory")
                continue
            
            # Read file contents
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.count('\n')
                words = len(content.split())
                chars = len(content)
                
                # Format output
                output_parts = []
                if count_lines:
                    output_parts.append(f"{lines:8d}")
                if count_words:
                    output_parts.append(f"{words:8d}")
                if count_chars:
                    output_parts.append(f"{chars:8d}")
                
                output_parts.append(filename)
                results.append(" ".join(output_parts))
                
                total_lines += lines
                total_words += words
                total_chars += chars
                
            except UnicodeDecodeError:
                results.append(f"wc: '{filename}': Cannot read binary file")
                
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error reading '{filename}': {e}")
    
    # Add total line if multiple files
    if len(files) > 1:
        output_parts = []
        if count_lines:
            output_parts.append(f"{total_lines:8d}")
        if count_words:
            output_parts.append(f"{total_words:8d}")
        if count_chars:
            output_parts.append(f"{total_chars:8d}")
        output_parts.append("total")
        results.append(" ".join(output_parts))
    
    return "\n".join(results)


def cmd_head(args: List[str]) -> str:
    """
    Display the first lines of files.
    
    Usage: head [options] <file>...
    Options:
        -n <num>    Number of lines to display (default: 10)
    """
    if not args:
        return "Usage: head [options] <file>...\nUse -n <num> to specify number of lines."
    
    num_lines = 10
    files = []
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-n' and i + 1 < len(args):
            try:
                num_lines = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid number of lines"
        elif not args[i].startswith('-'):
            files.append(args[i])
            i += 1
        else:
            i += 1
    
    if not files:
        return "Error: No files specified."
    
    results = []
    for filename in files:
        try:
            # Create file path
            file_path = safe_join(".", filename)
            
            if not file_path.exists():
                results.append(f"head: '{filename}': No such file")
                continue
            
            if not file_path.is_file():
                results.append(f"head: '{filename}': Is a directory")
                continue
            
            # Read file contents
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Display first num_lines
                display_lines = lines[:num_lines]
                for line in display_lines:
                    results.append(line.rstrip())
                
                # Add separator between files
                if len(files) > 1:
                    results.append("")
                    
            except UnicodeDecodeError:
                results.append(f"head: '{filename}': Cannot read binary file")
                
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error reading '{filename}': {e}")
    
    return "\n".join(results)


def cmd_tail(args: List[str]) -> str:
    """
    Display the last lines of files.
    
    Usage: tail [options] <file>...
    Options:
        -n <num>    Number of lines to display (default: 10)
    """
    if not args:
        return "Usage: tail [options] <file>...\nUse -n <num> to specify number of lines."
    
    num_lines = 10
    files = []
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-n' and i + 1 < len(args):
            try:
                num_lines = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid number of lines"
        elif not args[i].startswith('-'):
            files.append(args[i])
            i += 1
        else:
            i += 1
    
    if not files:
        return "Error: No files specified."
    
    results = []
    for filename in files:
        try:
            # Create file path
            file_path = safe_join(".", filename)
            
            if not file_path.exists():
                results.append(f"tail: '{filename}': No such file")
                continue
            
            if not file_path.is_file():
                results.append(f"tail: '{filename}': Is a directory")
                continue
            
            # Read file contents
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Display last num_lines
                display_lines = lines[-num_lines:] if len(lines) > num_lines else lines
                for line in display_lines:
                    results.append(line.rstrip())
                
                # Add separator between files
                if len(files) > 1:
                    results.append("")
                    
            except UnicodeDecodeError:
                results.append(f"tail: '{filename}': Cannot read binary file")
                
        except SecurityError as e:
            results.append(f"Security error: {e}")
        except Exception as e:
            results.append(f"Error reading '{filename}': {e}")
    
    return "\n".join(results)
