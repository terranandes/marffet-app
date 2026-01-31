# Product Code Review: Martian Investment System
**Date:** 2026-01-31
**Reviewer:** [PL] via Orchestration Team ([SPEC], [CODE], [CV])
**Version:** 2.1 (Post-Migration)

## 1. Executive Summary
The system has successfully migrated to a decoupled **FastAPI + Next.js** architecture deploying on **Zeabur**. 
- **Stability**: High. Core simulation logic is robust.
- **Security**: Medium-High. OAuth 2.0 and CORS are correctly implemented, but some hardcoded failures exist as safety nets.
- **Completeness**: High. All "Legacy" features (Race, Trend, BCR) are ported.

---

## 2. Architecture Review ([SPEC])
**Status: Compliant with `product/specifications.md` (v2.1)**

### ✅ Strengths
1.  **Decoupling**: The API (`martian-api`) is cleanly separated from the UI (`martian-app`).
2.  **Containerization**: `Dockerfile` and `frontend/Dockerfile` are correctly set up for Zeabur.
3.  **Dynamic Data**: The new `StockInfoService` (O(1) fetch) aligns with the requirement to remove static Excel dependencies.

### ⚠️ Observations
1.  **Frontend URL Source**: `app/main.py` explicitly hardcodes `https://martian-app.zeabur.app` in `ALLOWED_ORIGINS` as a fallback. While safe, it implies a dependency on that specific Zeabur domain.
    *   *Recommendation*: Ensure `FRONTEND_URL` env var is always set in Zeabur to avoid reliance on hardcoded fallbacks.

---

## 3. Code Quality Review ([CODE])

### ✅ Improvements
1.  **pandas Optimization**: `run_analysis.py` and `StockInfoService` effectively use `pandas` for bulk data handling.
2.  **Caching**: The `SIM_CACHE` in `main.py` prevents re-calculating the same simulation parameters repeatedly.
3.  **Modular Services**: `CrawlerService` and `StockInfoService` are well-isolated.

### 🔧 Code Smells & Tech Debt
1.  **Hardcoded Data**: `app/main.py` contains a `DIVIDENDS_DB` dictionary with hardcoded values (e.g., TSMC dividends).
    *   *Risk*: If `dividends_all.json` fails to load, this data is stale.
    *   *Fix*: Move this to a `defaults.py` or ensuring the JSON loader is robust.
2.  **Global Simulation Cache**: `SIM_CACHE` is a global dictionary in `main.py`.
    *   *Scaling*: This will not work if we scale to multiple API replicas (Zeabur Horizontal Scaling).
    *   *Fix*: Future migration to Redis if traffic increases.
3.  **Logging**: `StockInfoService` uses `print()` instead of the standard `logging` module.
    *   *Fix*: Standardize on `logging.getLogger("app")`.

---

## 4. Security & QA Review ([CV])

### 🛡️ Security
1.  **CORS**: `ALLOWED_ORIGINS` is restrictive (good).
2.  **Input Sanitization**: `pd.read_html` via `StockInfoService` now uses `io.StringIO` and explicit headers, mitigating some injection/parsing risks.
3.  **Dependency**: `lxml` was just added. Ensure it is pinned in `pyproject.toml` (It is).

### 🧪 Test Coverage
1.  **Unit Tests**: `tests/verify_quarter_logic.py` verifies the date logic.
2.  **Integration**: `scripts/test_fetch_names.py` verifies the connection.
3.  **Missing**: Automated tests for `CrawlerService` (Mocking the filesystem/requests).

---

## 5. Action Items (Prioritized)

| Priority | Task | Responsibility |
| :--- | :--- | :--- |
| **P1** | **Standardize Logging** | Replace `print()` with `logger` in `app/services/` |
| **P2** | **Refactor Hardcoded Data** | Move `DIVIDENDS_DB` out of `main.py` |
| **P3** | **Redis Caching** | Plan for Redis cache for `SIM_CACHE` (Optional for now) |
| **P4** | **Test Coverage** | Add `pytest` for `CrawlerService` mocking |

**Verdict: Approved for Production (v2.1). Minor refactoring recommended for v2.2.**
