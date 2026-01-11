# Task: Build Stock Analysis App

## 1. 👔 Product Manager (Vision & Market)
- [ ] **Vision Definition**
    - [ ] Define "Martian Investment System" core value proposition.
    - [ ] Identify target user persona (Quantitative Investor).

## 2. 📅 Project Leader (Timeline & Resources)
- [ ] **Project Management**
    - [x] track overall project timeline. (Sync-up 2026-01-12)
    - [ ] Coordinate handoffs between agents (e.g., Coder -> Verify).

## 3. 🧠 SPEC Manager (You)
- [x] **Project Initialization**
    - [x] Analyze existing codebase (`main_async_httpx.py`, `run_all.py`).
    - [x] Create `implementation_plan.md`.
    - [x] Define Agent Roles & Responsibilities.
- [/] **Spec Definition**
    - [x] Define Data Layer Specs (Crawler/Normalizer).
    - [x] Define Strategy Specs (Mars/CB).
    - [x] Define UI/UX Specs for "Bar Chart Race". ([Spec Link](specs/bar_chart_race.md))
    - [x] Review & Approve "Full Pipeline" methodology. ([Spec Link](specs/data_pipeline.md))

## 4. 🎨 UI Manager (Experience)
- [x] **Infrastructure**
    - [x] Initialize Vite + React Project (`frontend/`). (Verified: npm run dev works).
    - [x] **Pivot 1**: Adopt Streamlit for Python-native Dashboard. (Completed).
    - [x] **Pivot 2**: **Web Based UI** (No-Build).
- [ ] **Implementation**
    - [x] **Task**: Update `app/main.py` to serve `/static`. (Verified: curl 200).
    - [x] **Task**: Create `app/static/index.html` (Cyberpunk Shell). (Verified: Vue/Tailwind injected).
    - [x] **Task**: Implement features in `app/static/js/app.js` (Vue 3). (Verified: API logic robust).
    - [x] **Task**: **Interactive Simulation**: Add "MoneyCome-style" inputs (Principal/Contrib) and logic. (Verified: Vue.js Logic).
    - [x] **Task**: Implement GM Admin Dashboard. (Complete: `/admin` page + API)

## 5. 💻 Main Coder (Implementation)
- [x] **Core Infrastructure**
    - [x] Setup Python Environment & Dependencies.
    - [x] Implement TWSE Crawler (`project_tw/crawler.py`).
    - [x] Implement TPEX Crawler (`project_tw/crawler_tpex.py`).
- [x] **Data Pipeline**
    - [x] **Task**: Run `run_analysis.py` to generate full `stock_list.csv`.
    - [x] **Task**: Implement API Endpoints in `app/main.py`.
    - [x] **Task**: Create `ROICalculator` class for shared logic.
    - [x] **Task**: Implement CB Strategy Crawler & Logic (`project_tw/strategies/cb.py`). (Verified: Retrieves Prices + Static Info correctly).
    - [x] **Task**: Implement Admin API endpoints (`/api/admin/metrics`). (Complete)

## 6. 🔍 Verification Agent (Quality)
- [ ] **Verification**
    - [x] Verify TPEX Dividend Crawler (Output JSON checked).
    - [x] **Test**: Verify `stock_list.csv` format and column logic. (Note: Legacy `bah`/`bal` cols missing due to different data source; ROI varies by ~5% for high-div stocks).
    - [x] **Test**: Verify UI "Bar Chart Race" performance (Smoothness). (Verified: Plotly Animation Frame).
    - [x] **Quality**: Review Codebase for OOP standards. (Certified: Clean Class Structure in Strategies).
    - [x] **Quality**: Verify full pipeline with `verify_roi_correlation.py` (Corr: 0.94).
    - [x] **Deployment**: Verify `uv` migration and startup scripts.
    - [ ] **Security**: Verify Admin API is protected.
