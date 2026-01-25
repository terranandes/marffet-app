# 📅 Agents Sync-Up Meeting Minutes
**Date**: 2026-01-26
**Version**: v1
**Participants**: [PM], [PL], [SPEC], [UI], [CV], [CODE]

---

## 1. Project Progress
- **[PL]**: Great work team. **v1.1.0** is successfully deployed to Zeabur (`https://martian-app.zeabur.app/`).
    - Stabilization is complete.
    - Transaction Modal (BUG-007) and Mobile Viewport (BUG-008) are confirmed fixed.
    - **Critical Issue**: We just received a report for **BUG-009 (Mobile Google Login Failure)**. This is P0.

## 2. Feature & Market Status
- **[PM]**: The **AntiGravity Backtesting** feature is our killer app. I love the new **Social Media Copy** (`product/social_media_promo.md`) - we should start pushing that on Threads/IG once BUG-009 is fixed.
    - **Legacy UI**: Confirmed we are fully migrated. `frontend_vite_backup` is just an archive. The port 8000 "embedded" UI is a fallback but not the main product anymore.

## 3. Technical & Specs
- **[SPEC]**: Regarding **BUG-009**: I suspect `SessionMiddleware` in `app/main.py`. If `IS_HTTPS` defaults to `False` (because env var is missing or proxy headers aren't trusted), cookies get set to `Lax` without `Secure`. Mobile Safari is strict about cross-site redirects (Google -> Zeabur).
    - **Action**: [CODE] needs to harden `app/main.py` to force `Secure=True` in production if `FRONTEND_URL` implies HTTPS.

## 4. Work in Progress (WIP)
- **[CODE]**: 
    - **Google Login Fix**: Will investigate `app/main.py`. I probably need to explicitly trust Zeabur's proxy headers earlier or force HTTPS config.
    - **Legacy Cleanup**: I can eventually delete `frontend_vite_backup`, but [PL] says keep it for one more week.

- **[UI]**:
    - **Mobile Experience**: The new "Card View" for portfolio is much better than the table on phones.
    - **Login Flow**: On mobile, the redirect to Google sometimes feels "stuck". We might need a loading overlay before the redirect happens.

## 5. QA & Verification
- **[CV]**: 
    - **E2E Tests**: Full suite (`tests/e2e_suite.py`) is passing 100% on Desktop.
    - **Mobile Tests**: `tests/test_mobile_portfolio.py` is passing.
    - **Gap**: We cannot easily automate "Google Login on real Mobile Safari" via Playwright. This will require **Manual Verification** by Terran (Boss) after the fix.

## 6. Action Items
1.  **[CODE]**: Fix BUG-009 (Check `IS_HTTPS` / `SessionMiddleware`).
2.  **[PL]**: Monitor Zeabur deployment after fix.
3.  **[PM]**: Launch social media campaign once login is stable.

---
**Signed off by**: [PL] Project Leader
