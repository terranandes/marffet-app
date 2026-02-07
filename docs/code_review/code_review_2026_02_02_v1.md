# Code Review - 2026-02-02

**Reviewer**: [CV] Code Verification Manager
**Scope**: Mars Strategy Revamp (Phase 1)
**Files**: `app/main.py`, `app/project_tw/calculator.py`, `frontend/src/app/mars/page.tsx`

## 1. Summary
The implementation is logically sound and follows the clean-room approach defined in the Spec. The separation of the new `ROICalculator` logic from the legacy `run_mars_simulation` is a good architectural decision, preventing regression in the main table while allowing experimentation in the modal.

## 2. Findings

### `app/main.py`
- **[INFO]** `/api/results/detail`: Good use of `sanitize_for_json`. This prevents the "500 Internal Server Error" often caused by Pandas/NumPy `NaN` or `Infinite` values.
- **[WARNING]** **IO Performance**: The loop `for year in range(start, end): open(json_file)` is inefficient.
    - *Impact*: For a 20-year simulation, this opens 40 files (Market + TPEx).
    - *Mitigation*: Acceptable for a single "Detail View" click (User waits ~1-2s).
    - *Long Term*: Must move to a unified Data Lake (Phase 2).

### `app/project_tw/calculator.py`
- **[PASS]** `calculate_complex_simulation`: The logic correctly isolates `open` vs `close` vs `high` vs `low`.
- **[PASS]** **Dividend Handling**: The logic `div_info.get(str(year)) or div_info.get(year)` handles the messy Key types (String vs Int) in the JSON database well.
- **[NOTE]** High/Low Fallback:
    ```python
    if yearly_action_prices.max() == 0:
        yearly_action_prices = df.groupby('year')['close'].max()
    ```
    This fallback is necessary because our data lacks High/Low, but it effectively disables the "Buy At Lowest" strategy (making it "Buy At Close"). This is a Data Defect, not a Code Defect.

### `frontend/src/app/mars/page.tsx`
- **[PASS]** State Management: Moving `useEffect` after `sim` declaration fixed the `ReferenceError`.
- **[PASS]** UI: Standard table layout used.

## 3. Verdict
**APPROVED**. The code is safe to merge/deploy for testing. The Data Lake upgrade is the blocking factor for full feature realiztion.
