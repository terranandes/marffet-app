# Compound Simulator Tab — Feature Specification

**Date**: 2026-02-17
**Owner**: [SPEC] Agent
**Status**: Production

---

## 1. Overview

The **Compound Simulator** (`/compound`) lets users simulate the long-term wealth effect of a specific stock using three strategies: **BAO** (Buy At Open), **BAH** (Buy And Hold), and **BAL** (Buy At Low). It supports both **Single Stock** and **Comparison** (up to 3 stocks) modes.

---

## 2. Simulation Modes

### Single Stock Mode

- User enters a stock code (e.g., `2330`)
- Configures: start year, end year, principal, annual contribution
- Returns BAO / BAH / BAL results with yearly history

### Comparison Mode

- User enters up to 3 stock codes
- Same parameters applied to all stocks
- Side-by-side comparison of final wealth, ROI, and growth curves

---

## 3. Strategies

| Strategy | Logic                                                      |
|:-------- |:---------------------------------------------------------- |
| **BAO**  | Buy at the first trading day's **open** price each year    |
| **BAH**  | Buy and hold from day 1 — no additional contributions      |
| **BAL**  | Buy at the **lowest** price of the year (best-case timing) |

---

## 4. Frontend

**Route**: `/compound`
**File**: `frontend/src/app/compound/page.tsx` (520 lines)

### UI Components

1. **Mode Toggle** — Switch between Single / Comparison
2. **Parameter Panel** — Stock code(s), start year, end year, principal, contribution
3. **Results Cards** — Final Value, Total Cost for each strategy
4. **ECharts Line Chart** — Year-by-year growth of each strategy
   - X-axis: Year
   - Y-axis: Portfolio value (TWD)
   - Three lines for BAO/BAH/BAL (or per-stock in comparison mode)

### TypeScript Interfaces

```typescript
interface CompoundSettings {
    mode: "single" | "comparison";
    stockCode: string;
    stock1: string; stock2: string; stock3: string;
    startYear: number; endYear: number;
    principal: number; contribution: number;
}

interface HistoryPoint {
    year: number; value: number;
    dividend: number; invested: number;
    roi: number; cagr: number;
}
```

---

## 5. Backend API

| Method | Endpoint                     | Description                          |
|:------ |:---------------------------- |:------------------------------------ |
| `GET`  | `/api/results/detail`        | On-demand simulation for a stock     |

The Compound page reuses the **same** `/api/results/detail` endpoint as the Mars tab's detail modal. It calls:

```
GET /api/results/detail?stock_id={code}&start_year={sy}&principal={p}&contribution={c}
```

### Backend Logic

- **Service**: `app/project_tw/calculator.py` → `ROICalculator.calculate_complex_simulation()`
- **Data**: DuckDB `daily_prices` + `dividends` tables via `MarketDataProvider`
- **Cache**: Results cached in `SIM_CACHE` keyed by `(start_year, principal, contribution)`

---

## 6. Architecture

```
User Settings ──▶ /compound page
                      │
                      ├── Single Mode: 1× GET /api/results/detail
                      │
                      └── Comparison Mode: 3× GET /api/results/detail (parallel)
                                │
                                └── ROICalculator.calculate_complex_simulation()
                                        │
                                        ├── DuckDB: daily_prices
                                        └── DuckDB: dividends
```

---

## 7. Chart Library

- **ECharts** via `echarts-for-react` (dynamic import, SSR disabled)
- Renders interactive line charts with tooltip, legend, and zoom
