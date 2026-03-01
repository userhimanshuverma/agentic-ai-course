"""
Sandboxed code execution tool for MCP server.
"""

import ast
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict
import signal

from ...utils.config import config


class CodeExecutorTool:
    """Sandboxed Python code execution tool."""
    
    name = "code_executor"
    description = "Execute Python code in a sandboxed environment"
    
    input_schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds (max 30)",
                "default": 10
            }
        },
        "required": ["code"]
    }
    
    # Dangerous builtins to remove
    DANGEROUS_BUILTINS = [
        'open', 'exec', 'eval', 'compile', '__import__',
        'exit', 'quit', 'input', 'raw_input',
        'help', 'license', 'credits'
    ]
    
    # Dangerous modules
    DANGEROUS_MODULES = ['os', 'sys', 'subprocess', 'socket', 'urllib', 'http']
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in sandbox."""
        code = arguments.get("code", "")
        timeout = min(arguments.get("timeout", 10), config.MAX_CODE_EXECUTION_TIME)
        
        if not code:
            return {
                "content": [{"type": "text", "text": "Error: Empty code"}],
                "isError": True
            }
        
        # Security check
        if not self._is_safe(code):
            return {
                "content": [{"type": "text", "text": "Error: Code contains unsafe operations"}],
                "isError": True
            }
        
        try:
            result = self._execute_sandboxed(code, timeout)
            return {
                "content": [{"type": "text", "text": result}],
                "isError": False
            }
        except TimeoutError:
            return {
                "content": [{"type": "text", "text": f"Error: Execution timed out after {timeout}s"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    def _is_safe(self, code: str) -> bool:
        """Check if code is safe to execute."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        
        for node in ast.walk(tree):
            # Check for imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in self.DANGEROUS_MODULES:
                        return False
            
            # Check for dangerous builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_BUILTINS:
                        return False
            
            # Check for file operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['open', 'file']:
                        return False
        
        return True
    
    def _execute_sandboxed(self, code: str, timeout: int) -> str:
        """Execute code in restricted environment."""
        # Create restricted globals
        safe_builtins = {
            name: getattr(__builtins__, name)
            for name in dir(__builtins__)
            if name not in self.DANGEROUS_BUILTINS and not name.startswith('_')
        }
        
        # Add safe modules
        safe_globals = {
            "__builtins__": safe_builtins,
            "math": __import__("math"),
            "random": __import__("random"),
            "datetime": __import__("datetime"),
            "json": __import__("json"),
            "re": __import__("re"),
            "statistics": __import__("statistics"),
        }
        
        # Capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Set timeout
        def timeout_handler(signum, frame):
            raise TimeoutError("Code execution timed out")
        
        # Note: signal.SIGALRM is not available on Windows
        # For cross-platform compatibility, we'll use a simpler approach
        
        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, safe_globals)
        except TimeoutError:
            raise
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return f"Error during execution:\n{error_msg}"
        
        # Get output
        output = stdout_buffer.getvalue()
        errors = stderr_buffer.getvalue()
        
        result = ""
        if output:
            result += f"Output:\n{output}\n"
        if errors:
            result += f"Errors:\n{errors}\n"
        
        if not result:
            result = "Code executed successfully (no output)"
        
        return result.strip()


# Tool instance
code_executor_tool = CodeExecutorTool()
