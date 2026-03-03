# Meeting Notes — 2026-03-03 Marffet Rebrand Execution v1
**Date:** 2026-03-03 03:55 HKT
**Attendees:** [PL], [CODE], [CV], BOSS (Terran)

---

## Completed Tasks

| # | Task | Files Changed | Commit |
|---|------|---------------|--------|
| 1 | Gate Compound Interest comparison mode behind PREMIUM+ | `compound/page.tsx` | `7fcacbe` |
| 2 | Rebrand frontend user-facing strings (Martian → Marffet) | 7 files | `7fcacbe` |
| 3 | Rebrand i18n locale files (en, zh-TW, zh-CN) | 3 files | `7fcacbe` |
| 4 | Rebrand backend metadata + Zeabur domain refs | `main.py`, `auth.py`, `engines.py` | `7fcacbe` |

**Total: 21 files changed, 96 insertions, 85 deletions**
**Frontend Build: ✅ PASS (all 13 routes compile)**

---

## Remaining Tasks

| # | Task | Owner | Status |
|---|------|-------|--------|
| 5 | Update product documentation (READMEs, datasheet, spec) | [PL]/[PM] | ⏳ Pending |
| 6 | Create public repo `terranandes/marffet-app` | [PL] | ⏳ Pending |
| 7 | Update `tasks.md` and final commit | [PL] | ⏳ Pending |

---

## 🔴 BOSS Post-Deployment Checklist

After pushing `master` to origin and the Zeabur auto-deploy succeeds, Terran must manually perform these steps in the Zeabur Dashboard and Google Cloud Console:

### Zeabur Dashboard (https://dash.zeabur.com)

| # | Action | Details |
|---|--------|---------|
| 1 | **Rename Frontend Service** | `martian-app` → `marffet-app` |
| 2 | **Rename Backend Service** | `martian-api` → `marffet-api` |
| 3 | **Update Custom Domain** | Zeabur will auto-assign `marffet-app.zeabur.app` and `marffet-api.zeabur.app` |
| 4 | **Update `FRONTEND_URL` env var** | Change from `https://martian-app.zeabur.app` to `https://marffet-app.zeabur.app` |
| 5 | **Update `GOOGLE_REDIRECT_URI`** (if set) | Change to `https://marffet-app.zeabur.app/auth/callback` |
| 6 | **Verify old domain redirects** | Check if `martian-app.zeabur.app` still resolves (Zeabur may auto-redirect or 404) |

### GitHub Repositories (Completed manually by BOSS)

| # | Action | Details |
|---|--------|---------|
| 7 | **Rename private repo** | Rename `terranandes/martian` to `terranandes/marffet` |
| 8 | **Create public repo** | Create `terranandes/marffet-app` for project showcase |
| 9 | **Add documentation** | Push product READMEs (EN, zh-TW, zh-CN) to the public repo |

### Google Cloud Console (OAuth)

| # | Action | Details |
|---|--------|---------|
| 7 | **Update Authorized JavaScript Origins** | Add `https://marffet-app.zeabur.app` (can keep old one temporarily) |
| 8 | **Update Authorized Redirect URIs** | Add `https://marffet-app.zeabur.app/auth/callback` |
| 9 | **Test Google Login** | After deploy + domain change, test full OAuth flow on mobile & desktop |

### Ko-fi / Buy Me a Coffee

| # | Action | Details |
|---|--------|---------|
| 10 | **Update Ko-fi donation page URL** | If linking back to the app, use `marffet-app.zeabur.app` |

### Verification After Domain Rename

| # | Check | How |
|---|-------|-----|
| ✅ | App loads at new URL | Visit `https://marffet-app.zeabur.app` |
| ✅ | Google OAuth login works | Click Sign In, complete flow |
| ✅ | Session cookie persists on refresh | Refresh page, check user stays logged in |
| ✅ | API health returns "marffet-backend" | Visit `https://marffet-api.zeabur.app/health` |
| ✅ | Sidebar shows "MARFFET" | Visual check on landing page |
| ✅ | Compound Interest comparison locked for free users | Navigate to Compound Interest tab |
| ✅ | CORS allows cross-origin requests | Check browser console for CORS errors |

---

## Decision Log

| Decision | Made By | Rationale |
|----------|---------|-----------|
| Rename app to "Marffet" (Martian + Buffet) | BOSS | Brand identity evolution |
| Rename localStorage keys to `marffet_` | BOSS | Completeness over backward compat |
| Rename private repo to `terranandes/marffet` | BOSS | Clean brand alignment |
| Create separate public repo `terranandes/marffet-app` | BOSS | Clean showcase isolation |
| Gate comparison mode behind PREMIUM+ | BOSS | Feature differentiation for tier value |
