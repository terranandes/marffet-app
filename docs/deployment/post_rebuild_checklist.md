# Post-Rebuild Checklist

## 1. Verify Rebuild Completion
Check the logs or process to ensure `rebuild_market_db.py` has finished successfully.
The log file should end with "Done" or similar success message.

```bash
tail -f data/raw/mi_index/_rebuild.log
```

## 2. Fill Data Gaps (CRITICAL — Before Dividend Import)
If the rebuild experienced any network interruptions, some trading days may be missing.
This script detects and re-fetches them automatically.

```bash
uv run python scripts/ops/fill_rebuild_gaps.py
```

**Expected Output**: "No gaps found!" or a list of filled dates.
If persistent failures remain, investigate those specific dates manually.

## 3. Re-import TWSE Dividends (CRITICAL)
The rebuild process might populate dividends from YFinance (which is often inaccurate for TWSE).
We must overwrite this with official TWSE data using the re-import script.
**Note:** This script relies on `daily_prices` being populated in DuckDB (step 1).

```bash
# Run for the range 2003-2025
python scripts/ops/reimport_twse_dividends.py 2003 2025
```

## 4. Verify Data Integrity
Run the correlation scripts to ensure the new data source (DuckDB) matches expectations.

```bash
# Verify Mars Strategy Correlation (Grand Correlation)
python tests/analysis/correlate_mars.py
```

## 5. Restart Application
Restart the web server to ensure all in-memory caches are cleared and reloaded from the new DB.

```bash
# If running with uvicorn direct
pkill uvicorn
uvicorn app.main:app --reload --port 8000

# If using npm wrapper
npm run dev
```

## 6. Manual UI Check
- **Mars Strategy Tab**: Verify results load and look reasonable.
- **Bar Chart Race (BCR) Tab**: Verify animation plays.
- **Compound Interest (MoneyCome) Tab**: Verify value calculations.
