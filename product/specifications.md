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
-   **Language**: Python 3.11+
-   **Framework**: FastAPI
-   **Database**: SQLite (with `app/portfolio_db.py` abstraction layer)
-   **AI Integration**: Google Generative AI (Gemini) SDK

### 3.2 Frontend
-   **Core**: HTML5, Vanilla JavaScript (ES Module-based)
-   **Framework**: Vue.js 3 (CDN/ESM build)
-   **Styling**: Tailwind CSS (CDN)
-   **Visualization**: Plotly.js (Charts), D3.js (Bar Chart Race)

## 4. MCP Integration (Tooling)
-   **Playwright**: For End-to-End UI testing.
-   **Chrome DevTools**: For deep browser inspection and console log analysis.
-   **Tavily**: For retrieving external financial news/data.
