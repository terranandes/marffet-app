# Martian Investment System - Test Plan
**Version**: 2.1  
**Date**: 2026-01-16  
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We use **Playwright MCP** for End-to-End (E2E) verification.

### 1.1 Test Suite Location
- `tests/full_verification.py`

### 1.2 Test Cases

| ID | Feature | Description | Criteria |
|----|---------|-------------|----------|
| TC-01 | Landing | Home page loads | Title contains "Martian" |
| TC-02 | Mars Strategy | Simulation works | Stock table appears, rows > 0 |
| TC-03 | BCR | Bar Chart Race | Wealth/CAGR toggle works |
| TC-04 | Modal Data | Detail modal | Values match table |
| TC-05 | Year Range | History data | 21 years (2006-2026) |
| TC-06 | Dividend | Dividend chart | Non-zero values displayed |
| TC-07 | Top 50 | Table sorting | Shows max 50 rows |

### 1.3 Execution (Playwright MCP)
```bash
# Using Playwright MCP server for browser automation
# 1. Navigate to app
# 2. Click "Apply (Recalculate)"
# 3. Verify table has 50 rows
# 4. Click first stock row
# 5. Verify modal shows matching Final Value
# 6. Switch to Dividend tab
# 7. Verify chart shows non-zero data
```

## 2. Manual Verification Checklist

### Mars Strategy
- [x] Table sorts by Simulated Final (default)
- [x] Table sorts by CAGR when clicked
- [x] Volatility column has no sorting
- [x] Shows Top 50 only
- [x] Modal values match table

### BCR Tab
- [x] Wealth racing mode works
- [x] CAGR racing mode works
- [x] Top 50 performers shown

### Data Consistency
- [x] Year range: 2006-2026 (21 years)
- [x] Final Value: $502M for stock 2383
- [x] CAGR: 28.10% for stock 2383
- [x] Dividend chart shows actual data

## 3. Regression Tests (v2.1 Fixes)

| Test | Expected | Status |
|------|----------|--------|
| Race-data format | Flat `[{id, year, wealth}]` | ✅ |
| Modal data source | Pre-computed (no client sim) | ✅ |
| Year 2006 in history | First entry in wealth_trend | ✅ |
| Dividend in race-data | Non-null values | ✅ |
| sortedMarsList | Used by table v-for | ✅ |
