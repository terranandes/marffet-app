# Martian Investment System - Software Stack
**Version**: 2.3
**Date**: 2026-01-31
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
| Database | SQLite + JSON | Zero-maintenance, **Auto-Backup to GitHub** |
| Persistence | Git Backup Loop | [Read Architecture Spec](./backup_restore.md) |
| Data Crawler | AsyncIO + HTTPX | **[Crawler Architecture](./crawler_architecture.md)** |
| Data Pipeline | Python, Pandas, Asyncio, HTTPX | **[Data Pipeline Architecture](./data_pipeline.md)** |
| External API | TWSE (MI_INDEX), TPEx | Stock Name Resolution & Verification |
| Pre-warm | APScheduler | Annual auto-rebuild + push |

## 3. Legacy UI Layer
**"The Original Interface"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | Vue.js 3 (CDN) | Embedded in backend static |
| Visualization | D3.js, Plotly.js | Bar Chart Race, Detail Charts |
| Styling | TailwindCSS (CDN) | Same cyberpunk theme |
| System Ops | Admin Dashboard | Crawler, Backup, Pre-warm buttons |

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
