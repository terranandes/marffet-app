#!/bin/bash

# Production Runner for Ultra-Fast Crawler
# Usage: ./run_crawler_prod.sh [start_year] [end_year]

# Check for foreground flag
RUN_MODE="background"
if [ "$1" == "--foreground" ]; then
    RUN_MODE="foreground"
    shift
fi

START_YEAR=${1:-2000}
END_YEAR=${2:-2025}
LOG_FILE="tests/log/Crawler_Prod_$(date +%Y%m%d_%H%M%S).log"

mkdir -p tests/log

echo "🚀 Starting Production Crawler (Mode: $RUN_MODE)"
echo "📅 Years: $START_YEAR to $END_YEAR"
echo "📝 Log: $LOG_FILE"

# Run command based on mode
CMD="uv run python tests/ops_scripts/crawl_fast.py --start-year $START_YEAR --end-year $END_YEAR --output-dir data/raw"

if [ "$RUN_MODE" == "foreground" ]; then
    # Run in foreground, still logging to file but also waiting
    $CMD > "$LOG_FILE" 2>&1
    echo "✅ Crawler finished (Foreground)."
else
    # Run with nohup in background
    nohup $CMD > "$LOG_FILE" 2>&1 &
    PID=$!
    echo "✅ Crawler launched in background. PID: $PID"
    echo "   To monitor: tail -f $LOG_FILE"
fi
