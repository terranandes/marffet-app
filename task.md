# Task: Build Stock Analysis App

## Phase 1: Planning and Architecture
- [/] Analyze existing code and data flow <!-- id: 0 -->
    - [x] Analyze `main_async_httpx.py` (Old Crawler - `moneycome.in`)
    - [x] Analyze `run_all.py` (Pipeline Driver)
    - [x] Analyze `pandas_stock.py` (Data Filtering)
    - [x] Analyze `README` (Project Goals)
- [x] Research & Design New Crawler (TWSE) <!-- id: 1 -->
    - [x] Research TWSE Data Endpoints (ROI vs Raw Price)
    - [x] Design Data Normalization Layer (TWSE -> Native Format)
    - [x] Updates to calculator logic (if raw data only)
- [ ] Define Application Requirements <!-- id: 2 -->
    - [ ] Confirm Web App vs Dashboard (Pending User Feedback)
    - [x] Requirement: Bar Chart Race Visualization
    - [x] Requirement: OOP Refactoring
    - [x] Requirement: Support for future `project_usa`/`project_cn`
- [x] Create Technical Design Document (`implementation_plan.md`) <!-- id: 2 -->
    - [x] Propose Tech Stack (Switched to Streamlit Dashboard)
    - [x] Design OOP Class Structure for Crawler
    - [x] Design "Shared Package" architecture
    - [x] Design "Mars" Strategy Module (Volatility & Rebalancing)
    - [x] Design "CB" Strategy Module (Bond Data & Notifications)

## Phase 2: Implementation
- [x] **Infrastructure & Core**
    - [x] Setup Project Structure (Streamlit Prototype Done)
    - [x] Implement TWSE Crawler (Price & Dividend)
    - [x] Implement CB Strategy Logic (User Rules)
    - [x] Clean up legacy files
- [x] **UI Layer (Web App Upgrade)**
    - [x] **Frontend**: Initialize Vite + React Project
    - [x] **Frontend**: Implement Mars Dashboard (Table & API)
    - [x] **Frontend**: Implement CB Calculator Component
    - [x] **Frontend**: Integrate Plotly.js for Bar Chart Race
- [ ] **Data & Automation (Next)**
    - [ ] **Mars Batch Integration**: Connect Dashboard to `stock_list` to analyze *all* stocks.
    - [ ] **CB Automation**: Crawl TPEX for real-time bond prices.
