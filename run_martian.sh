#!/bin/bash
# Wrapper to run the Martian Stock Analysis correctly
# This ensures Python finds the 'project_tw' module

echo "Starting Martian Stock Analysis..."
# Run as a module to fix import paths using uv
uv run python -m project_tw.run_analysis
