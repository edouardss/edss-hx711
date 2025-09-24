#!/bin/bash
# Clean virtual environment activation script

echo "🐍 Activating virtual environment..."

# Clean existing PATH first
export PATH=$(echo $PATH | tr ':' '\n' | awk '!seen[$0]++' | tr '\n' ':' | sed 's/:$//')

# Set virtual environment variables
export VIRTUAL_ENV="/home/edss/edss-hx711/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Remove duplicates again (in case venv/bin was already in PATH)
export PATH=$(echo $PATH | tr ':' '\n' | awk '!seen[$0]++' | tr '\n' ':' | sed 's/:$//')

echo "✅ Virtual environment activated: $VIRTUAL_ENV"
echo "📁 Python location: $(which python)"
