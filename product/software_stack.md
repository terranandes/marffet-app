# Martian Investment System - Software Stack
**Version**: 2.1  
**Date**: 2026-01-16  
**Owner**: [PL][CODE][UI]

## 1. Frontend Layer
**"The Cyberpunk Visualizer"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | Next.js 14 (React 18) | App Router, Server Actions |
| Styling | TailwindCSS | Cyberpunk theme (Cyan/Gold/Zinc-950) |
| Fonts | Inter (Google) | Clean, modern |
| Visualization | ECharts for React | Bar Chart Race, Trend Lines, Donut |
| State | React useState/useContext | Lightweight |

## 2. Backend Layer
**"The Mathematical Core"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | FastAPI (Python 3.12) | Async, Auto-Swagger |
| Data Processing | Pandas | Simulation, Excel I/O |
| Authentication | Authlib + Starlette | OAuth 2.0 (Google) |
| Database | SQLite + JSON | Zero-maintenance, **Auto-Backup to GitHub** |
| Persistence | Git Backup Loop | [Read Architecture Spec](./backup_restore.md) |

## 3. Legacy UI Layer
**"The Original Interface"**

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | Vue.js 3 (CDN) | Embedded in backend static |
| Visualization | D3.js, Plotly.js | Bar Chart Race, Detail Charts |
| Styling | TailwindCSS (CDN) | Same cyberpunk theme |

## 4. DevOps & Automation

| Category | Technology | Notes |
|----------|------------|-------|
| Containerization | Docker | Multi-stage builds |
| E2E Testing | Playwright | Python Sync API |
| CI/CD | Zeabur | Auto-deploy on git push |

## 5. Key Files
| Path | Purpose |
|------|---------|
| `app/main.py` | Backend API + simulation engine |
| `app/static/main.js` | Legacy UI Vue app |
| `app/static/index.html` | Legacy UI template |
| `frontend/src/app/` | Next.js pages |
