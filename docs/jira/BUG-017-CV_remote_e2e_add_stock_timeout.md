# BUG-017 — Remote E2E Add Stock Timeout

**Type:** BUG  
**Serial ID:** 017  
**Reporter:** `[CV]` (Antigravity)  

**Status:** ✅ CLOSED (2026-03-20) — Fixed in Phase 38 by converting Zeabur verification wait strategy from `networkidle` to `domcontentloaded`.

## 1. Issue Description
During remote Playwright E2E verification of `marffet-app.zeabur.app` (Desktop View), the test failed at `TEST 2: Add Stock`. The `+ Add Asset` button was clicked, but the resulting TSMC `2330` row was not visible within the 15000ms timeout window. 
This flaw did not appear on local tests against `localhost:3000` executing the same SWR caching refactor logic.

## 2. Steps to Reproduce
1. Execute `tests/e2e/e2e_suite.py` bound to the remote environment context (`TARGET_URL=https://marffet-app.zeabur.app`).
2. Login as Guest.
3. Add a new Group.
4. Attempt to add Ticker `2330` Name `TSMC` and click `+ Add Asset`.
5. Wait for the `2330` TR element to appear.
6. **Result:** Playwright crashes with `Error: Locator.wait_for: Timeout 15000ms exceeded`.

## 3. Potential Root Causes
*   **Latency vs. SWR Revalidation:** Adding a transaction/stock has a higher round-trip latency to the database on Zeabur than localhost. The local component state invalidation might take longer than Playwright expects.
*   **Mobile vs Desktop:** The mobile E2E test runs successfully with `Mobile Card is VISIBLE`. This points to a possible test script locator flake with `tr` or `visible=true` on the desktop view when rendered sequentially.

## 4. Workaround/Resolution
- Evaluate frontend API revalidation logic. `portfolioService.ts` currently forces an SWR mutation when a stock is added.
- Playwright's desktop locator may need a longer hardcoded timeout or a broader locator (e.g. `page.locator("text=TSMC")`).
