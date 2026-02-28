# Martian Investment System - Software Stack
**Version**: 3.1
**Date**: 2026-02-28
**Owner**: [PL][CODE][UI]

## 1. Frontend Layer (New)
**"The Cyberpunk Visualizer"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | Next.js 16 (React 18) | App Router, Server Actions |
| Runtime | **Bun** | Ultra-fast JS Runtime & Bundler |
| Styling | TailwindCSS | Cyberpunk theme (Cyan/Gold/Zinc-950) |
| Fonts | Inter (Google) | Clean, modern |
| Visualization | ECharts for React | Bar Chart Race, Trend Lines, Donut |
| Animations | **Framer Motion** | Collapsible sections, tab transitions |
| Notifications | **react-hot-toast** | System-wide toast notifications |
| State | React useState/useContext | Lightweight |
| Auth | Guest Mode + Google OAuth | `/auth/guest` endpoint |

## 2. Backend Layer
**"The Mathematical Core"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | FastAPI (Python 3.12) | Async, Auto-Swagger |
| Package Manager | **uv** | Ultra-fast Python package installer |
| Data Processing | Pandas | Simulation, Excel I/O |
| Authentication | Authlib + Starlette | OAuth 2.0 (Google) + Guest Mode |
| Database | DuckDB + SQLite | **DuckDB (Market Data Lake)** + SQLite (User Data) |
| Persistence | Zeabur Persistent Volume | [Read Architecture Spec](./duckdb_architecture.md) |
| Data Crawler | AsyncIO + yfinance | Nightly Full Supplement (`period=2d`) |
| Data Pipeline | Python, Pandas, Asyncio, HTTPX | **[Data Pipeline Architecture](./data_pipeline.md)** |
| External API | TWSE (MI_INDEX), TPEx | Stock Name Resolution & Verification |
| Pre-warm | APScheduler | Annual auto-rebuild + push |

## 3. Legacy UI Layer (RETIRED)
**"Fully migrated to Next.js. Legacy code removed."**

> Legacy Vue.js 3 UI has been fully replaced by the Next.js frontend.
> All legacy static files have been cleaned up.

## 4. DevOps & Automation

| Category | Technology | Notes |
|----------|------------|-------|
| Containerization | Docker | Multi-stage builds |
| E2E Testing | Playwright MCP | Headless browser automation |
| CI/CD | Zeabur | Auto-deploy on git push |

## 5. UI Alignment Status ✅

| Feature | Legacy UI | New Frontend | Status |
|---------|-----------|--------------|--------|
| Mars Strategy | ✅ | ✅ | Aligned |
| Bar Chart Race | ✅ | ✅ | Aligned |
| CB Strategy | ✅ | ✅ | Aligned |
| Portfolio | ✅ | ✅ | Aligned |
| Admin Dashboard | ✅ | ✅ | Aligned |
| Guest Mode | ✅ | ✅ | **NEW** (2026-01-18) |
| System Operations | ✅ | ✅ | Aligned |

## 6. Key Files

| Path | Purpose |
|------|---------|
| `app/main.py` | Backend API + simulation engine |
| `app/auth.py` | OAuth + Guest mode endpoints |
| `app/static/main.js` | Legacy UI Vue app |
| `app/static/index.html` | Legacy UI template |
| `frontend/src/app/` | Next.js pages |
| `frontend/src/components/Sidebar.tsx` | Navigation + auth UI |
