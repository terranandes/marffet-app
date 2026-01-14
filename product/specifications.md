# Martian Investment System - Technical Specifications
**Version**: 2.0 (Next.js Migration)
**Date**: 2026-01-15
**Owner**: [SPEC] Agent

## 1. System Architecture
The system adopts a **Decoupled Client-Server Architecture** tailored for containerized deployment (Zeabur).

### 1.1 Components
1.  **Backend Service (Data Core)**:
    *   **Technique**: Python FastAPI
    *   **Role**: REST API, Authentication Authority, Data Persistence (SQLite/JSON), Simulation Engine.
    *   **Origin**: `https://martian-api.zeabur.app`
2.  **Frontend Service (UI Layer)**:
    *   **Technique**: Next.js 14+ (App Router)
    *   **Role**: Interactive UI, Data Visualization (ECharts), SSR/CSR.
    *   **Origin**: `https://martian-app.zeabur.app`

### 1.2 Authentication & Security
*   **Protocol**: OAuth 2.0 (Google).
*   **Flow**:
    1.  Frontend triggers Login -> Redirects to `Backend/auth/login`.
    2.  Backend handles Google flow -> Sets `httpOnly` Session Cookie (`SameSite=None`, `Secure`).
    3.  Backend redirects back to Frontend Dashboard.
*   **Cross-Domain Strategy**:
    *   Backend CORS allows specific Frontend Origin.
    *   Frontend fetches directly from Backend absolute URL.

## 2. API Specification
### 2.1 Base URL
*   **Production**: Defined by `FRONTEND_URL` and Zeabur Service Name.
*   **Local**: `http://localhost:8000`

### 2.2 Key Endpoints
*   `GET /auth/me`: user session status.
*   `GET /api/notifications`: user alerts.
*   `GET /api/race-data`: historical simulation data.
*   `GET /api/results`: filtered stock list.
*   `GET /api/public/profile/{uid}`: guest view.

## 3. Data Structures
### 3.1 User
```json
{
  "id": "google_sub_id",
  "email": "user@example.com",
  "name": "User Name",
  "nickname": "MarsExplorer",
  "is_admin": false
}
```

## 4. Deployment Strategy
*   **Platform**: Zeabur (or Docker-compatible PaaS).
*   **Service 1 (Backend)**:
    *   Build: `Dockerfile` (Root).
    *   Env Vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SECRET_KEY`, `FRONTEND_URL`, `GM_EMAILS`.
*   **Service 2 (Frontend)**:
    *   Build: `frontend/Dockerfile`.
    *   Env Vars: `NEXT_PUBLIC_API_URL`.

## 5. Environment Variables Map
| Variable | Service | Purpose | Value Example |
| :--- | :--- | :--- | :--- |
| `FRONTEND_URL` | Backend | Redirect Target | `https://martian-app.zeabur.app` |
| `NEXT_PUBLIC_API_URL` | Frontend | API Target | `https://martian-api.zeabur.app` |
| `SECRET_KEY` | Backend | Session Encryption | `long_random_string` |
