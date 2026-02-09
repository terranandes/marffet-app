#!/bin/bash
# Annual Full Crawl + Prewarm Script
# Schedule: Jan 1st, 02:00 UTC (10:00 Taipei)
# Purpose: Crawl all years (2000-2026) and refresh MarketCache

cd "$(dirname "$0")/../.."

echo "---------------------------------------------------"
echo "🎆 Starting Annual Prewarm: $(date)"
echo "📂 Working Directory: $(pwd)"

# 1. Run Full Crawler (all years)
echo "🕷️ Running Full Crawler (2000-2026)..."
./scripts/ops/run_crawler_prod.sh --foreground 2000 2026

CRAWL_EXIT_CODE=$?
if [ $CRAWL_EXIT_CODE -ne 0 ]; then
    echo "❌ Crawler failed with exit code $CRAWL_EXIT_CODE"
    exit $CRAWL_EXIT_CODE
fi

# 2. Trigger Admin Webhook to refresh cache
echo "🔄 Triggering API Refresh..."
CRON_SECRET=${CRON_SECRET:-change_me_in_prod_please}
API_URL=${API_URL:-http://localhost:8000}

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_URL/api/admin/refresh-market-data" \
     -H "X-API-KEY: $CRON_SECRET" \
     -H "Content-Type: application/json")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Cache Refreshed."
else
    echo "⚠️ API Call returned status $HTTP_STATUS (continuing...)"
fi

# 3. Backup to GitHub (optional - if BackupService.refresh_prewarm_data is exposed)
echo "📦 Triggering Prewarm Backup..."
curl -s -X POST "$API_URL/api/admin/refresh-prewarm" \
     -H "X-API-KEY: $CRON_SECRET" \
     -H "Content-Type: application/json" || echo "Backup endpoint not available"

echo "🎉 Annual Prewarm Complete."
echo "---------------------------------------------------"
