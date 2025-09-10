import subprocess
import tempfile
import os
import sys
import signal
import threading
import time
from contextlib import contextmanager
from io import StringIO
import traceback

class CodeExecutor:
    """Secure Python code executor with sandboxing and timeout protection."""
    
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.restricted_imports = [
            'os', 'sys', 'subprocess', 'shutil', 'pathlib',
            'socket', 'urllib', 'requests', 'http',
            'ftplib', 'smtplib', 'telnetlib',
            'threading', 'multiprocessing',
            'ctypes', 'importlib'
        ]
    
    def set_timeout(self, timeout):
        """Set execution timeout in seconds."""
        self.timeout = timeout
    
    def _check_security(self, code):
        """Basic security check for dangerous operations."""
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess',
            'import shutil', 'import socket', 'import urllib',
            'import requests', 'import http', 'import threading',
            'import multiprocessing', 'import ctypes',
            'from os', 'from sys', 'from subprocess',
            '__import__', 'eval(', 'exec(',
            'open(', 'file(', 'input(',
            'raw_input(', 'compile(',
            'exit(', 'quit(', 'reload(',
            'globals(', 'locals(', 'vars(',
            'dir(', 'help(', 'copyright', 'credits',
            'license', 'exit', 'quit'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return False, f"Restricted operation detected: {pattern}"
        
        return True, ""
    
    @contextmanager
    def _capture_output(self):
        """Context manager to capture stdout and stderr."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            yield stdout_capture, stderr_capture
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _execute_with_timeout(self, code):
        """Execute code with timeout protection."""
        output = ""
        error = ""
        
        def target():
            nonlocal output, error
            try:
                with self._capture_output() as (stdout_capture, stderr_capture):
                    # Create a restricted globals environment
                    safe_globals = {
                        '__builtins__': {
                            'abs': abs, 'all': all, 'any': any, 'bin': bin,
                            'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
                            'chr': chr, 'complex': complex, 'dict': dict,
                            'divmod': divmod, 'enumerate': enumerate, 'filter': filter,
                            'float': float, 'frozenset': frozenset, 'hash': hash,
                            'hex': hex, 'int': int, 'isinstance': isinstance,
                            'issubclass': issubclass, 'iter': iter, 'len': len,
                            'list': list, 'map': map, 'max': max, 'min': min,
                            'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
                            'print': print, 'range': range, 'repr': repr,
                            'reversed': reversed, 'round': round, 'set': set,
                            'slice': slice, 'sorted': sorted, 'str': str,
                            'sum': sum, 'tuple': tuple, 'type': type,
                            'zip': zip, 'Exception': Exception, 'ValueError': ValueError,
                            'TypeError': TypeError, 'IndexError': IndexError,
                            'KeyError': KeyError, 'AttributeError': AttributeError,
                        }
                    }
                    
                    # Add safe imports
                    safe_globals['__builtins__']['__import__'] = __import__
                    
                    # Execute the code
                    exec(code, safe_globals)
                    
                    output = stdout_capture.getvalue()
                    error = stderr_capture.getvalue()
                    
            except Exception as e:
                error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            error = f"TimeoutError: Code execution exceeded {self.timeout} seconds"
            return "", error
        
        return output, error
    
    def execute_code(self, code):
        """
        Execute Python code safely with security checks and timeout.
        
        Args:
            code (str): Python code to execute
            
        Returns:
            tuple: (output, error) where both are strings
        """
        if not code.strip():
            return "", "No code to execute"
        
        # Security check
        is_safe, security_error = self._check_security(code)
        if not is_safe:
            return "", f"Security Error: {security_error}"
        
        try:
            # Execute with timeout
            output, error = self._execute_with_timeout(code)
            return output, error
            
        except Exception as e:
            return "", f"Execution Error: {str(e)}"
    
    def execute_code_subprocess(self, code):
        """
        Alternative execution method using subprocess (more secure but limited).
        
        Args:
            code (str): Python code to execute
            
        Returns:
            tuple: (output, error)
        """
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute in subprocess with timeout
            process = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            output, error = process.communicate(timeout=self.timeout)
            
            # Clean up
            os.unlink(temp_file)
            
            return output, error
            
        except subprocess.TimeoutExpired:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return "", f"TimeoutError: Code execution exceeded {self.timeout} seconds"
            
        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return "", f"Subprocess Error: {str(e)}"
