# Code Review Note (API Routing & Caching Fixes)
**Date:** 2026-02-27 17:45 HKT
**Reviewer:** [CV]

## 1. Changes Reviewed
- **`app/main.py` & `app/routers/portfolio.py` (`api_target_dividends`)**
  - *Bug:* The prior fix applied exclusively to `main.py` acted as dead code. FastAPI's `app.include_router(portfolio_router, prefix="/api/portfolio")` executed *before* the standalone route declarations, causing requests to be intercepted by the original, unmapped DB logic.
  - *Fix:* 
    1. Re-located the `ex_date` mapping translation loop definitively into `app/routers/portfolio.py`.
    2. Deleted the legacy and duplicate Portfolio route definitions hanging in `main.py` to prevent namespace shadowing.
    3. Injected strict `Cache-Control: no-store` headers via the `fastapi.Response` object.
  - *Status:* APPROVED. Router shadowing entirely eradicated.

- **`frontend/src/services/portfolioService.ts` (`getDividends`)**
  - *Bug:* Zeabur proxy networks / Next.js edge routers cached the old JSON response indiscriminately, masking the deployed API changes. 
  - *Fix:* Integrated a forced cache-busting query parameter `?_cb=${Date.now()}` appended to the GET request and explicitly enforced `cache: "no-store'` inside the JS native fetch configuration.
  - *Status:* APPROVED. Front-end cleanly bypasses staleness.

## 2. Verdict
- **Production Code:** APPROVED.
- **Data Integrity:** VERIFIED. Application deployment is sound and synchronized. No logic mutations outside bug boundaries.
