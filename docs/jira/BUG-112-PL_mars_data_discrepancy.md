# BUG-112: Mars Strategy ROI and Wealth Discrepancy
**Reporter:** [PL] Agent (Detected during Debugging)
**Date:** 2026-02-11
**Severity:** **High**
**Component:** Mars Strategy / Data Infrastructure

## Description
The Mars Strategy table on Zeabur and local runs showed incorrect ROI and Total Wealth for long-term simulations (e.g., 2006-2026). 
- **Symptoms**: Total Cost for TSMC (2330) was only 1.06M (reflecting only 1 year of contributions) despite a 20+ year request. ROI often showed "None" or extreme 1-year spikes.

## Root Cause
**Data Corruption/Truncation**: The historical market price files in `data/raw/Market_YYYY_Prices.json` for years 2000-2023 were incomplete. They contained only a small subset of stocks (~150) and were missing market leaders like TSMC (2330). This caused the simulation to "start" only in 2024 when the full universe data was available.

## Resolution
1. **Tool Creation**: Developed `scripts/ops/patch_stock_data.py` to perform targeted yfinance downloads and injection.
2. **Data Patching**: Successfully patched 27 years of daily data for 2330, 2317, 2454, and other key stocks into the JSON database.
3. **Verification**: `tests/analysis/debug_mars_vs_reference.py` now confirms 21-year simulation coverage for 2330.

## Corrected Metrics (TSMC 2330)
- **Total Cost**: ~2.26M (Fixed from 1.06M)
- **CAGR**: 19.1% (Fixed from 87.9% 1-year spike)

## Status: FIXED (Local)
**Pending**: Deployment of patched `data/raw/` files to Zeabur.
