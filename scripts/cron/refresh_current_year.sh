#!/bin/bash

# Ensure we are in project root (assuming script is in scripts/cron/)
cd "$(dirname "$0")/../.."

echo "---------------------------------------------------"
echo "🕒 Starting Nightly Refresh: $(date)"
echo "📂 Working Directory: $(pwd)"

# 1. Run Ultra-Fast Crawler (Current Year)
# This includes Name Fixing and Dividend Updates
echo "🕷️  Running Ultra-Fast Crawler (Current Year)..."
CURRENT_YEAR=$(date +%Y)
uv run python scripts/ops/crawl_fast.py --start-year $CURRENT_YEAR

CRAWL_EXIT_CODE=$?
if [ $CRAWL_EXIT_CODE -ne 0 ]; then
    echo "❌ Full supplement failed with exit code $CRAWL_EXIT_CODE"
    exit $CRAWL_EXIT_CODE
fi
# 1.5 Backup DuckDB to Parquet
echo "💾 Backing up DuckDB to Parquet..."
uv run python scripts/ops/backup_duckdb.py
BACKUP_EXIT_CODE=$?
if [ $BACKUP_EXIT_CODE -ne 0 ]; then
    echo "⚠️ Parquet backup failed, but continuing..."
fi

# 2. Trigger Admin Webhook via curl
# Validates using X-API-KEY (added to app/auth.py)
echo "🔄 Triggering API Refresh..."
CRON_SECRET=${CRON_SECRET:-change_me_in_prod_please}
API_URL=${API_URL:-http://localhost:8000}

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_URL/api/admin/refresh-market-data" \
     -H "X-API-KEY: $CRON_SECRET" \
     -H "Content-Type: application/json")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

echo "Response Body: $BODY"

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Success: Market Data Refreshed."
else
    echo "❌ API Call Failed (Status $HTTP_STATUS)."
    exit 1
fi

# 3. Push to GitHub
echo "📤 Pushing to GitHub..."
curl -s -X POST "$API_URL/api/admin/market-data/push" \
     -H "X-API-KEY: $CRON_SECRET" \
     -H "Content-Type: application/json" || echo "Push endpoint not available"

echo "🎉 Nightly Refresh Complete."
echo "---------------------------------------------------"
