# Martian Agents Sync-Up: Next.js Migration & Launch
**Date**: 2026-01-15
**Version**: v1.0
**Moderator**: [PL] Project Leader

## 1. Attendees
*   [PM] Product Manager
*   [PL] Project Leader
*   [SPEC] SPEC Manager
*   [UI] Frontend Manager
*   [CV] Code Verification
*   [CODE] Backend Manager

## 2. Project Progress (Summary)
*   **[PL]**: "Team, we have successfully completed the migration to Next.js. The app is live on Zeabur with a decoupled architecture."
*   **[UI]**: "The Cyberpunk design system (Cyan/Gold) is implemented. Sidebar, ECharts, and Glassmorphism are stable. Guest/Admin modes are functional."
*   **[CODE]**: "Backend is now pure FastAPI. Legacy Vue templates removed. `ProxyHeadersMiddleware` added to support Zeabur HTTPS."

## 3. Key Issues & Fixes (Triage)
*   **Bug 1: Local Network Popup**
    *   *Cause*: Hardcoded `localhost:8000` in client code.
    *   *Fix*: Refactored to use `NEXT_PUBLIC_API_URL` env var.
    *   *Status*: **RESOLVED**.
*   **Bug 2: Login/Logout Redirect Loop**
    *   *Cause*: Backend Redirect default was `/`, keeping users on the API domain.
    *   *Fix*: Implemented Smart Redirects (Referer-based) + `FRONTEND_URL` fallback.
    *   *Status*: **RESOLVED**.
*   **Bug 3: Cross-Domain Cookie Loss**
    *   *Cause*: Browsers blocked strict cookies between `.app` and `.api`.
    *   *Fix*: Set `SameSite=None`, `Secure=True`, and used Absolute URLs for fetch.
    *   *Status*: **RESOLVED**.

## 4. Features Status
| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Mars Strategy** | ✅ Done | Full simulation, interactive table. |
| **Visualization** | ✅ Done | Bar Chart Race with custom colors. |
| **Authentication** | ✅ Done | Google OAuth, multi-domain support. |
| **Portfolio** | ✅ Done | CRUD operations, Grouping. |
| **AI Chat** | ⏸️ Deferred | Basic API implementation ready, frontend UI pending Premium tier. |

## 5. Deployment Completeness
*   **[SPEC]**: "Infrastructure is defined. Two services (Front/Back) on Zeabur."
*   **[CV]**: "Testing passes. Local vs Cloud discrepancy (CORS/HTTPS) has been addressed."

## 6. Action Items
1.  **[Terran/BOSS]**: Set Env Vars in Zeabur (`FRONTEND_URL`, `NEXT_PUBLIC_API_URL`).
2.  **[Team]**: Monitor logs for 24h.
3.  **[Next Phase]**: Implement "Ruthless Manager" AI notifications fully.

## 7. Next Steps
*   Wait for BOSS final verification on Zeabur.
*   Celebration! 🍺

---
*Reported by [PL]*
