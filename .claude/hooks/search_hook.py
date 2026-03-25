#!/usr/bin/env python3
"""
Claude Search Hook for AI Code Helper

This hook runs when Claude performs file searches.
It enhances search results with AI-powered analysis and filtering.
"""

import sys
import os
import json
import re
from typing import Dict, Any, List

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

def search_hook(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process search results before Claude sees them.

    Args:
        query: The search query
        results: List of search result dictionaries

    Returns:
        Enhanced and filtered search results
    """
    # Filter out irrelevant results
    filtered_results = filter_results(query, results)

    # Add relevance scores
    scored_results = add_relevance_scores(query, filtered_results)

    # Sort by relevance
    sorted_results = sorted(scored_results, key=lambda x: x.get('relevance_score', 0), reverse=True)

    # Add AI insights if enabled
    if CONFIG.get('groq', {}).get('enabled', False) and GROQ_AVAILABLE and len(sorted_results) > 0:
        enhanced_results = add_ai_insights(query, sorted_results)
        return enhanced_results

    return sorted_results

def filter_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out irrelevant or unwanted search results.
    """
    filtered = []

    # Keywords that indicate irrelevant files
    irrelevant_patterns = [
        r'\.pyc$',  # Compiled Python files
        r'__pycache__',  # Cache directories
        r'\.git',  # Git files
        r'node_modules',  # Node modules
        r'\.env',  # Environment files
        r'\.log$',  # Log files
        r'\.tmp$',  # Temporary files
    ]

    for result in results:
        file_path = result.get('file_path', result.get('path', ''))

        # Skip irrelevant files
        if any(re.search(pattern, file_path) for pattern in irrelevant_patterns):
            continue

        # For Python projects, prioritize .py files for code-related queries
        if is_code_query(query) and not file_path.endswith(('.py', '.md', '.txt', '.json')):
            continue

        filtered.append(result)

    return filtered

def is_code_query(query: str) -> bool:
    """
    Determine if the search query is related to code.
    """
    code_keywords = [
        'function', 'class', 'def ', 'import ', 'method', 'variable',
        'code', 'implementation', 'algorithm', 'bug', 'error', 'fix'
    ]

    query_lower = query.lower()
    return any(keyword in query_lower for keyword in code_keywords)

def add_relevance_scores(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add relevance scores to search results.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for result in results:
        content = result.get('content', result.get('text', ''))
        file_path = result.get('file_path', result.get('path', ''))

        score = 0

        # Exact matches get highest score
        if query_lower in content.lower():
            score += 10

        # Word matches
        content_words = set(content.lower().split())
        matching_words = query_words.intersection(content_words)
        score += len(matching_words) * 2

        # File path relevance
        if any(word in file_path.lower() for word in query_words):
            score += 3

        # Python files get slight boost for code queries
        if is_code_query(query) and file_path.endswith('.py'):
            score += 1

        result['relevance_score'] = score

    return results

def add_ai_insights(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add AI-powered insights to search results.
    """
    if not GROQ_AVAILABLE or not client:
        return results

    try:
        # Prepare context from top results
        top_results = results[:5]  # Only analyze top 5 results
        context = "\n".join([
            f"File: {r.get('file_path', r.get('path', 'unknown'))}\nContent: {r.get('content', r.get('text', ''))[:200]}..."
            for r in top_results
        ])

        prompt = f"""Given this search query and the following file contents, provide a brief insight about what the search results suggest. Keep it under 50 words.

Query: {query}

Results:
{context}

Insight:"""

        response = client.chat.completions.create(
            model=CONFIG.get('groq', {}).get('model', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )

        insight = response.choices[0].message.content.strip()

        # Add insight to the first result
        if results:
            results[0]['ai_insight'] = insight.replace('\n', ' ')

    except Exception as e:
        print(f"AI insights failed: {e}", file=sys.stderr)

    return results

if __name__ == "__main__":
    # Hook interface - Claude will call this
    if len(sys.argv) < 2:
        print("Usage: python search_hook.py <query> [result_json]", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]

    # If results are provided as JSON string
    if len(sys.argv) > 2:
        try:
            results = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("Invalid JSON for results", file=sys.stderr)
            sys.exit(1)
    else:
        # For testing, create mock results
        results = [
            {
                'file_path': 'main.py',
                'content': 'def ask_ai(prompt):\n    # Function to call AI API',
                'line': 10
            },
            {
                'file_path': 'README.md',
                'content': '# AI Code Helper\nThis is a tool for reviewing code',
                'line': 1
            }
        ]

    # Process and output
    enhanced_results = search_hook(query, results)

    # Output as JSON
    print(json.dumps(enhanced_results, indent=2))