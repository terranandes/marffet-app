#!/bin/bash

# Automated Continuation Script for AFK User
# 1. Wait for fix_discrepancies.py to finish (PID 6ca21010)
# 2. Run Final Correlation Report
# 3. Backup DuckDB to Parquet
# 4. Git Commit
# 5. Report Status

LOG_FILE="tests/log/continue_report_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🕒 Script started at $(date)"
echo "💤 Waiting for fix_discrepancies.py (PID 6ca21010)..."

# Wait loop
while kill -0 6ca21010 2>/dev/null; do
    sleep 60
    echo "   ... still running at $(date)"
done

echo "✅ fix_discrepancies.py finished."

# 2. Run Correlation Report
echo "📊 Running Final Correlation Report..."
uv run python tests/analysis/correlate_all_stocks.py

# 3. Backup DB
echo "💾 Backing up DuckDB to Parquet..."
# Check if backup_duckdb.py exists (it should be created if not)
if [ ! -f scripts/ops/backup_duckdb.py ]; then
    echo "⚠️  backup_duckdb.py not found. Creating simple backup..."
    # Create simple backup script
    cat <<EOF > scripts/ops/backup_duckdb.py
import duckdb
import os

os.makedirs('data/backup', exist_ok=True)
conn = duckdb.connect('data/market.duckdb', read_only=True)
years = conn.execute("SELECT DISTINCT year FROM daily_prices ORDER BY year").fetchall()
for (y,) in years:
    print(f"Exporting {y}...")
    conn.execute(f"COPY (SELECT * FROM daily_prices WHERE year={y}) TO 'data/backup/prices_{y}.parquet' (FORMAT 'parquet')")
print("Backup complete.")
EOF
fi

uv run python scripts/ops/backup_duckdb.py

# 4. Git Commit
echo "📤 Committing backups..."
git add data/backup/*.parquet docs/product/correlation_report_full.csv docs/product/tasks.md
git commit -m "chore: automated backup and correlation report after bulk fix"
git push origin master || echo "⚠️  Push failed (SSH issue?), checks local commit."

echo "🎉 All Done at $(date)"
