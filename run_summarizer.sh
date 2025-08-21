#!/bin/bash

# Test script to run the Claude summarizer with batching

echo "=== Claude Batch Summarizer ==="
echo "Setting up environment..."

# Check if CLAUDE_API_KEY is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ CLAUDE_API_KEY not set!"
    echo "Please set it with: export CLAUDE_API_KEY='your-api-key-here'"
    exit 1
else
    echo "✅ CLAUDE_API_KEY is set"
fi

# Check if ordered_text directory exists
if [ ! -d "ordered_text" ]; then
    echo "❌ ordered_text directory not found!"
    exit 1
else
    file_count=$(ls ordered_text/page_*.txt 2>/dev/null | wc -l)
    echo "✅ Found $file_count text files in ordered_text/"
fi

# Run the summarizer
echo "🚀 Starting batch summarization..."
/workspaces/oo1-extractor/.venv/bin/python /workspaces/oo1-extractor/claude_summarizer.py

echo "✅ Summarization complete! Check the 'summarized_content' directory for results."
