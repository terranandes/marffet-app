# MoneyCome Methodology & Verification

## Objective
The goal is to replicate the ROI (Return on Investment) simulation logic provided by the popular Taiwanese site **MoneyCome.in**. This serves as our "Golden Master" for verifying the accuracy of our backtesting engine.

## Core Logic (Re-Engineered from MoneyCome Notes — Verified 2026-02-18)

> Source: MoneyCome.in comparison mode (BAO) tooltip notes

### 1. Simulation Parameters
- **Principal**: Initial lump sum investment (e.g., 1,000,000 TWD).
- **Annual Contribution**: Yearly addition to capital (e.g., 60,000 TWD).
- **Dividend Policy**: **100% Reinvestment**. All cash dividends are used to buy more shares.
- **Timeframe**: Typically 2006 - Present (20 years).
- **Capital Reduction**: **NOT considered** (暫不考慮減資所的影響).

### 2. Execution Steps (Per Year)

**Order of operations is CRITICAL:**

1. **Apply Stock Splits** (if any occurred this year)
   - Existing shares multiply by split ratio to preserve value.

2. **Calculate & Reinvest Dividends** (去年留倉部位)
   - Cash dividends are calculated based on **last year's remaining position** (shares held BEFORE this year's new investment).
   - **Cash Dividend Reinvestment Price**: `當年均價` (Annual Average Close Price).
   - **Stock Dividend**: Added proportionally based on par value ($10 base).

3. **Invest Annual Capital**
   - **BAO mode (comparison)**: Buy at `當年第一個收盤價` (First Close of Year).
   - **Single mode**: User selects: First Close / Year High / Year Low.
   - Year 1: Principal + Annual Contribution.
   - Year 2+: Annual Contribution only.

4. **Valuation**: `Total Shares × Year End Close Price`.

### 3. Data Sources
- **Price History**: `daily_prices` (DuckDB). **Mandatory: 100% Nominal Basis**. Adjusted prices (TRI) are strictly forbidden as they cause "Double Adjustment" errors.
- **Dividends**: `dividends` (DuckDB). Nominal cash and stock dividends.

### 4. Verification Benchmark
**Target**: TSMC (2330)
- **Period**: 2006 - 2025
- **Validation**: Match MoneyCome BAO CAGR within ±1.5%.
- **Grand Correlation Target**: >85% match rate across ~1000+ valid stocks.

## Key Implementation Notes

### Dividend Timing (去年留倉部位 Rule)
```
❌ WRONG: Buy shares → Calculate dividends on ALL shares (including new)
✅ CORRECT: Calculate dividends on LAST YEAR's shares → Then buy new shares
```

This is documented directly in MoneyCome's tooltip:
> 每年領取的現金股利總金額以**去年留倉部位**進行計算

### Price Modes (Single vs Comparison)

| Mode | Annual Capital Buy Price | Dividend Reinvest Price |
|------|-----------|------------------------|
| BAO (comparison) | 當年第一個收盤價 (First Close) | 當年均價 (Annual Avg) |
| Single (bao/bah/bal) | First Close / Year High / Year Low | 當年均價 (Annual Avg) |
