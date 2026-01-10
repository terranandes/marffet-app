# Product Specifications

## 1. Data Privacy Model ("Competition without Exposure")

### 1.1 Private Data (Server-Side Only)
These fields are **NEVER** exposed via public APIs:
-   `transactions.shares` (Specific quantity of shares held)
-   `targets.initial_capital` (Total account size)
-   `users.email` (PII)

### 1.2 Public Data (Sanitized API)
The `GET /api/public/profile/{user_id}` endpoint exposes only relative metrics:
-   **ROI %**: `((Current Value - Cost Basis) / Cost Basis) * 100`
-   **Asset Allocation**: Percentage breakdown by Asset Class (e.g., 60% Stock, 40% Bond).
-   **Top Holdings**: List of Symbols (e.g., ["NVDA", "TSLA"]) sorted by weight, **without** share counts or values.

## 2. Database Schema (SQLite)

### 2.1 Tables
-   **Users**: `id`, `nickname`, `email`, `hashed_password`
-   **Groups**: `id`, `user_id`, `name` (Portfolio Groups)
-   **Targets**: `id`, `group_id`, `symbol`, `name`
-   **Transactions**: `id`, `target_id`, `type` (BUY/SELL), `shares`, `price`, `date`

## 3. Technology Stack

### 3.1 Backend
-   **Language**: Python 3.10+
-   **Framework**: FastAPI (AsyncIO)
-   **Database**: SQLite (managed via `app/portfolio_db.py`)
-   **Authentication**: Google OAuth 2.0 (via `authlib`)
-   **Data Source**:
    -   **TWSE/TPEx**: Daily price crawling via `project_tw` crawlers.
    -   **Cache**: JSON-based flat file cache (`data/raw/*.json`) for performance.
    -   **Golden Source**: `references/stock_list_s2006e2025_filtered.xlsx`.

### 3.2 Frontend
-   **Framework**: Vue.js 3 (ES Module Build / Composition API)
-   **Styling**: Tailwind CSS (CDN)
-   **Visualization**: Plotly.js (Wealth Charts)
-   **State Management**: Vue `ref`/`reactive` (Local State)

## 4. System Capabilities & Limitations

### 4.1 Data Integrity
-   **Coverage**: Supports TWSE (Mainboard) and TPEx (OTC) markets, including Bond ETFs.
-   **Verification**: Automated `verify_targets.py` script validates simulation data against the Golden Excel source.
-   **Latency**: Blocking AI operations are offloaded to threadpools to ensure non-blocking UI.

### 4.2 Known Constraints
-   **Google Auth**: Requires strict URI matching (`http://127.0.0.1:8000` vs `localhost`).
-   **Delisted Stocks**: Historical data for delisted stocks may be incomplete if not present in Yahoo Finance.
