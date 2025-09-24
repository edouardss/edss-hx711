#!/bin/bash
# Script to clean up PATH and prevent duplicates

echo "🧹 Cleaning up PATH..."

# Remove duplicates from PATH
export PATH=$(echo $PATH | tr ':' '\n' | awk '!seen[$0]++' | tr '\n' ':' | sed 's/:$//')

echo "✅ PATH cleaned!"
echo "Current PATH entries:"
echo $PATH | tr ':' '\n' | nl

# Show if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🐍 Virtual environment: $VIRTUAL_ENV"
else
    echo "🐍 No virtual environment active"
fi
