#!/bin/bash
# TOTAL RESET: Deletes ALL cache files to force a complete re-download of 19 years of data.
# WARNING: The next run will take ~15-20 minutes.

echo "WARNING: This will delete ALL cached market data from 2006 to Present."
echo "The next scan will be SLOW (~15 mins) as it re-downloads everything."
read -p "Are you sure? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo "Cleaning ALL Market Prices..."
rm -f data/raw/Market_*_Prices.json
rm -f data/raw/TPEx_Market_*_Prices.json

echo "Cleaning ALL Dividend Data..."/raw/TWT49U_*.json

echo "Cache Cleared. Run './run_martian.sh' to start a Fresh Scan."
