# Software Perspective & Stack

## 1. Architecture: Monolithic Web Service
The application uses a **monolithic architecture** where the Backend serves both the API and the Static Frontend files. This simplifies deployment to a single container/host.

### 1.1 Directory Structure
```bash
.
├── app/                    # Backend & Frontend Host (Active)
│   ├── main.py             # FastAPI Entry Point
│   ├── auth.py             # Google OAuth Logic
│   ├── portfolio_db.py     # Database Abstraction
│   └── static/             # Frontend (Vue.js SPA)
│       ├── index.html      # Entry Point
│       ├── main.js         # Vue App Logic
│       └── vendor/         # Local Dependencies (Vue, Tailwind)
├── project_tw/             # Data Crawlers (The "Fuel")
│   ├── crawler.py          # TWSE Crawler
│   ├── crawler_tpex.py     # TPEx (OTC) Crawler
│   └── strategies/         # Mars Strategy Logic
├── data/
│   └── raw/                # JSON Cache (Market_YYYY.json)
├── frontend/               # (Legacy) Output of previous build experiments
├── product/                # Documentation
└── requirements.txt        # Python Dependencies
```

## 2. Key Components

### 2.1 Backend (FastAPI)
-   **Session Management**: Uses `Starlette` SessionMiddleware for secure, encrypted cookie-based sessions.
-   **Excel Export**: `pandas` + `openpyxl` for generating `.xlsx` reports (Backend).
-   **Async I/O**: Leveraging `async def` for non-blocking database and API calls.
-   **Static Mounting**: `app.mount("/static", ...)` serves the UI directly.
### 2.2 Frontend (Vue 3 ESM)
-   **No-Build Setup**: Uses native ES Modules (`<script type="module">`). No Webpack/Vite build step required for development, making it extremely lightweight.
-   **Reactivity**: Vue 3 Composition API (`ref`, `computed`) manages state.
-   **Routing**: Simple hash-based visibility toggles (`v-if="currentTab === 'mars'"`) simulate routing in this SPA.
-   **Responsive Design**: Mobile-First approach using Tailwind CSS breakpoints (`lg:`).
    -   **Mobile**: Hamburger Menu, Stacked Layout.
    -   **Desktop**: Full Top Navigation, horizontal Layout.
-   **Notification System**: Integrated with Backend API. Includes Polling (60s), Badge UI, and Dropdown with "Mark as Read" actions.

### 2.3 Premium Engines
-   **Rebalancing Engine**: Background job running the "Ruthless Manager" logic (Gravity, Size, Yield checks).
-   **Notification System**: Internal messaging system to queue and deliver In-App alerts to Premium users.

## 2. Backend Stack (The "Engine")
-   **Framework**: FastAPI (Python 3.10+) 🐍
-   **Server**: Uvicorn (ASGI) for high-concurrency ⚡
-   **Database**: SQLite (`portfolio.db`) - Simple, serverless, file-based.
-   **Authentication**: standard Google OAuth 2.0 Flow.

## 3. Data Pipeline (The "Fuel")
-   **Crawlers**: Custom AsyncIO crawlers for TWSE and TPEx (`project_tw`).
-   **Cache Strategy**: 
    -   **Raw Data**: Stored as JSON chunks (`data/raw/Market_YYYY.json`) for bulk I/O efficiency.
    -   **Dividend DB**: `DIVIDENDS_DB` loaded into memory on startup for simulation speed.
-   **Verification**: Automated integrity checks against a "Golden Excel" source.

## 4. Deployment Strategy
-   **Platform**: PaaS (Render, Zeabur, or Heroku).
-   **Build Command**: `pip install -r requirements.txt`
-   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
-   **Environment Variables**:
    -   `GEMINI_API_KEY`: For AI features.
    -   `SECRET_KEY`: For session encryption.
