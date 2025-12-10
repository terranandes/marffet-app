#!/bin/bash
# Wrapper to run the Martian Stock Analysis correctly
# This ensures Python finds the 'project_tw' module

echo "Starting Martian Stock Analysis..."
# Activate venv if it exists, otherwise assume system python
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run as a module to fix import paths
python3 -m project_tw.run_analysis
