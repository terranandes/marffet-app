# Code Review (2026-02-17 v3)

**Author**: [CV]
**Sprint**: Mars Strategy Final Polish & Export Optimization

## 1. Summary of Changes
- **`app/main.py`**:
    - Optimized `@app.get("/api/export/excel")` to reuse `SIM_CACHE` and use fast bulk analysis.
    - Optimized `@app.get("/api/race-data")` to reuse `SIM_CACHE` and use fast bulk analysis.
- **`app/services/strategy_service.py`**:
    - Fixed `valid_lasting_years` logic to count distinct years instead of daily price rows.
- **`scripts/cron/nightly_full_supplement.py`**:
    - Changed `period` from `1d` to `2d` for a one-day safety buffer.

## 2. Review Findings
- **Performance**: The export and BCR endpoints are now O(1) if cached, or O(12s) if not. This is a massive improvement over the previous 5-minute loop which was certain to time out on Zeabur.
- **Accuracy**: TSMC detail modal now correctly shows 21 years (from simulated history) instead of the bogus 4923 row count.
- **Reliability**: `period=2d` in cron is a best practice for nightly jobs to handle intermittent connectivity/server downtime without missing data.

## 3. Approval Status
- **Result**: ✅ APPROVED
- **Next Steps**: Deployment-ready.
