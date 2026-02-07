
# 🕵️ Multi-Agent Code Review: Zeabur Crash Incident
**Date:** 2026-01-31
**Subject:** Socket Hang Up / `ECONNRESET` & Empty "My Race"
**Status:** 🔴 CRITICAL (Root Cause Found, Partial Fix Deployed)

---

## 1. 🚨 Incident Summary
User experienced "Socket Hang Up" errors and "Empty Data" on the Zeabur deployment. Logs revealed repeated logic failures for invalid stock ID `65331` and ETF `00937B`.

## 2. 🧠 Root Cause Analysis (RCA)
### The "Retry-Timeout" Death Spiral
1.  **Invalid ID (`65331`):** The system tried to fetch data for `65331`.
2.  **Naive Logic:** It tried `65331.TW` -> Failed (Cost ~2s). It then tried `65331.TWO` -> Failed (Cost ~2s).
3.  **No Memory:** The system did not *remember* this ID was invalid.
4.  **Amplification:** `My Race` and `Gravity Check` endpoints triggered this loop for *every user request* and *every background check*.
5.  **Result:** 30+ seconds of latency per request -> Zeabur Load Balancer killed the connection (`ECONNRESET`).

---

## 3. 🤖 Agent Findings

### 🔧 [BACKEND] Backend Specialist
**Finding 1: `update_price_cache` (Fixed)**
- The original code re-fetched specific IDs infinitely because it didn't check for alternate suffixes in the DB first.
- **Fix Deployed:** Added "Negative Caching" (Marker: `month='ERROR'`) and "Smart DB Lookup".

**Finding 2: `fetch_live_prices` (Still Vulnerable!)**
- Located in `app/portfolio_db.py`.
- **Issue:** It performs real-time YFinance fetches **without checking cache validity**.
- **Risk:** If `65331` is requested for a "Live Price" (e.g., Notification Engine), it will perform the same slow dual-fetch, potentially causing timeouts again.
- **Recommendation:** modifying `fetch_live_prices` to check `race_cache` for the `ERROR` marker before attempting YFinance.

**Finding 3: `engines.py` (Gravity Check)**
- Calls `fetch_live_prices` AND performs its own separate YFinance call for SMA250.
- **Optimization:** Should be consolidated.

### 🏛️ [DB] Database Architect
**Finding 1: Schema Usage**
- Storing `'ERROR'` in the `month` column (TEXT) is effective for immediate relief but violates Type Safety.
- **Recommendation:** Future Refactor -> Create a `stock_metadata` table:
  ```sql
  CREATE TABLE stock_metadata (
      stock_id TEXT PRIMARY KEY,
      alias_id TEXT, -- e.g. 00937B.TWO
      status TEXT, -- 'ACTIVE', 'INVALID', 'DELISTED'
      last_checked TIMESTAMP
  );
  ```

### 📋 [PL] Project Planner
**Finding 1: Testing Gap**
- Local tests used valid data or a subset of user data. We missed the `65331` edge case because we didn't mock "Bad Data".
- **Action:** Add a "Chaos Mode" to tests that injects invalid IDs.

---

## 4. ✅ Action Items

### Immediate (Hotfix)
- [x] **Fix `update_price_cache`**: Implemented Negative Caching for Historical Data. (DONE)
- [ ] **Fix `fetch_live_prices`**: Modify it to respect the "Negative Cache" (skip IDs marked ERROR).

### Short Term
- [ ] **Consolidate YF Logic**: Create a single `SmartFetcher` class that handles suffixes and caching validity.
- [ ] **Add "Bad Data" Test**: Create `tests/chaos_test.py`.

### Long Term
- [ ] **Migrate to `stock_metadata` table**.

---

## 5. 💡 Recommendation
**Approve Hotfix 2:** Update `fetch_live_prices` to check `race_cache` for `'ERROR'` before fetching. This ensures the Notification Engine doesn't crash the server.
