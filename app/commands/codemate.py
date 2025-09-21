"""
CodeMate Integration Commands Module

Implements CodeMate compiler service integration:
- Code analysis and optimization
- AI-powered code generation
- Debugging assistance
- Code refactoring
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..config import (
    CODEMATE_API_BASE_URL, CODEMATE_TIMEOUT, CODEMATE_MAX_FILE_SIZE,
    CODEMATE_SUPPORTED_LANGUAGES, CODEMATE_DEFAULT_MODEL,
    get_error_message, get_success_message
)
from ..utils import (
    PyTermError, PathError, SecurityError, safe_join, path_in_jail,
    colorize, format_size, truncate_text, validate_filename
)


class CodeMateAPI:
    """CodeMate API client for compiler service integration."""
    
    def __init__(self):
        self.api_key = os.getenv('CODEMATE_API_KEY')
        self.base_url = CODEMATE_API_BASE_URL
        self.timeout = CODEMATE_TIMEOUT
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'PyTerm-CodeMate-Integration/1.0.0'
            })
    
    def _check_api_key(self):
        """Check if API key is configured."""
        if not self.api_key:
            raise PyTermError(get_error_message("codemate_no_api_key"))
    
    def _validate_file(self, file_path: Path) -> str:
        """Validate file for CodeMate analysis."""
        if not file_path.exists():
            raise PathError(get_error_message("file_not_found", path=str(file_path)))
        
        if not file_path.is_file():
            raise PathError(get_error_message("invalid_path", path=str(file_path)))
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > CODEMATE_MAX_FILE_SIZE:
            raise PyTermError(get_error_message("codemate_file_too_large", 
                                              max_size=format_size(CODEMATE_MAX_FILE_SIZE)))
        
        # Detect language from file extension
        extension = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }
        
        language = language_map.get(extension, 'python')
        if language not in CODEMATE_SUPPORTED_LANGUAGES:
            raise PyTermError(get_error_message("codemate_unsupported_language", language=language))
        
        return language
    
    def analyze_code(self, file_path: Path, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code using CodeMate compiler service."""
        self._check_api_key()
        language = self._validate_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "language": language,
                "code": content,
                "analysis_type": analysis_type,
                "model": CODEMATE_DEFAULT_MODEL,
                "options": {
                    "include_suggestions": True,
                    "include_complexity": True,
                    "include_security": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PyTermError(get_error_message("codemate_timeout"))
        except requests.exceptions.RequestException as e:
            raise PyTermError(get_error_message("codemate_api_error", error=str(e)))
        except Exception as e:
            raise PyTermError(f"Analysis failed: {e}")
    
    def optimize_code(self, file_path: Path, optimization_level: str = "balanced") -> Dict[str, Any]:
        """Optimize code using CodeMate compiler service."""
        self._check_api_key()
        language = self._validate_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "language": language,
                "code": content,
                "optimization_level": optimization_level,
                "model": CODEMATE_DEFAULT_MODEL,
                "options": {
                    "preserve_functionality": True,
                    "improve_performance": True,
                    "reduce_complexity": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/optimize",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PyTermError(get_error_message("codemate_timeout"))
        except requests.exceptions.RequestException as e:
            raise PyTermError(get_error_message("codemate_api_error", error=str(e)))
        except Exception as e:
            raise PyTermError(f"Optimization failed: {e}")
    
    def generate_code(self, prompt: str, language: str = "python", context: str = "") -> Dict[str, Any]:
        """Generate code using CodeMate compiler service."""
        self._check_api_key()
        
        if language not in CODEMATE_SUPPORTED_LANGUAGES:
            raise PyTermError(get_error_message("codemate_unsupported_language", language=language))
        
        try:
            payload = {
                "prompt": prompt,
                "language": language,
                "context": context,
                "model": CODEMATE_DEFAULT_MODEL,
                "options": {
                    "include_comments": True,
                    "include_tests": True,
                    "follow_best_practices": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PyTermError(get_error_message("codemate_timeout"))
        except requests.exceptions.RequestException as e:
            raise PyTermError(get_error_message("codemate_api_error", error=str(e)))
        except Exception as e:
            raise PyTermError(f"Code generation failed: {e}")
    
    def refactor_code(self, file_path: Path, refactor_type: str = "general") -> Dict[str, Any]:
        """Refactor code using CodeMate compiler service."""
        self._check_api_key()
        language = self._validate_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "language": language,
                "code": content,
                "refactor_type": refactor_type,
                "model": CODEMATE_DEFAULT_MODEL,
                "options": {
                    "preserve_behavior": True,
                    "improve_readability": True,
                    "modernize_syntax": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/refactor",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PyTermError(get_error_message("codemate_timeout"))
        except requests.exceptions.RequestException as e:
            raise PyTermError(get_error_message("codemate_api_error", error=str(e)))
        except Exception as e:
            raise PyTermError(f"Refactoring failed: {e}")
    
    def debug_code(self, file_path: Path, error_message: str = "") -> Dict[str, Any]:
        """Debug code using CodeMate compiler service."""
        self._check_api_key()
        language = self._validate_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "language": language,
                "code": content,
                "error_message": error_message,
                "model": CODEMATE_DEFAULT_MODEL,
                "options": {
                    "identify_bugs": True,
                    "suggest_fixes": True,
                    "explain_issues": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/debug",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PyTermError(get_error_message("codemate_timeout"))
        except requests.exceptions.RequestException as e:
            raise PyTermError(get_error_message("codemate_api_error", error=str(e)))
        except Exception as e:
            raise PyTermError(f"Debugging failed: {e}")


def cmd_compile(args: List[str]) -> str:
    """
    Compile and analyze code using CodeMate compiler service.
    
    Usage: compile [options] <file>
    Options:
        -a <type>    Analysis type: comprehensive, quick, security
        -o <file>    Output file for results
        -v           Verbose output
    """
    if not args:
        return "Usage: compile [options] <file>\nOptions: -a <type> (analysis type), -o <file> (output), -v (verbose)"
    
    analysis_type = "comprehensive"
    output_file = None
    verbose = False
    target_file = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-a' and i + 1 < len(args):
            analysis_type = args[i + 1]
            i += 2
        elif args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == '-v':
            verbose = True
            i += 1
        elif not args[i].startswith('-'):
            target_file = args[i]
            i += 1
        else:
            i += 1
    
    if not target_file:
        return "Error: No file specified for compilation."
    
    try:
        # Create file path
        file_path = safe_join(".", target_file)
        
        # Initialize CodeMate API
        api = CodeMateAPI()
        
        # Perform analysis
        result = api.analyze_code(file_path, analysis_type)
        
        # Format output
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Compilation Results', 'bold')}")
        output_lines.append(f"File: {colorize(target_file, 'cyan')}")
        output_lines.append(f"Analysis Type: {colorize(analysis_type, 'yellow')}")
        output_lines.append("")
        
        # Analysis summary
        if 'summary' in result:
            output_lines.append(f"{colorize('Summary:', 'yellow')}")
            output_lines.append(result['summary'])
            output_lines.append("")
        
        # Issues found
        if 'issues' in result and result['issues']:
            output_lines.append(f"{colorize('Issues Found:', 'red')}")
            for issue in result['issues']:
                severity = issue.get('severity', 'info')
                color = 'red' if severity == 'error' else 'yellow' if severity == 'warning' else 'blue'
                output_lines.append(f"  {colorize(severity.upper(), color)}: {issue.get('message', 'No message')}")
                if 'line' in issue:
                    output_lines.append(f"    Line {issue['line']}: {issue.get('code', '')}")
            output_lines.append("")
        
        # Suggestions
        if 'suggestions' in result and result['suggestions']:
            output_lines.append(f"{colorize('Suggestions:', 'green')}")
            for suggestion in result['suggestions']:
                output_lines.append(f"  • {suggestion}")
            output_lines.append("")
        
        # Complexity metrics
        if 'metrics' in result:
            metrics = result['metrics']
            output_lines.append(f"{colorize('Code Metrics:', 'blue')}")
            if 'complexity' in metrics:
                output_lines.append(f"  Complexity: {metrics['complexity']}")
            if 'lines_of_code' in metrics:
                output_lines.append(f"  Lines of Code: {metrics['lines_of_code']}")
            if 'functions' in metrics:
                output_lines.append(f"  Functions: {metrics['functions']}")
            output_lines.append("")
        
        # Save to output file if specified
        if output_file:
            try:
                output_path = safe_join(".", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                output_lines.append(f"{colorize('Results saved to:', 'green')} {output_file}")
            except Exception as e:
                output_lines.append(f"{colorize('Warning:', 'yellow')} Could not save to {output_file}: {e}")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")


def cmd_analyze(args: List[str]) -> str:
    """
    Analyze code for issues and improvements.
    
    Usage: analyze [options] <file>
    Options:
        -t <type>    Analysis type: security, performance, style
        -d           Detailed analysis
    """
    if not args:
        return "Usage: analyze [options] <file>\nOptions: -t <type> (analysis type), -d (detailed)"
    
    analysis_type = "comprehensive"
    detailed = False
    target_file = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-t' and i + 1 < len(args):
            analysis_type = args[i + 1]
            i += 2
        elif args[i] == '-d':
            detailed = True
            i += 1
        elif not args[i].startswith('-'):
            target_file = args[i]
            i += 1
        else:
            i += 1
    
    if not target_file:
        return "Error: No file specified for analysis."
    
    try:
        file_path = safe_join(".", target_file)
        api = CodeMateAPI()
        
        result = api.analyze_code(file_path, analysis_type)
        
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Analysis Results', 'bold')}")
        output_lines.append(f"File: {colorize(target_file, 'cyan')}")
        output_lines.append("")
        
        # Detailed analysis
        if detailed and 'detailed_analysis' in result:
            output_lines.append(f"{colorize('Detailed Analysis:', 'yellow')}")
            output_lines.append(result['detailed_analysis'])
            output_lines.append("")
        
        # Security analysis
        if 'security' in result:
            security = result['security']
            output_lines.append(f"{colorize('Security Analysis:', 'red')}")
            if 'vulnerabilities' in security:
                for vuln in security['vulnerabilities']:
                    output_lines.append(f"  ⚠️  {vuln}")
            if 'recommendations' in security:
                for rec in security['recommendations']:
                    output_lines.append(f"  💡 {rec}")
            output_lines.append("")
        
        # Performance analysis
        if 'performance' in result:
            perf = result['performance']
            output_lines.append(f"{colorize('Performance Analysis:', 'blue')}")
            if 'bottlenecks' in perf:
                for bottleneck in perf['bottlenecks']:
                    output_lines.append(f"  🐌 {bottleneck}")
            if 'optimizations' in perf:
                for opt in perf['optimizations']:
                    output_lines.append(f"  ⚡ {opt}")
            output_lines.append("")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")


def cmd_optimize(args: List[str]) -> str:
    """
    Optimize code for better performance and maintainability.
    
    Usage: optimize [options] <file>
    Options:
        -l <level>   Optimization level: conservative, balanced, aggressive
        -o <file>    Output optimized code to file
    """
    if not args:
        return "Usage: optimize [options] <file>\nOptions: -l <level> (optimization level), -o <file> (output)"
    
    optimization_level = "balanced"
    output_file = None
    target_file = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-l' and i + 1 < len(args):
            optimization_level = args[i + 1]
            i += 2
        elif args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif not args[i].startswith('-'):
            target_file = args[i]
            i += 1
        else:
            i += 1
    
    if not target_file:
        return "Error: No file specified for optimization."
    
    try:
        file_path = safe_join(".", target_file)
        api = CodeMateAPI()
        
        result = api.optimize_code(file_path, optimization_level)
        
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Optimization Results', 'bold')}")
        output_lines.append(f"File: {colorize(target_file, 'cyan')}")
        output_lines.append(f"Optimization Level: {colorize(optimization_level, 'yellow')}")
        output_lines.append("")
        
        # Optimization summary
        if 'summary' in result:
            output_lines.append(f"{colorize('Optimization Summary:', 'green')}")
            output_lines.append(result['summary'])
            output_lines.append("")
        
        # Optimized code
        if 'optimized_code' in result:
            optimized_code = result['optimized_code']
            output_lines.append(f"{colorize('Optimized Code:', 'blue')}")
            output_lines.append("```")
            output_lines.append(optimized_code)
            output_lines.append("```")
            output_lines.append("")
        
        # Improvements made
        if 'improvements' in result:
            output_lines.append(f"{colorize('Improvements Made:', 'green')}")
            for improvement in result['improvements']:
                output_lines.append(f"  ✓ {improvement}")
            output_lines.append("")
        
        # Performance gains
        if 'performance_gains' in result:
            gains = result['performance_gains']
            output_lines.append(f"{colorize('Performance Gains:', 'yellow')}")
            for gain in gains:
                output_lines.append(f"  📈 {gain}")
            output_lines.append("")
        
        # Save optimized code if requested
        if output_file:
            try:
                output_path = safe_join(".", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.get('optimized_code', ''))
                output_lines.append(f"{colorize('Optimized code saved to:', 'green')} {output_file}")
            except Exception as e:
                output_lines.append(f"{colorize('Warning:', 'yellow')} Could not save to {output_file}: {e}")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")


def cmd_debug(args: List[str]) -> str:
    """
    Debug code issues using CodeMate AI assistance.
    
    Usage: debug [options] <file>
    Options:
        -e <error>   Error message to debug
        -l <line>    Specific line to focus on
    """
    if not args:
        return "Usage: debug [options] <file>\nOptions: -e <error> (error message), -l <line> (line number)"
    
    error_message = ""
    focus_line = None
    target_file = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-e' and i + 1 < len(args):
            error_message = args[i + 1]
            i += 2
        elif args[i] == '-l' and i + 1 < len(args):
            try:
                focus_line = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid line number"
        elif not args[i].startswith('-'):
            target_file = args[i]
            i += 1
        else:
            i += 1
    
    if not target_file:
        return "Error: No file specified for debugging."
    
    try:
        file_path = safe_join(".", target_file)
        api = CodeMateAPI()
        
        result = api.debug_code(file_path, error_message)
        
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Debug Results', 'bold')}")
        output_lines.append(f"File: {colorize(target_file, 'cyan')}")
        if error_message:
            output_lines.append(f"Error: {colorize(error_message, 'red')}")
        if focus_line:
            output_lines.append(f"Focus Line: {colorize(str(focus_line), 'yellow')}")
        output_lines.append("")
        
        # Issues identified
        if 'issues' in result:
            output_lines.append(f"{colorize('Issues Identified:', 'red')}")
            for issue in result['issues']:
                output_lines.append(f"  🐛 {issue.get('description', 'No description')}")
                if 'line' in issue:
                    output_lines.append(f"    Line {issue['line']}: {issue.get('code', '')}")
                if 'severity' in issue:
                    severity_color = 'red' if issue['severity'] == 'error' else 'yellow'
                    output_lines.append(f"    Severity: {colorize(issue['severity'].upper(), severity_color)}")
            output_lines.append("")
        
        # Suggested fixes
        if 'fixes' in result:
            output_lines.append(f"{colorize('Suggested Fixes:', 'green')}")
            for fix in result['fixes']:
                output_lines.append(f"  🔧 {fix.get('description', 'No description')}")
                if 'code' in fix:
                    output_lines.append(f"    ```")
                    output_lines.append(f"    {fix['code']}")
                    output_lines.append(f"    ```")
            output_lines.append("")
        
        # Root cause analysis
        if 'root_cause' in result:
            output_lines.append(f"{colorize('Root Cause Analysis:', 'blue')}")
            output_lines.append(result['root_cause'])
            output_lines.append("")
        
        # Prevention tips
        if 'prevention_tips' in result:
            output_lines.append(f"{colorize('Prevention Tips:', 'yellow')}")
            for tip in result['prevention_tips']:
                output_lines.append(f"  💡 {tip}")
            output_lines.append("")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")


def cmd_generate(args: List[str]) -> str:
    """
    Generate code using CodeMate AI.
    
    Usage: generate [options] <prompt>
    Options:
        -l <lang>    Programming language (default: python)
        -o <file>    Output file for generated code
        -c <context> Additional context
    """
    if not args:
        return "Usage: generate [options] <prompt>\nOptions: -l <lang> (language), -o <file> (output), -c <context>"
    
    language = "python"
    output_file = None
    context = ""
    prompt_parts = []
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-l' and i + 1 < len(args):
            language = args[i + 1]
            i += 2
        elif args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == '-c' and i + 1 < len(args):
            context = args[i + 1]
            i += 2
        elif not args[i].startswith('-'):
            prompt_parts.append(args[i])
            i += 1
        else:
            i += 1
    
    if not prompt_parts:
        return "Error: No prompt specified for code generation."
    
    prompt = ' '.join(prompt_parts)
    
    try:
        api = CodeMateAPI()
        
        result = api.generate_code(prompt, language, context)
        
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Code Generation', 'bold')}")
        output_lines.append(f"Language: {colorize(language, 'cyan')}")
        output_lines.append(f"Prompt: {colorize(prompt, 'yellow')}")
        if context:
            output_lines.append(f"Context: {colorize(context, 'blue')}")
        output_lines.append("")
        
        # Generated code
        if 'generated_code' in result:
            output_lines.append(f"{colorize('Generated Code:', 'green')}")
            output_lines.append("```" + language)
            output_lines.append(result['generated_code'])
            output_lines.append("```")
            output_lines.append("")
        
        # Explanation
        if 'explanation' in result:
            output_lines.append(f"{colorize('Explanation:', 'blue')}")
            output_lines.append(result['explanation'])
            output_lines.append("")
        
        # Usage examples
        if 'usage_examples' in result:
            output_lines.append(f"{colorize('Usage Examples:', 'yellow')}")
            for example in result['usage_examples']:
                output_lines.append(f"  {example}")
            output_lines.append("")
        
        # Save generated code if requested
        if output_file:
            try:
                output_path = safe_join(".", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.get('generated_code', ''))
                output_lines.append(f"{colorize('Generated code saved to:', 'green')} {output_file}")
            except Exception as e:
                output_lines.append(f"{colorize('Warning:', 'yellow')} Could not save to {output_file}: {e}")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")


def cmd_refactor(args: List[str]) -> str:
    """
    Refactor code using CodeMate AI assistance.
    
    Usage: refactor [options] <file>
    Options:
        -t <type>    Refactor type: general, performance, readability
        -o <file>    Output refactored code to file
    """
    if not args:
        return "Usage: refactor [options] <file>\nOptions: -t <type> (refactor type), -o <file> (output)"
    
    refactor_type = "general"
    output_file = None
    target_file = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-t' and i + 1 < len(args):
            refactor_type = args[i + 1]
            i += 2
        elif args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif not args[i].startswith('-'):
            target_file = args[i]
            i += 1
        else:
            i += 1
    
    if not target_file:
        return "Error: No file specified for refactoring."
    
    try:
        file_path = safe_join(".", target_file)
        api = CodeMateAPI()
        
        result = api.refactor_code(file_path, refactor_type)
        
        output_lines = []
        output_lines.append(f"{colorize('CodeMate Refactoring Results', 'bold')}")
        output_lines.append(f"File: {colorize(target_file, 'cyan')}")
        output_lines.append(f"Refactor Type: {colorize(refactor_type, 'yellow')}")
        output_lines.append("")
        
        # Refactoring summary
        if 'summary' in result:
            output_lines.append(f"{colorize('Refactoring Summary:', 'green')}")
            output_lines.append(result['summary'])
            output_lines.append("")
        
        # Refactored code
        if 'refactored_code' in result:
            output_lines.append(f"{colorize('Refactored Code:', 'blue')}")
            output_lines.append("```")
            output_lines.append(result['refactored_code'])
            output_lines.append("```")
            output_lines.append("")
        
        # Changes made
        if 'changes' in result:
            output_lines.append(f"{colorize('Changes Made:', 'yellow')}")
            for change in result['changes']:
                output_lines.append(f"  🔄 {change}")
            output_lines.append("")
        
        # Benefits
        if 'benefits' in result:
            output_lines.append(f"{colorize('Benefits:', 'green')}")
            for benefit in result['benefits']:
                output_lines.append(f"  ✓ {benefit}")
            output_lines.append("")
        
        # Save refactored code if requested
        if output_file:
            try:
                output_path = safe_join(".", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.get('refactored_code', ''))
                output_lines.append(f"{colorize('Refactored code saved to:', 'green')} {output_file}")
            except Exception as e:
                output_lines.append(f"{colorize('Warning:', 'yellow')} Could not save to {output_file}: {e}")
        
        return '\n'.join(output_lines)
        
    except PyTermError as e:
        return colorize(f"Error: {e.message}", "red")
    except Exception as e:
        return colorize(f"Unexpected error: {e}", "red")
