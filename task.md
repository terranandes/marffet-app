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
    - [x] Propose Tech Stack (Python Backend + React Frontend)
    - [x] Design OOP Class Structure for Crawler
    - [x] Design "Shared Package" architecture
    - [ ] Design "Mars" Strategy Module (Volatility & Rebalancing)
    - [ ] Design "CB" Strategy Module (Bond Data & Notifications)

## Phase 2: Implementation (TBD)
- [ ] **Infrastructure Layer**
    - [ ] Setup FastAPI + React Project Structure
    - [ ] Implement TWSE Crawler (Price & Dividend)
    - [ ] Implement CB/OTC Crawler (Bond Data)
- [ ] **Strategy Layer**
    - [ ] Implement `MarsStrategy` (StdDev Filter, Top 50 Selection)
    - [ ] Implement `CBStrategy` (Tracking Rules from Spreadsheet)
- [ ] **UI Layer**
    - [ ] Build "Mars" Portfolio Dashboard
    - [ ] Build "CB" Watchlist & Notification Settings
    - [ ] Build Bar Chart Race Visualization
