# Code Review Note (Bug Fixes)
**Date:** 2026-02-27 14:30 HKT
**Reviewer:** [CV]

## 1. Changes Reviewed
- **`app/main.py` (`api_target_dividends`)**
  - *Bug:* The endpoint previously forwarded raw DuckDB dictionary columns (`shares_held`, `total_cash`) identically to the frontend. However, `DividendHistoryModal.tsx` expected keys structured as `held_shares` and `amount`. This caused `total_cash` to evaluate as `undefined` array properties on the client, yielding `$NaN` currency formats.
  - *Fix:* Integrated a mapping loop inside `api_target_dividends` to convert DB schema keys to frontend-compliant keys (e.g. `d.get("total_cash", 0)` -> `"amount"`).
  - *Status:* APPROVED. Key mismatch eliminated.

- **`frontend/src/app/portfolio/components/TransactionFormModal.tsx`**
  - *Bug:* Native HTML5 `<input type="date">` rendered a dark-on-dark invisible calendar icon under Tailwind's `bg-black/50` styling because the browser had no `color-scheme` context.
  - *Fix:* Added `style={{ colorScheme: "dark" }}` directly to the `<input>` element to force Webkit/Blink styling engines to invert the calendar picker asset to white.
  - *Status:* APPROVED. Styling restored.

## 2. Verdict
- **Production Code:** APPROVED.
- **Data Integrity:** VERIFIED. Both fixes address critical UX blocks without altering mathematical foundations.
