# Martian Investment System - Technical Specifications
**Version**: 2.3
**Date**: 2026-01-31
**Owner**: [SPEC] Agent

## 1. System Architecture
Decoupled Client-Server architecture for containerized deployment (Zeabur).

### 1.1 Components
| Component | Tech | Role | URL |
|-----------|------|------|-----|
| Backend | FastAPI (Python 3.12) | REST API, Auth, Simulation Engine | `martian-api.zeabur.app` |
| Frontend | Next.js 14+ | UI, Visualization (ECharts), SSR | `martian-app.zeabur.app` |

### 1.2 Authentication
- **Protocol**: OAuth 2.0 (Google)
- **Cookie**: `httpOnly`, `SameSite=None`, `Secure`
- **CORS**: Backend allows specific Frontend origin

## 2. API Specification

### 2.1 Base URLs
| Environment | URL |
|-------------|-----|
| Production | `https://martian-api.zeabur.app` |
| Local | `http://localhost:8000` |

### 2.2 Key Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/me` | GET | User session status |
| `/api/results` | GET | Mars Strategy simulation results |
| `/api/race-data` | GET | Flat race data for BCR (wealth, cagr, dividend) |
| `/api/stock/{id}/history` | GET | Raw price/dividend history |
| `/api/export/excel` | GET | Excel export with dynamic params |

### 2.3 Race-Data Response Format (v2.1)
```json
[
  {
    "id": "2383",
    "name": "台光電",
    "year": 2006,
    "wealth": 1000000,
    "value": 1000000,
    "dividend": 0,
    "cagr": 0,
    "roi": 0
  }
]
```
**Note**: Changed from nested `{year, stocks}` to flat format for legacy UI compatibility.

## 3. Simulation Engine

### 3.1 Key Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `start_year` | 2006 | Simulation start year |
| `principal` | 1,000,000 | Initial investment (TWD) |
| `contribution` | 60,000 | Annual contribution (TWD) |

### 3.2 History Output
- **Year Range**: `start_year` → 2026 (21 years inclusive)
- **Fields**: `year`, `value` (wealth), `dividend`
- Year 2006 added as initial investment point (v2.1 fix)

## 4. Deployment Strategy

### 4.1 Services
| Service | Build | Env Vars |
|---------|-------|----------|
| Backend | `Dockerfile` (root) | `GOOGLE_CLIENT_ID`, `SECRET_KEY`, `FRONTEND_URL` |
| Frontend | `frontend/Dockerfile` | `NEXT_PUBLIC_API_URL` |

### 4.2 Environment Variables
| Variable | Service | Example |
|----------|---------|---------|
| `FRONTEND_URL` | Backend | `https://martian-app.zeabur.app` |
| `NEXT_PUBLIC_API_URL` | Frontend | `https://martian-api.zeabur.app` |
| `SECRET_KEY` | Backend | `long_random_string` |

## 5. Changelog (v2.3)
- **Dynamic Stock Naming**: Real-time alignment with TWSE/TPEX data (No more hardcoded maps).
- **Convertible Bond (CB) Support**: Full support for CB tickers (e.g., 11011).
- **Admin Sync Ops**: Enhanced "Smart Update" to always refresh stock list.
- **Directory Consolidation**: Unified python logic in `app/project_tw`.

