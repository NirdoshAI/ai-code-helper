#!/usr/bin/env python3
"""
Claude Read Hook for AI Code Helper

This hook runs when Claude reads files from the workspace.
It adds helpful context and AI-powered analysis for code understanding.
"""

import sys
import os
import json
from typing import Dict, Any

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

def read_hook(file_path: str, content: str) -> str:
    """
    Process content before Claude analyzes it.

    Args:
        file_path: Path to the file being read
        content: Original file content

    Returns:
        Processed content with added context
    """
    # Add project context header
    project_context = f"""# AI Code Helper Project Context
# File: {file_path}
# Project: AI-powered Python CLI tool using Groq API and LLaMA
# Commands: review, explain, improve
#
# Original content follows:
# {'='*50}

"""

    # For Python files, add analysis
    if file_path.endswith('.py'):
        processed_content = add_python_context(content, file_path)
    else:
        processed_content = content

    return project_context + processed_content

def add_python_context(content: str, file_path: str) -> str:
    """
    Add Python-specific context to the content.
    """
    lines = content.split('\n')

    # Analyze code structure
    analysis = analyze_code_structure(lines)

    context_parts = []
    context_parts.append(f"\n# Code Analysis for {os.path.basename(file_path)}")
    context_parts.append(f"# Lines: {len(lines)}")
    context_parts.append(f"# Functions: {len(analysis['functions'])}")
    context_parts.append(f"# Classes: {len(analysis['classes'])}")
    context_parts.append(f"# Imports: {len(analysis['imports'])}")

    if analysis['functions']:
        context_parts.append(f"# Functions: {', '.join(analysis['functions'][:5])}{'...' if len(analysis['functions']) > 5 else ''}")
    if analysis['classes']:
        context_parts.append(f"# Classes: {', '.join(analysis['classes'])}")

    # Add AI analysis if enabled
    if CONFIG.get('groq', {}).get('code_analysis', False) and GROQ_AVAILABLE:
        ai_analysis = get_ai_analysis(content, file_path)
        if ai_analysis:
            context_parts.append(f"# AI Analysis: {ai_analysis}")

    context_parts.append("\n# Original code follows:")
    context_parts.append("")

    return '\n'.join(context_parts) + content

def analyze_code_structure(lines: list) -> Dict[str, list]:
    """
    Analyze the structure of Python code.
    """
    imports = []
    functions = []
    classes = []

    for line in lines:
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
        elif line.startswith('def '):
            func_name = line.split('(')[0].replace('def ', '')
            functions.append(func_name)
        elif line.startswith('class '):
            class_name = line.split(':')[0].replace('class ', '').split('(')[0]
            classes.append(class_name)

    return {
        'imports': imports,
        'functions': functions,
        'classes': classes
    }

def get_ai_analysis(content: str, file_path: str) -> str:
    """
    Get AI-powered analysis of the code using Groq.
    """
    if not GROQ_AVAILABLE or not client:
        return ""

    try:
        # Limit content length for API
        if len(content) > 2000:
            content = content[:2000] + "\n... (truncated)"

        prompt = f"""Analyze this Python code file and provide a brief summary of its purpose and key features. Keep it under 100 words.

File: {os.path.basename(file_path)}
Code:
{content}

Summary:"""

        response = client.chat.completions.create(
            model=CONFIG.get('groq', {}).get('model', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )

        analysis = response.choices[0].message.content.strip()
        return analysis.replace('\n', ' ')  # Make it single line

    except Exception as e:
        print(f"AI analysis failed: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    # Hook interface - Claude will call this
    if len(sys.argv) != 2:
        print("Usage: python read_hook.py <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Process and output
    processed = read_hook(file_path, content)
    print(processed)
