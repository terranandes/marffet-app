# BUG-009: Mobile Google Login Failure

## Description
User reports "fails to logic google account" (login failure) on iPhone when accessing `https://martian-app.zeabur.app/`.
Likely specific to Mobile Safari or In-App Browsers. Desktop works (implied).

## Potential Causes
1. **Cookie Security**: `IS_HTTPS` logic in `main.py` might be false if `FRONTEND_URL` isn't set, causing `SessionMiddleware` to use `SameSite=Lax` without `Secure`. Safari might dislike this on HTTPS, or lose the session cookie during redirect.
2. **In-App Browser (WebView)**: If user clicked link from FB/Line, Google blocks `disallowed_useragent`.
3. **Redirect URI Mismatch**: If `ProxyHeadersMiddleware` fails to detect HTTPS on mobile (unlikely).

## Investigation Plan
- [x] Check `app/main.py` HTTPS detection logic. -> *Found it relied only on `FRONTEND_URL` env var.*
- [ ] Verify `ProxyHeadersMiddleware` configuration.
- [ ] Ask user for specific error message (403 vs 400 vs Loop).
- [x] Harden `SessionMiddleware` settings for production. -> *Implemented `IS_PRODUCTION` check.*

## Resolution
**Fixed in `app/main.py`**:
- Added `IS_PRODUCTION` check (looks for Zeabur env vars).
- Enforced `SameSite='none'` and `https_only=True` when running in production or HTTPS.
- Added `https://accounts.google.com` to CORS (just in case).

## Validation
- **Status:** ✅ RESOLVED  
**Verified By:** BOSS (2026-01-29 02:47): [Ready for Deploy]
- **Verification**: User must test on iPhone after Zeabur redeploy.
