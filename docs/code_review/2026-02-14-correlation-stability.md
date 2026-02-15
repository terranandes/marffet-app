# Code Review: Correlation Stability & Nominal Data Handling
**Date**: 2026-02-14
**Reviewer**: [CV] Agent

## 🔍 Scope
Review of changes related to dividend re-import (`reimport_twse_dividends.py`) and price restoration (`restore_nominal_prices.py`).

## 📋 Findings

### 1. `app/project_tw/crawler.py`
- **Good**: Added logic to skip the ambiguous 'Combined' (權息) string which was the source of the 100x dividend inflation.
- **Improvement**: Error handling in `derive_stock_rate` should log a WARNING rather than just returning 0, as missing stock dividends affect split detection.

### 2. `scripts/ops/reimport_twse_dividends.py`
- **Good**: Systematic 30% yield threshold protects against future crawler hallucinations.
- **Good**: Transaction-based DB insertion prevents half-populated tables.

### 3. `app/services/market_data_provider.py`
- **Risk**: Missing a "Basis Awareness" flag. The provider assumes the user knows if the data is nominal or adjusted.
- **Recommendation**: Add a method `is_basis_nominal(stock_id)` that compares the first price in DuckDB vs the 2006 nominal anchor.

## ✅ Conclusion
The code is robust enough to handle the 'Nominal Reset'. The primary risk is the data ingestion source (TWSE rate limits), not the processing logic.

**Status**: PASS with recommendations.
