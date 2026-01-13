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

### 2.2 New Tables (Premium Features)
-   **Notifications**:
    -   `id`: Primary Key
    -   `user_id`: Foreign Key (Users)
    -   `type`: Enum (GRAVITY, SIZE, YIELD)
    -   `title`: String (e.g., "Gravity Alert: NVDA")
    -   `message`: String (e.g., "Price deviates > 20%...")
    -   `is_read`: Boolean (Default: False)
    -   `created_at`: Timestamp

### 3.3 Premium Backend Engines (The "Ruthless Manager")
**Logic**: A background background job (cron or loop) runs periodically (e.g., every hour) to scan all Premium Portfolios.
**Global Safeguard**: To prevent "Nagging", the engine checks the `Notifications` table before sending.
   - **Rule**: Do NOT create a new notification if one exists for the same `user_id`, `type`, and `target_id` within the last **24 hours**.

1.  **Gravity Alert**:
    -   Trigger: $Price > 1.2 \times SMA_{250}$ (Sell Signal) OR $Price < 0.8 \times SMA_{250}$ (Buy Signal).
2.  **Size Authority**:
    -   Trigger: $MarketCap > 1.2 \times AvgPortfolioCap$ (Overweight) OR $MarketCap < 0.8 \times AvgPortfolioCap$ (Underweight).
3.  **Yield Hunter**:
    -   Trigger: $Premium < -1.0$ (Buy) OR $Premium \ge 30.0$ (Sell).

### 3.4 API Interface (Notifications) & Export
-   `GET /api/notifications`: Fetch active alerts (lazy trigger).
-   `POST /api/notifications/{id}/read`: Mark alert as read.
-   `GET /api/export/excel`: Dynamic Excel generation with simulation params (`start_year`, `principal`, `contribution`).
    -   **Polling Strategy**: Frontend polls this endpoint every 60 seconds.

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
