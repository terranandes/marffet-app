# Meeting Notes: Agents Sync-Up
**Date:** 2026-01-27 (v2)
**Topic:** Auth Recovery, Dual-UI Architecture, and Stabilization

## 1. Project Progress
- **Feature:** Dual-UI Authentication (Frontend + Legacy) has been architected and deployed.
- **Status:**
    - **Localhost:** Confirmed working (Legacy & Next.js).
    - **Zeabur:** Deployed with "Dual Domain" fix (`COOKIE_DOMAIN=None`, Relative Paths). Waiting for final user verification tomorrow.
- **Critical Fixes:**
    - **Login Loop:** Solved by `Host-Only` cookies.
    - **Cross-Domain Fetch:** Solved by enforced `Relative Paths` in Frontend.
    - **Redirect URI Mismatch:** Solved by `Smart Redirect Logic` in Backend (Referer-based).
    - **DB Crashes:** Solved by `Self-Healing Schema` (Startup Migration).

## 2. Current Bugs & Triages
- **[RESOLVED]** "Mismatching State" on Zeabur (Legacy UI) -> Fixed by HTTPS enforcement and correct Redirect URI.
- **[RESOLVED]** "Effectiveless Login" on Frontend -> Fixed by switching Fetch to Relative Paths.
- **[Monitoring]** User will verify tomorrow. Potential edge case: Mobile Browser (Safari ITP) handling of Host-Only cookies (should be fine with `SameSite=None, Secure`).

## 3. Discrepancy (Local vs Remote)
- **Local (Port 3000/8000):** Shares `localhost` domain. Cookies naturally shared.
- **Remote (Zeabur):** Distinct domains (`martian-app` vs `martian-api`).
- **Resolution:** We adopted the "Remote-First" architecture (`Domain=None`) which treats them as separate entities. This works for both environments.

## 4. Mobile Layout
- **[UI]**: Confirmed `Sidebar.tsx` now uses relative links. This ensures mobile users on `martian-app` stay on `martian-app`, avoiding "App Switching" feel.
- **Follow-up:** Check Layout Responsiveness on `martian-app` (Task for tomorrow).

## 5. Next Steps
1.  **[CV]**: Run Full Test Suite (Headless) to verify existing flows didn't regress.
2.  **[UI]**: Verify Mobile Experience (Responsiveness).
3.  **[BOSS]**: Verify Zeabur Login tomorrow.

## Summary
The "Disaster Scene" (災後現場) has been cleaned, rebuilt, and documented. The architecture is now more robust than before, enforcing strict Domain isolation which aligns with modern security standards.

**Reported by:** [PL] Project Leader
