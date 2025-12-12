#!/bin/bash
# Script to manually trigger the full Mars Strategy Analysis

echo "Starting Martian Analysis Scan..."
echo "This will fetch latest prices, apply split detection (including 0050), and regenerate stock lists."
echo "Output will be saved to: project_tw/output/stock_list_s2006e2025_filtered.xlsx"

# Ensure venv
if [ -d ".venv" ]; then
    PYTHONPATH=. ./.venv/bin/python3 project_tw/run_analysis.py
else
    echo "Error: .venv not found. Please run ./start_app.sh first to setup environment."
    exit 1
fi

echo "Scan Complete."
