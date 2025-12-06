# Implementation Plan - Stock Analysis App

## Goal Description
Transform the existing scripts (`main_async_httpx.py`, `pandas_stock.py`) into a robust, object-oriented Web Application.
Key objectives from README:
-   **Visualization**: Implement **Bar Chart Race** to visualize stock ROI over time.
-   **Refactoring**: Convert functional scripts into **OOP** classes for better maintainability.
-   **Scalability**: Prepare a shared package structure to support future `project_usa` and `project_cn`.
-   **Performance**: Optimize crawler (AsyncIO is done, investigate local multiprocessing for calculations).

## User Review Required
> [!IMPORTANT]
> **Technology Stack Choice**: Use `notify_user` to confirm your preference.
> *   **Option A: Modern Web App (Recommended)**
>     *   **Backend**: Python (FastAPI) - Robust, easy to integrate with async crawler.
>     *   **Frontend**: React (Vite) - Essential for high-performance animations like "Bar Chart Race".
>     *   **Pros**: Premium feel, highly interactive, future-proof.
> *   **Option B: Data Dashboard**
>     *   **Stack**: Streamlit.
>     *   **Pros**: Quick to write.
>     *   **Cons**: Limited animation control (Bar Chart Race might be laggy or static).

## Proposed Changes

### Core Logic (Refactoring)
### Core Logic (Refactoring & Strategies)
#### [NEW] `project_tw/crawler.py`
-   **Class**: `TWSECrawler`
    -   Fetch **Stock Prices** (TWSE).
    -   Fetch **Convertible Bond (CB)** Data (likely from TPEX/OTC).
    -   Fetch **Dividend** Data.
    -   *Optimization*: Cache data to `data/raw/` to minimize external requests.

#### [NEW] `project_tw/strategies/mars.py`
-   **Goal**: "Mars Investment Method" - Safe, low-volatility asset growth.
-   **Logic**:
    1.  **Metric**: Calculate `Annualized ROI` + `Standard Deviation` (Volatility).
    2.  **Filter (Legacy)**: Use the existing logic from `pandas_stock.py` (`std_grd` threshold).
    3.  **Selection**: Pick Top 50 stocks with the best "Return per Unit of Risk" (or simple filtering).
    4.  **Signal**: Alert when a held stock's volatility exceeds `std_grd` or drops out of the Top 50.

#### [NEW] `project_tw/strategies/cb.py`
-   **Goal**: "CB Tracking" - Arbitrage & Hedging signals.
-   **Key Metric**: `Conversion Premium Rate` (I2).
-   **Logic (per User Rules)**:
    -   `I2 < -1%`: **Action**: "Buy CB, Sell Stock" (Arbitrage Alert).
    -   `I2 < 3.5%`: **Action**: "Consider Buy CB" (Best Entry).
    -   `I2 < 7%`: **Action**: "Hold" (Neutral).
    -   `I2 < 15%`: **Action**: "Consider Sell CB" (Check Confidence).
    -   `I2 < 30%`: **Action**: "Sell CB, Buy Stock" (Opportunity Cost High).
    -   `I2 >= 30%`: **Action**: "Immediately Sell CB" (Realize Profits).

#### [NEW] `project_tw/calculator.py`
-   **Class**: `ROICalculator`
    -   Shared utility for calculating ROI and Volatility for the `MarsStrategy`.

### Backend Application (FastAPI)
#### [NEW] `app/main.py`
-   **Endpoints**:
    -   `GET /api/mars/portfolio`: Returns current "Mars 50" list.
    -   `GET /api/mars/rebalance`: Returns recommended swaps (Sell X, Buy Y).
    -   `GET /api/cb/watchlist`: Returns tracked CB stocks.
    -   `POST /api/cb/notify`: Triggers check for CB signals.
    -   `GET /api/data/race`: Visuals.

### Frontend Application
#### [NEW] `frontend/`
-   **Framework**: React + Vite + TailwindCSS.
-   **Charts**: Use `echarts` or `d3.js` for the Bar Chart Race (it needs smooth interpolation).
-   **Dashboard**:
    -   Configuration Panel (Start/End Year, Capital).
    -   Real-time Crawler Status Log.

## Verification Plan

### Automated Tests
-   **Unit Tests**: Test the new `Crawler` class methods in isolation.
-   **Integration Tests**: Run a short 1-year crawl for a small stock subset and verify CSV output format.

### Manual Verification
-   **Visual Check**: Build the React app and inspect the Bar Chart Race animation smoothness.
-   **Data Validation**: Compare `stock_list.csv` output from the new App vs the old script.
