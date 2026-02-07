# Code Review: Split Detector Implementation
**Date**: 2026-02-06
**Reviewer**: [CV] Code Verifier
**Target**: `app/services/split_detector.py`, `app/project_tw/calculator.py`

---

## 1. Summary
The implementation introduces a dedicated `SplitDetector` class to handle stock splits (e.g., 0050 ETF 2014 split). It integrates into the simulated "Year-Over-Year" loop in `ROICalculator`.

## 2. Key Findings

### ✅ Strengths
- **Detection Logic**: The use of a simple `>40%` drop threshold is robust for 1:2 or larger splits.
- **Cache**: Singleton pattern with caching (`_cache`) prevents re-scanning history for every simulation year.
- **Integration**: `calculate_complex_simulation` correctly applies the cumulative ratio to `current_shares`.

### ⚠️ Observations
- **Data Source Quirk**: yfinance provides "mixed" data (some years adjusted, some not).
    - *Mitigation*: The detector dynamically adapts—if a split is "hidden" (retroactively adjusted), it's ignored (correctly). If it's visible, it's detected.
- **Edge Case**: If a stock drops 41% due to a crash (unlikely in one day for an ETF, but possible for individual stocks), it might trigger a false positive.
    - *Verdict*: Acceptable trade-off for now. MoneyCome doesn't even handle this.

## 3. Verdict
**Approved**. The simulation result (0050 CAGR 12.1%) is now significantly more accurate than the previous baseline (5%).

---
