# -*- coding: utf-8 -*-
import ast
import re
import sys
import traceback
from typing import Tuple, List

def validate_python_syntax(code: str) -> Tuple[bool, str]:
    """
    Validate Python syntax without executing the code.
    
    Args:
        code (str): Python code to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not code.strip():
        return True, ""
    
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        error_msg = f"Line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f"\n  {e.text.strip()}"
            if e.offset:
                error_msg += f"\n  {' ' * (e.offset - 1)}^"
        return False, error_msg
    except Exception as e:
        return False, f"Parse error: {str(e)}"

def format_error_message(error: str) -> str:
    """
    Format error messages for better readability.
    
    Args:
        error (str): Raw error message
        
    Returns:
        str: Formatted error message
    """
    if not error:
        return ""
    
    # Extract the most relevant part of traceback
    lines = error.strip().split('\n')
    
    # Find the actual error line
    error_line = ""
    for line in reversed(lines):
        if line and not line.startswith('  ') and not line.startswith('    '):
            error_line = line
            break
    
    # Format common Python errors
    if "NameError" in error:
        formatted = "NAME ERROR: Variable or function not defined\n"
    elif "SyntaxError" in error:
        formatted = "📝 **Syntax Error**: Check your code syntax\n"
    elif "TypeError" in error:
        formatted = "⚠️ **Type Error**: Incorrect data type usage\n"
    elif "ValueError" in error:
        formatted = "💥 **Value Error**: Invalid value provided\n"
    elif "IndexError" in error:
        formatted = "📋 **Index Error**: List/string index out of range\n"
    elif "KeyError" in error:
        formatted = "🔑 **Key Error**: Dictionary key not found\n"
    elif "AttributeError" in error:
        formatted = "ATTRIBUTE ERROR: Object doesn't have this attribute\n"
    elif "IndentationError" in error:
        formatted = "📐 **Indentation Error**: Check your code indentation\n"
    elif "TimeoutError" in error:
        formatted = "⏰ **Timeout Error**: Code took too long to execute\n"
    else:
        formatted = "EXECUTION ERROR:\n"
    
    formatted += f"```\n{error_line}\n```"
    
    # Add helpful tips
    if "NameError" in error:
        formatted += "\nTIP: Make sure all variables are defined before use"
    elif "SyntaxError" in error:
        formatted += "\nTIP: Check for missing colons, brackets, or quotes"
    elif "IndentationError" in error:
        formatted += "\nTIP: Use consistent indentation (4 spaces recommended)"
    elif "TimeoutError" in error:
        formatted += "\nTIP: Avoid infinite loops or very long operations"
    
    return formatted

def extract_imports(code: str) -> List[str]:
    """
    Extract all import statements from code.
    
    Args:
        code (str): Python code
        
    Returns:
        list: List of imported modules
    """
    imports = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except:
        # Fallback to regex if AST parsing fails
        import_pattern = r'(?:^|\n)\s*(?:import\s+(\w+)|from\s+(\w+)\s+import)'
        matches = re.findall(import_pattern, code)
        for match in matches:
            imports.extend([m for m in match if m])
    
    return list(set(imports))

def get_code_stats(code: str) -> dict:
    """
    Get basic statistics about the code.
    
    Args:
        code (str): Python code
        
    Returns:
        dict: Code statistics
    """
    if not code.strip():
        return {
            'lines': 0,
            'characters': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0
        }
    
    lines = len(code.split('\n'))
    characters = len(code)
    
    try:
        tree = ast.parse(code)
        functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        imports = len(extract_imports(code))
    except:
        functions = code.count('def ')
        classes = code.count('class ')
        imports = code.count('import ')
    
    return {
        'lines': lines,
        'characters': characters,
        'functions': functions,
        'classes': classes,
        'imports': imports
    }

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename or "untitled.py"

def highlight_syntax_errors(code: str) -> List[dict]:
    """
    Find and highlight syntax errors in code.
    
    Args:
        code (str): Python code
        
    Returns:
        list: List of error annotations for the editor
    """
    annotations = []
    
    try:
        ast.parse(code)
    except SyntaxError as e:
        if e.lineno:
            annotations.append({
                'row': e.lineno - 1,  # ace editor uses 0-based indexing
                'column': e.offset - 1 if e.offset else 0,
                'type': 'error',
                'text': e.msg
            })
    except Exception:
        pass
    
    return annotations
