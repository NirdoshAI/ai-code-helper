#!/usr/bin/env python3
"""
Claude Edit Hook for AI Code Helper

This hook runs when Claude suggests code changes.
It validates, formats, and enhances the suggested edits using Groq AI.
"""

import sys
import os
import ast
import subprocess
import json
from typing import Dict, Any, Optional

# Import Groq for AI enhancements
try:
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_AVAILABLE = True
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except ImportError:
    GROQ_AVAILABLE = False
    client = None

def load_config() -> Dict[str, Any]:
    """Load configuration from .claude/config.json"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

CONFIG = load_config()

def edit_hook(file_path: str, original_content: str, new_content: str) -> str:
    """
    Process code changes before they're applied.

    Args:
        file_path: Path to the file being edited
        original_content: Original file content
        new_content: Suggested new content

    Returns:
        Processed and validated content
    """
    # Validate Python syntax if it's a Python file
    if file_path.endswith('.py'):
        validation_result = validate_python_code(new_content)
        if not validation_result['valid']:
            print(f"Warning: Syntax errors in suggested code: {validation_result['errors']}", file=sys.stderr)
            # Still return the content but log the warning

    # Apply formatting
    formatted_content = format_code(new_content, file_path)

    # Add helpful comments if needed
    enhanced_content = add_helpful_comments(formatted_content, file_path)

    # Use Groq AI for enhancement if enabled
    if CONFIG.get('groq', {}).get('enhance_edits', False) and GROQ_AVAILABLE and file_path.endswith('.py'):
        enhanced_content = enhance_with_groq(enhanced_content, original_content, file_path)

    return enhanced_content

def validate_python_code(code: str) -> Dict[str, Any]:
    """
    Validate Python code syntax.

    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    try:
        ast.parse(code)
        return {'valid': True, 'errors': []}
    except SyntaxError as e:
        return {'valid': False, 'errors': [str(e)]}
    except Exception as e:
        return {'valid': False, 'errors': [f"Parse error: {str(e)}"]}

def format_code(content: str, file_path: str) -> str:
    """
    Format the code using available formatters.
    """
    if not CONFIG.get('formatting', {}).get('use_black', True):
        return basic_format_python(content)

    # Try black formatter if available
    try:
        result = subprocess.run(
            ['black', '--diff', '--quiet', '-'],
            input=content,
            text=True,
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            # No changes needed
            return content
        elif result.returncode == 1:
            # Changes would be made, apply them
            result = subprocess.run(
                ['black', '-'],
                input=content,
                text=True,
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: basic formatting
    return basic_format_python(content)

def basic_format_python(content: str) -> str:
    """
    Basic Python formatting as fallback.
    """
    lines = content.split('\n')
    formatted_lines = []

    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        formatted_lines.append(line)

    # Remove excessive blank lines
    result = []
    prev_blank = False
    for line in formatted_lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return '\n'.join(result)

def add_helpful_comments(content: str, file_path: str) -> str:
    """
    Add helpful comments to the code.
    """
    if not CONFIG.get('formatting', {}).get('add_docstrings', True):
        return content

    lines = content.split('\n')
    enhanced_lines = []

    for i, line in enumerate(lines):
        enhanced_lines.append(line)

        # Add comment after function definitions
        if line.strip().startswith('def ') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line.startswith('"""') and not next_line.startswith("'''"):
                # Add a placeholder for docstring
                enhanced_lines.append('    """TODO: Add docstring"""')
                enhanced_lines.append('')

    return '\n'.join(enhanced_lines)

def enhance_with_groq(content: str, original_content: str, file_path: str) -> str:
    """
    Use Groq AI to enhance the code suggestions.
    """
    if not GROQ_AVAILABLE or not client:
        return content

    try:
        prompt = f"""You are an expert Python code reviewer. Given the following code changes, provide an enhanced version that:

1. Improves code quality and readability
2. Adds appropriate error handling where needed
3. Follows Python best practices
4. Includes helpful comments for complex logic
5. Maintains the original functionality

Original code:
{original_content}

Suggested changes:
{content}

Return only the enhanced Python code without any explanation or markdown formatting:"""

        response = client.chat.completions.create(
            model=CONFIG.get('groq', {}).get('model', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )

        enhanced_code = response.choices[0].message.content.strip()

        # Validate the enhanced code
        if validate_python_code(enhanced_code)['valid']:
            print("Code enhanced with Groq AI", file=sys.stderr)
            return enhanced_code
        else:
            print("Groq enhancement produced invalid code, using original", file=sys.stderr)
            return content

    except Exception as e:
        print(f"Groq enhancement failed: {e}, using original", file=sys.stderr)
        return content

if __name__ == "__main__":
    # Hook interface - Claude will call this
    if len(sys.argv) != 3:
        print("Usage: python edit_hook.py <file_path> <new_content>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    new_content = sys.argv[2]

    # Read original content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"Error reading original file {file_path}: {e}", file=sys.stderr)
        original_content = ""

    # Process and output
    processed = edit_hook(file_path, original_content, new_content)
    print(processed)
