# Code Review: Automation & Backup Scripts (2026-02-20 v1)

**Date**: 2026-02-20 04:05 HKT
**Reviewer**: [CV]
**Scope**: AFK Automation Script (`continue_and_report.sh`) and Database Backup Routine (`backup_duckdb.py`)

---

## 1. Changes Reviewed

### 1.1 `scripts/ops/continue_and_report.sh`
**Purpose**: Automates post-crawl workflows (Run correlation -> Backup DB -> Git Commit) when the user is AFK.
**Changes**:
- Added a `kill -0` wait loop mapped to the crawler PID.
- Sequentially executes correlation, backup, and git ops.
- Outputs logs to `tests/log/continue.out`.

**Verdict**: 🟡 APPROVED WITH WARNINGS
- **Risk**: The wait loop (`kill -0`) is brittle if the target PID halts early but leaves orphaned subprocesses (e.g., Python `subprocess.run`). This caused a file lock conflict previously where the script tried to run `correlate_all_stocks.py` while a zombie `crawl_fast.py` held the DuckDB lock.
- **Action**: Future versions should implement file-based status flags or proper task queuing instead of PID polling.

### 1.2 `scripts/ops/backup_duckdb.py`
**Purpose**: Exports monolithic DuckDB data into partitioned yearly Parquet files for Git tracking.
**Changes**:
- Connects to DuckDB (`read_only=True`).
- Iterates over distinct years in `daily_prices`.
- Copies subsets to `data/backup/prices_YYYY.parquet`.

**Verdict**: ✅ APPROVED
- Efficient use of DuckDB's native Parquet `COPY` exporting.
- Partitioning by year keeps file sizes under GitHub's 50MB limit.
- Ensures data persistence across Zeabur rebuilds.

---

## 2. Open Issues

| Issue | File | Severity | Status |
|-------|------|----------|--------|
| DuckDB File Lock | `continue_and_report.sh` | 🟡 Medium | Resolved manually, but automation is brittle |
| Missing Zeabur Volume | Deployment | 🔴 High | Blocked on persistent volume configuration |

---
**Signed**: [CV] Code Verification Agent
