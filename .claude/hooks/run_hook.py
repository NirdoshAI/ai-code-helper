#!/usr/bin/env python3
"""
Claude Run Hook for AI Code Helper

This hook runs when Claude executes terminal commands.
It logs commands, validates them, and can integrate with the AI code helper.
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

def run_hook(command: str, cwd: str) -> Optional[str]:
    """
    Process terminal commands before execution.

    Args:
        command: The command being executed
        cwd: Current working directory

    Returns:
        Modified command or None to proceed with original
    """
    # Log the command
    log_command(command, cwd)

    # Validate command for safety
    validation = validate_command(command)
    if not validation['safe']:
        print(f"Warning: Potentially unsafe command: {validation['reason']}", file=sys.stderr)
        # Still allow it but log the warning

    # For Python-related commands, enhance them
    if is_python_command(command):
        enhanced_command = enhance_python_command(command, cwd)
        if enhanced_command != command:
            print(f"Enhanced command: {enhanced_command}", file=sys.stderr)
            return enhanced_command

    # For the AI code helper commands, validate arguments
    if command.startswith('python main.py'):
        validation = validate_ai_helper_command(command)
        if not validation['valid']:
            print(f"AI Helper command issue: {validation['message']}", file=sys.stderr)

    return None  # Proceed with original command

def log_command(command: str, cwd: str):
    """
    Log the command execution for debugging.
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'cwd': cwd,
        'user': os.getenv('USERNAME', 'unknown')
    }

    log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'command_log.jsonl')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Failed to log command: {e}", file=sys.stderr)

def validate_command(command: str) -> Dict[str, Any]:
    """
    Basic command validation for safety.
    """
    dangerous_commands = [
        'rm -rf /',
        'del /s /q c:\\',
        'format',
        'fdisk',
        'sudo rm',
        'rm -rf ~'
    ]

    for dangerous in dangerous_commands:
        if dangerous in command.lower():
            return {
                'safe': False,
                'reason': f'Contains potentially dangerous command: {dangerous}'
            }

    return {'safe': True, 'reason': ''}

def is_python_command(command: str) -> bool:
    """
    Check if the command is Python-related.
    """
    return (
        command.startswith('python') or
        command.startswith('python3') or
        'pip' in command or
        '.py' in command
    )

def enhance_python_command(command: str, cwd: str) -> str:
    """
    Enhance Python commands with additional flags or setup.
    """
    # For running Python files, add verbose flag if not present
    if command.startswith('python ') and not any(flag in command for flag in ['-v', '--verbose', '-m']):
        # Check if it's running a .py file
        parts = command.split()
        if len(parts) >= 2 and parts[1].endswith('.py'):
            return command  # Don't modify direct file execution

    # For pip installs, add --user flag for safety
    if command.startswith('pip install') and '--user' not in command and 'sudo' not in command:
        return command.replace('pip install', 'pip install --user', 1)

    return command

def validate_ai_helper_command(command: str) -> Dict[str, Any]:
    """
    Validate AI code helper specific commands.
    """
    parts = command.split()
    if len(parts) < 3:
        return {'valid': False, 'message': 'Missing arguments for AI helper command'}

    action = parts[2]
    valid_actions = ['review', 'explain', 'improve']

    if action not in valid_actions:
        return {'valid': False, 'message': f'Invalid action: {action}. Valid: {valid_actions}'}

    if len(parts) < 4:
        return {'valid': False, 'message': 'Missing filename argument'}

    filename = parts[3]
    if not os.path.exists(filename):
        return {'valid': False, 'message': f'File does not exist: {filename}'}

    return {'valid': True, 'message': ''}

if __name__ == "__main__":
    # Hook interface - Claude will call this
    if len(sys.argv) < 2:
        print("Usage: python run_hook.py <command> [cwd]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    cwd = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    # Process the command
    result = run_hook(command, cwd)

    # Output the command to execute (modified or original)
    if result:
        print(result)
    else:
        print(command)