    # Code Review — 2026-02-17 v2 (03:29 HKT)
**Reviewer:** [CV] (Code Verification Agent)
**Scope:** Mars Strategy correlation sprint (since meeting v1)

---

## New Files Created

| File | Purpose | Verdict |
|------|---------|---------|
| `tests/analysis/correlate_all_stocks.py` | Grand correlation vs MoneyCome Excel | ✅ Well-structured |
| `tests/log/correlation_report.xlsx` | Side-by-side CAGR comparison for all stocks | ✅ Output artifact |

## Files Modified (Focus Review)

### [market_db.py](file:///home/terwu01/github/martian/app/services/market_db.py) — **Critical Change**
- Added `_resolve_db_path()` with volume priority logic
- **Risk**: `/data/` directory check uses `is_dir()` — safe, won't trigger on files
- **Edge case**: If `/data/` exists but is not a Zeabur volume (e.g., some other system), it would try to copy there. Mitigated by the `exists()` check on source file.
- **Verdict**: ✅ APPROVED

### [admin.py](file:///home/terwu01/github/martian/app/routers/admin.py) — New Endpoints
- `download_duckdb`: FileResponse streaming — correct for large files
- `download_portfolio`: Checks both volume and local paths — good fallback
- `upload_duckdb`: Uses temp file + atomic `shutil.move` — safe against partial uploads
- All endpoints require `get_admin_user` — properly protected
- **Verdict**: ✅ APPROVED

### [main.py](file:///home/terwu01/github/martian/app/main.py) — Debug Endpoint
- Now imports `DB_PATH` from `market_db` — eliminates path duplication
- **Verdict**: ✅ APPROVED

## Overall: ✅ ALL CHANGES APPROVED FOR MERGE
