#!/bin/bash
# Resolve Daily Dividends (Quarterly Cron)
# Runs the Goodinfo fetcher in incremental mode to patch new combined dividends.

# Ensure we are in the project root
cd "$(dirname "$0")/../.."

# Activate environment if needed, or rely on uv run
echo "🔄 Starting Dividend Resolution (Goodinfo Incremental)..."
date

# Run fetcher incrementally
uv run python3 scripts/ops/fetch_goodinfo_dividends.py --incremental

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Dividend Resolution Complete."
else
    echo "❌ Dividend Resolution Failed."
    exit 1
fi
