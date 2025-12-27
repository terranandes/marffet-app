#!/bin/bash
# Universal Verification Runner

# Ensure script fails on error
set -e

echo "Starting Verification Process..."
echo "Date: $(date)"

# Check if we are in environment (simple check)
if command -v pytest &> /dev/null; then
    RUNNER="pytest"
elif [ -f ".venv/bin/pytest" ]; then
    RUNNER=".venv/bin/pytest"
else
    echo "pytest not found. Attempting to run via python module..."
    RUNNER="python3 -m pytest"
fi

echo "Using runner: $RUNNER"

# Run Tests
# -v: verbose
# -s: show stdout/stderr (optional, maybe remove for strict CI)
$RUNNER tests/ -v

echo "Verification Complete."
