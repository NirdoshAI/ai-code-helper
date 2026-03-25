# Claude Hooks for AI Code Helper

This directory contains Claude hooks that enhance the AI code helper experience with Groq AI integration.

## Available Hooks

### `read_hook.py` - Enhanced File Reading
- **Purpose**: Processes files before Claude reads them
- **Features**:
  - Adds project context headers
  - Analyzes Python code structure (functions, classes, imports)
  - **NEW**: AI-powered code analysis using Groq API
  - Provides detailed metadata for better code understanding

### `edit_hook.py` - AI-Enhanced Code Editing
- **Purpose**: Processes code changes before they're applied
- **Features**:
  - Validates Python syntax
  - Formats code using Black (if available) or basic formatting
  - Adds docstring placeholders for functions
  - **NEW**: Groq AI enhancement for code improvements
  - Adds error handling and best practices automatically

### `run_hook.py` - Command Enhancement & Logging
- **Purpose**: Processes terminal commands before execution
- **Features**:
  - Logs all commands to `command_log.jsonl` with timestamps
  - Validates commands for safety (blocks dangerous operations)
  - Enhances Python/pip commands (adds `--user` flag to pip installs)
  - Validates AI code helper specific commands

### `search_hook.py` - Smart Search Enhancement
- **Purpose**: Enhances file search results
- **Features**:
  - Filters out irrelevant files (cache, logs, etc.)
  - Adds relevance scoring to results
  - Prioritizes code files for code-related queries
  - **NEW**: AI-powered insights for search results

## Configuration

The hooks are configured via `.claude/config.json`:

```json
{
  "hooks": {
    "read_hook": { "enabled": true, "add_context": true, "analyze_code": true },
    "edit_hook": { "enabled": true, "validate_syntax": true, "format_code": true, "add_docstrings": true, "groq_enhancement": true },
    "run_hook": { "enabled": true, "log_commands": true, "safety_check": true, "enhance_commands": true },
    "search_hook": { "enabled": true, "filter_results": true, "add_scores": true, "ai_insights": true }
  },
  "groq": {
    "enabled": true,
    "model": "llama-3.3-70b-versatile",
    "enhance_edits": true,
    "code_analysis": true
  },
  "formatting": {
    "use_black": true,
    "line_length": 88,
    "add_docstrings": true
  },
  "logging": {
    "command_log": "command_log.jsonl",
    "max_log_size": 1000
  }
}
```

## AI Integration Features

### Groq API Enhancements
- **Code Analysis**: Automatically analyzes code purpose and features
- **Edit Enhancement**: Improves code quality, adds error handling, follows best practices
- **Search Insights**: Provides AI-powered analysis of search results

### Safety Features
- Command validation and dangerous command blocking
- Automatic `--user` flag addition for pip installs
- Syntax validation for code changes

## Usage

The hooks are automatically called by Claude when:
- **Reading files** (read_hook) - Adds context and AI analysis
- **Suggesting edits** (edit_hook) - Validates, formats, and enhances code
- **Running commands** (run_hook) - Logs and enhances terminal commands
- **Searching files** (search_hook) - Filters and ranks search results

## Logs and Monitoring

- **Command Log**: `command_log.jsonl` in project root tracks all terminal activity
- **Error Output**: Hooks write warnings/errors to stderr for Claude to see
- **AI Insights**: Groq API calls are logged for debugging

## Customization

You can modify the hooks to:
- Add more validation rules
- Integrate additional AI services
- Include project-specific formatting
- Add custom logging or monitoring
- Create new hook types for specific workflows

## Dependencies

The enhanced hooks require:
- `groq` package (for AI features)
- `python-dotenv` (for API key loading)
- `black` (optional, for code formatting)

Install with: `pip install groq python-dotenv black`

You can modify the hooks to:
- Add more validation rules
- Integrate with your Groq API
- Add project-specific formatting
- Include additional logging or monitoring

## Logs

Command executions are logged to `command_log.jsonl` in the project root for debugging and analysis.