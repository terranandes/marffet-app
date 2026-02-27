# BUG-118-PL: Portfolio Dividend Sync Returns Empty/NaN

**Reporter:** [PL]
**Component:** Frontend (Portfolio) & Backend (Dividend Sync / Calculation)
**Severity:** High
**Status:** OPEN

## Description
When the user goes to the Portfolio tab and clicks "Sync Dividends", the dividend receipt remains empty or displays `NaN` in the UI (specifically within the Dividend History modal and the Target list). Despite having valid transactions (e.g., buying 40,000 shares of TSMC in 2010), the dividend sync process fails to populate historical dividends, and the calculation engine yields `NaN` for total cash.

## Expected Behavior
Clicking "Sync Dividends" should fetch historical dividends for all held stocks, calculate the correct cash payout based on the holdings at the ex-dividend date, and display the total cash received along with a detailed history in the modal.

## Investigation Steps
1. Trace `api_sync_dividends` in `/api/portfolio/sync-dividends` to see if the yfinance dividend fetch or DuckDB update logic is failing.
2. Check `calculation_service.py` `get_target_summary` to see why the fallback or DB fetch returns values that lead to `NaN` on the frontend.
3. Review `DividendHistoryModal.tsx` and `TargetList.tsx` to verify exactly what backend response structure causes the `NaN` display (e.g., missing keys or `null` values returned).
