# BUG-115-PL: YFinance Adjusted Dividend Data Mismatch

## Issue Description
YFinance `actions` API (used for KY/DR stocks and emergency reloads like 9958) returns **split-adjusted dividends**, not nominal dividends.
Our system uses **nominal (unadjusted) prices** from MI_INDEX.
The combination of Adjusted Dividends + Nominal Prices leads to **incorrect Wealth Calculation** (overstatement).

## Impact
- **Severity**: 🔴 High
- **Affected Stocks**: ~90 KY/DR stocks (using `generate_ky_patches.py`) + any manually reloaded stocks (using `reload_9958.py`).
- **Example**: 9958 (Century Iron)
    - 2010 Dividend (Nominal): 0.5 Cash, 1.05 Split
    - YFinance Reports: 0.0888 Cash (Adjusted by 1.05 * 1.04143 * 1.02 * ...)
    - Result: Wealth calculation uses 0.0888 on a nominal price, severely underestimating early dividends, but potentially overestimating later ones if splits are double-counted or ratios are wrong.
    - **Wait**: If YFinance gives 0.0888 and we use Nominal Price, we UNDER-estimate yield.
    - **Correction**: 9958 Wealth was 2.3x HIGHER than MoneyCome.
    - **Hypothesis**: The "Splits" from YFinance might be interacting with our `SplitDetector` or `ROICalculator` in a way that compounds wealth incorrectly. Or, YFinance "Stock Splits" column returns Ratio (e.g. 1.05), but our system expects Stock Dividend (e.g. 0.5).
    - **Check**: `reload_9958.py` output:
      ```
      2010-09-13: Stock Splits = 1.05000
      ```
      Our text parser converts `1.05` -> `(1.05-1)*10` = `0.5` Stock Dividend. **This is Correct.**
      But the CASH dividend `0.0888` is adjusted. Real cash was likely `0.5`?
      If real cash was 0.5 and we use 0.0888, we lose wealth.
      So why is 9958 wealth HIGHER?
      **Answer**: The 2023 "False Split" (Price 181->97).
      We fixed the price history.
      But for KY stocks, we rely on YFinance dividends.

## Status
- [x] Identified
- [ ] Solutions Proposed:
    1. Multiply YFinance dividends by cumulative split ratio.
    2. Use TWSE/Goodinfo if available (even for KY?).
    3. Manual patch.

## Owner
[CODE]
