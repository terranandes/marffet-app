# BUG-005-PL: Trend Chart Market Value Mismatch with Portfolio
**Reporter:** [PL]
**Component:** Backend (Portfolio Service - Trend)
**Severity:** Medium
**Status:** CLOSED

## Description
User reports that the final coordinate on the "Portfolio Trend" chart displays a Market Value of $93,983,073, whereas the "My Portfolio" dashboard Live Market Value shows $97,082,769. The Cost Basis on the tip of the Trend Chart is identical to the Portfolio Cost Basis ($36,626,440), proving that transaction parsing is correct. 

## Root Cause Hypothesis
The Portfolio tab actively fetches `livePrice` points for real-time intraday snapshots, whereas the `get_portfolio_trend` endpoint likely constructs its timeseries strictly out of historical `market.duckdb` EoD closing prices. Because the duckdb price is at least 1 day stale (or intraday updates haven't synced), the tip of the chart trails the live UI.

## Fix Strategy
In `get_portfolio_trend()`, when constructing the timeline, fetch the Live Market Prices (via cache or `yfinance`) and forcefully append "Today" to the timeline using the live values. Or, stitch the last datapoint.
