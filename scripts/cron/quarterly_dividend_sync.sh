#!/bin/bash
# Quarterly Dividend Sync Script
# Schedule: Jan/Apr/Jul/Oct 1st, 03:00 UTC (11:00 Taipei)
# Purpose: Sync dividend data for all stocks and backup to GitHub
#
# NOTE: This script calls the in-app endpoint. The actual sync logic
# is lightweight (just API calls to cache/backup), so can remain in-app.
# This script exists for external trigger capability (e.g., manual run).

cd "$(dirname "$0")/../.."

echo "---------------------------------------------------"
echo "💰 Starting Quarterly Dividend Sync: $(date)"
echo "📂 Working Directory: $(pwd)"

CRON_SECRET=${CRON_SECRET:-change_me_in_prod_please}
API_URL=${API_URL:-http://localhost:8000}

# Trigger the sync endpoint (if exposed, otherwise this is a placeholder)
# Currently the quarterly sync runs in-app via APScheduler
# This script can be used for manual triggering or external cron override

echo "🔄 Triggering Dividend Sync API (if available)..."

# Option 1: Use the global admin sync endpoint (Universe + Push)
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_URL/api/admin/market-data/sync-dividends" \
     -H "X-API-KEY: $CRON_SECRET" \
     -H "Content-Type: application/json")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

echo "Response Body: $BODY"

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Dividend Sync Complete."
else
    echo "⚠️ Sync returned status $HTTP_STATUS"
fi

echo "💰 Quarterly Dividend Sync Complete."
echo "---------------------------------------------------"
