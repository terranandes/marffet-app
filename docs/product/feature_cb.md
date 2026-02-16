# Convertible Bond (CB) Tab — Feature Specification

**Date**: 2026-02-17
**Owner**: [SPEC] Agent
**Status**: Development (🚧)

---

## 1. Overview

The **CB Strategy** tab (`/cb`) provides convertible bond arbitrage analysis. It has two modes:

1. **My CB Portfolio** — Auto-analyzes all CBs in the user's portfolio
2. **CB Analyzer** — On-demand analysis of any CB by code

---

## 2. Core Logic

### Premium Rate Calculation

```
Premium (%) = ((CB Price ÷ (100 ÷ Conversion Price)) − Stock Price) ÷ Stock Price × 100
```

### Action Signals

| Premium      | Action       | Color  | Description                          |
|:------------ |:------------ |:------ |:------------------------------------ |
| < -5%        | `BUY`        | Green  | CB is undervalued vs underlying      |
| -5% to +10%  | `HOLD`       | Yellow | Fair value range                     |
| > +10%       | `SELL`       | Red    | CB is overvalued, consider selling   |
| N/A          | `NOT_FOUND`  | Gray   | Data unavailable                     |

---

## 3. Frontend

**Route**: `/cb`
**File**: `frontend/src/app/cb/page.tsx`

### UI Components

1. **My CB Portfolio** — Cards showing all CBs from the user's portfolio groups
   - Displays: code, name, stock price, CB price, conversion price, premium %, action signal
   - Color-coded border (green/yellow/red) based on action
   - Links to `/portfolio` if no CBs found

2. **CB Analyzer** — Input field + "Analyze" button
   - Enter a CB code (e.g., `66691`)
   - Returns real-time premium rate and action recommendation

---

## 4. Backend API

**Service**: `app/services/cb_strategy.py` (`CBStrategy` class)

| Method | Endpoint               | Auth      | Description                          |
|:------ |:---------------------- |:--------- |:------------------------------------ |
| `GET`  | `/api/cb/analyze?code=` | None     | Analyze a single CB by code          |
| `GET`  | `/api/cb/portfolio`    | Session   | Analyze all CBs in user's portfolio  |

### Data Sources

| Data Point        | Source                    |
|:----------------- |:------------------------- |
| CB Price          | TWSE/OTC API (real-time)  |
| Stock Price       | yfinance / TWSE API       |
| Conversion Price  | TWSE CB reference data    |

---

## 5. Architecture

```
User ──▶ /cb page
           │
           ├── GET /api/cb/portfolio ──▶ CBStrategy.analyze_specific_cbs()
           │                                │
           │                                ├── Fetch CB codes from portfolio.db
           │                                └── Scrape TWSE for live CB + stock prices
           │
           └── GET /api/cb/analyze?code=X ──▶ CBStrategy.analyze_list([X])
                                                └── Single CB analysis
```

---

## 6. Premium Feature: CB Notifications

> **Status**: Planned (not yet implemented)

- Email alerts when a CB's premium drops below a configurable threshold
- Requires Premium subscription tier
