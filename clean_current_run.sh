#!/bin/bash
# Clean up output and Current Year's cache to force a fresh fetch for the active year.

CURRENT_YEAR=$(date +%Y)
echo "Cleaning output files..."
rm -f project_tw/output/*.xlsx

echo "Cleaning Cache for Current Year ($CURRENT_YEAR) to force refresh..."
rm -f data/raw/Market_${CURRENT_YEAR}_Prices.json
rm -f data/raw/TPEx_Market_${CURRENT_YEAR}_Prices.json
rm -f data/raw/TWT49U_${CURRENT_YEAR}.json

echo "Done. Next run will fetch fresh data for $CURRENT_YEAR."
