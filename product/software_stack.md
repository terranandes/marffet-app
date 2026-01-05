# Software Perspective & Stack

## 1. Architecture: Monolithic Web Service
The application uses a **monolithic architecture** where the Backend serves both the API and the Static Frontend files. This simplifies deployment to a single container/host.

### 1.1 Directory Structure
```
/app
  /main.py            # Entry point, API Routes, Static File Mounting
  /portfolio_db.py    # Database Access Layer (DAL)
  /auth.py            # JWT Authentication & Password Hashing
  /static/            # Frontend Assets
    index.html        # SPA Entry Point
    main.js           # Vue.js Application Logic
    style.css         # Custom Styles
    /vendor/          # Local copies of libraries (Vue, Tailwind, D3)
```

## 2. Key Components

### 2.1 Backend (FastAPI)
-   **Session Management**: Uses `Starlette` SessionMiddleware for secure, encrypted cookie-based sessions.
-   **Async I/O**: Leveraging `async def` for non-blocking database and API calls.
-   **Static Mounting**: `app.mount("/static", ...)` serves the UI directly.

### 2.2 Frontend (Vue 3 ESM)
-   **No-Build Setup**: Uses native ES Modules (`<script type="module">`). No Webpack/Vite build step required for development, making it extremely lightweight.
-   **Reactivity**: Vue 3 Composition API (`ref`, `computed`) manages state.
-   **Routing**: Simple hash-based visibility toggles (`v-if="currentTab === 'mars'"`) simulate routing in this SPA.

## 3. Deployment Strategy
-   **Platform**: PaaS (Render, Zeabur, or Heroku).
-   **Build Command**: `pip install -r requirements.txt`
-   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
-   **Environment Variables**:
    -   `GEMINI_API_KEY`: For AI features.
    -   `SECRET_KEY`: For session encryption.
