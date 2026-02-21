# Implementation Plan: Zeabur DuckDB Deployment (Phase 8)

## Goal Description
Deploy our lightning-fast, highly accurate DuckDB nominal pricing engine to Zeabur without inflating repository size or causing Container Startup Timeouts. We will achieve this using a Persistent Volume Mount combined with a Parquet-based bootstrap sequence.

## Proposed Changes

### 1. Parquet Export Pipeline (Local)
Create a utility script to convert our local DuckDB state into neat, git-friendly Parquet files.
#### [NEW] `scripts/ops/backup_duckdb.py`
- Connects to `data/market.duckdb`.
- Executes `COPY (SELECT * FROM daily_prices WHERE year = YYYY) TO 'data/backup/prices_YYYY.parquet'`.
- Executes `COPY (SELECT * FROM dividends) TO 'data/backup/dividends.parquet'`.
- This ensures no single file exceeds GitHub's size constraints, keeping git operations snappy.

### 2. Zeabur Volume Configuration
Update the infrastructure configuration to persist our data across deploys.
#### [MODIFY] `zeabur.json` (or via Zeabur Dashboard) 
- Declare a persistent volume mounted at `/data`.
- This ensures the DuckDB file survives container restarts and retains the automated daily crawls.

### 3. Application Rehydration Logic
Modify the backend initialization code to automatically construct the DB on the first fresh boot on Zeabur.
#### [MODIFY] `app/main.py` (or `app/services/market_db.py`)
- During FastAPI `@asynccontextmanager`, check if `/data/market.duckdb` exists.
- If it exists -> Proceed normally.
- If missing -> Rehydrate! Execute DuckDB queries to read all `data/backup/*.parquet` into the new persistent `market.duckdb` database.

### 4. Cron Scheduling
Update the daily crawler to run directly on the deployed server.
#### [MODIFY] `scripts/cron/refresh_current_year.sh`
- Ensure this script targets the persistent DB path.
- (Optional) Configure a cronjob within Zeabur to execute this script daily at 16:00 Taiwan time to fetch new nominal closing prices.

## Verification Plan
1. Run `python scripts/ops/backup_duckdb.py` locally.
2. Verify that `data/backup/` contains parquets covering 2004-2026.
3. Temporarily delete the local `market.duckdb` entirely.
4. Run the app (`uvicorn app.main:app`). Watch the console logs confirm "Rehydrating DB from Parquets...".
5. Verify the app successfully starts and the Mars Strategy tab responds instantly, identical to the prior state.
6. Commit Parquets, Push to Master, and monitor Zeabur deployment logs.
