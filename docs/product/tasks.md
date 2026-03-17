# Marffet Project Tasks

**Owner:** [PL] Project Leader
**Status:** Active

---

## Archived Phases (COMPLETED — detail in git history)

> The following phases are fully completed and archived. See git history for full detail.
> Meeting notes and code reviews before 2026-03-01 have been pruned from the filesystem.

| Phase | Title | Key Achievement |
|-------|-------|-----------------|
| 1 | Auth & DB Stabilization | Cookie domain fix, self-healing schema, HTTPS redirect |
| 2 | Next.js Migration Verification | Guest localStorage, Settings Modal, mobile responsiveness |
| 3 | User Verification (BOSS) | Mobile login/logout on Zeabur |
| 4 | Feature Roadmap | Compound Interest, MoneyCome Comparison, My Race, Scraper, MarketCache |
| 6 | Universal Data Lake | Universe backfill, Admin Dashboard, Ultra-Fast Crawler, DuckDB prep |
| 7 | DuckDB Core Migration | JSON→DuckDB (6.5M rows), MarketDataProvider, cleanup |
| 14 | Nominal Price Standardization | MI_INDEX 2004-2025, 5M+ rows, dividend import |
| 15 | DuckDB Optimization & Dividend | Single source of truth, Tab audit |
| 16 | Data Integrity (2000-2025) | Bad tick cleanup, split patching, CAGR >85% validation |
| 17 | Grand Correlation & Zeabur Deploy | 84.71% match rate, Parquet backup, nightly pipeline |
| 18 | Pure Nominal DB Rebuild | Strict nominal prices, absolute dividends, 67.45→84.71% |
| 19-21 | Correlation Math Tuning | SplitDetector, emerging market exclusion, final tuning |
| 22 | Multi-Language Support (i18n) | LanguageContext, 3 locales, all pages translated |
| 23 | Phase 23: UI/UX Polish | GM Dashboard, Settings Modal, Phase E/F, Portfolio Webull style |
| 24 | VIP/PREMIUM Membership Injection | Membership API, tier precedence, sponsorship links |
| 25 | Marffet Rebrand & Tier Gating | Brand rename, localStorage migration, 5-tier formalization |
| 26 | Tier Differentiation (Backend) | 4-tier limit enforcement in portfolio_service |
| 27 | Chart Viz & Data Integrity | X-axis alignment, pre-IPO filter, BUG-012 fix |
| 28 | Public Repo Showcase | README sync, screenshots, LICENSE, marffet-app repo |
| 29 | Accounts-Over-Time Chart | Admin Net Worth Line Chart |
| 30 | Document-Flow & Mobile Sidebar | BMAC/Ko-fi docs, sidebar scroll fix |
| 31 | Mobile App-Like Experience | Bottom tab bar, PWA, touch polish, page transitions |

### Remaining Open Items from Archived Phases

- [ ] Direct DB Upload to Zeabur (Bypass Cloud Fetch) — Phase 14
- [ ] TSMC CAGR ~19% frontend UI verification (pending Boss review) — Phase 17
- [ ] **BUG-000-CV**: Local Worktree Frontend `.env.local` Missing — LOW <!-- id: bug-110-cv -->
- [ ] **BUG-010-CV**: Mobile Portfolio Card Click Timeout (E2E flake) <!-- id: bug-114 -->
- [ ] **BUG-115-PL**: YFinance Adjusted Dividend Mismatch — resolved by Phase 18 rebuild <!-- id: bug-115 -->
- [x] **BUG-021-CV CLOSED**: Guest Mode uses Shared Backend DB instead of LocalStorage — 🔴 CRITICAL
- [x] **Interactive Backfill Dashboard** — Admin feature, low priority
- [ ] **Mobile Premium Overhaul** — deferred

## 30. Phase 32: Google Auth Stabilization & UI/UX Polish - [COMPLETED]
>
> Ref: `docs/meeting/meeting_notes_2026_03_07_sync_v2.md`

- [x] **Google Auth Diagnostics & Fix** (`auth.py`)
  - [x] Identified Safari ITP HTML workaround as root cause of Next.js rewrite freezing.
  - [x] Replaced with standard HTTP `RedirectResponse` resolving the loop.
  - [x] Verified login/logout stability locally.
- [x] **AICopilot UI/UX Polish** (`AICopilot.tsx`)
  - [x] Upgraded design system using newly introduced `ui-ux-pro-max` workflow.
  - [x] Added `backdrop-blur-2xl` glassmorphism, Framer Motion animations, sleek SVGs, and responsive sticky input.
- [x] **Agents Sync Meeting - 2026-03-07 v2** (Ref: `docs/meeting/meeting_notes_2026_03_07_sync_v2.md` & `docs/code_review/code_review_2026_03_07_sync_v2.md`)

## 31. Phase 33: Client-Side Routing & Rendering Optimization - [COMPLETED]

- [x] **File BUG-015** for infinite rendering state on Tab Switch (Mobile/Desktop)
- [x] **Install SWR** caching library for the Next.js frontend
- [x] **Refactor Tabs** to use SWR (Mars, Race, Portfolio, Trend, CB, Ladder, Compound) replacing native Context/useState logic
- [x] **Verify Tab Snapping** functionality ensuring `< 0.1s` UI updates and elimination of React skeleton loaders.
- [x] **Update Test Plan** (`TC-30` Tab Switching Snap, `TC-31` Auth Smoothness) for E2E validation.
- [x] **Agents Sync Meeting - 2026-03-07 v3** (Ref: `docs/meeting/meeting_notes_2026_03_07_sync_v3.md` & `docs/code_review/code_review_2026_03_07_sync_v3.md`)
- [x] **BUG-015-PL CLOSED**: Infinite Rendering on Tab Switch — Fixed via SWR refactor.
- [x] **BUG-016-PL CLOSED**: Mobile AICopilot Notch Close Button — Fixed via `env(safe-area-inset-top)` padding.
- [x] **AbortError Fix** — `UserContext.tsx` timeout 8s→15s, explicit abort reason, silent catch for expected timeouts.
- [x] **Backend Deadlock Recovery** — Long-running Uvicorn on port 8000 diagnosed and restarted.
- [x] **Agents Sync Meeting - 2026-03-07 v4** (Ref: `docs/meeting/meeting_notes_2026_03_07_sync_v4.md` & `docs/code_review/code_review_2026_03_07_sync_v4.md`)
- [x] **Agents Sync Meeting - 2026-03-07 v5** (Ref: `docs/meeting/meeting_notes_2026_03_07_sync_v5.md` & `docs/code_review/code_review_2026_03_07_sync_v5.md`)
  - Code review: APPROVED (11 source files, 235+/308−). Fixed root `node_modules` tracked in git.
  - JIRA: 15/17 CLOSED. No new bugs. Phase 34 audit items identified from BOSS_TBD.md.

## 32. Phase 34: App Behavior & UX Fixes - [COMPLETED]
>
> Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v6.md`

- [x] **Default Tab Redirect** — `/mars` → `/portfolio` in `page.tsx`. Existing users with `/mars` saved are migrated.
- [x] **Settings Start Page Cleanup** — Removed `/mars` from dropdown in `SettingsModal.tsx`
- [x] **Mars Background Warmup** — `warm_mars_cache()` task in `main.py` lifespan hook (local only; Zeabur guard in place)
- [x] **Mars Chart Error Fix** — `detailResult.error` graceful display in `mars/page.tsx`
- [x] **Test Plan v3.9** — Added Phase 34 test cases to `test_plan.md`
- [x] **Agents Sync Meeting - 2026-03-08 v6** (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v6.md` & `docs/code_review/code_review_2026_03_08_sync_v6.md`)
  - Code review: APPROVED. Phase 34 complete. Phase 35 Full Feature Verification Campaign planned.
- [x] **Agents Sync Meeting - 2026-03-08 v7** (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v7.md` & `docs/code_review/code_review_2026_03_08_sync_v7.md`)
  - Code review: APPROVED. Cleaned temp files, fixed duplicate cache check in `main.py`. Phase 35 awaiting BOSS signal.
- [x] **Agents Sync Meeting - 2026-03-08 v8** (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v8.md` & `docs/code_review/code_review_2026_03_08_sync_v8.md`)
  - Code review: APPROVED. Implemented strict `AuthGuard` for zero-load unauthenticated pages. Refactored logout to client-side Next.js router. Deleted redundant `/login` page completely.

## 33. Phase 35: Full Feature Verification Campaign - [COMPLETED]
>
> Ref: `docs/plan/2026-03-08-full-feature-verification-campaign.md`

**Campaign:** 10 full-scope verification rounds, BOSS-gated between each round.

- [x] **Round 1** — Guest Login Verification (10/10 areas PASSED)
  - Evidence: `tests/evidence/round1_area_*.png` (27 screenshots)
  - **Hotfix 35.1**: CB tab `portfolioCBs.map` TypeError fixed in `cb/page.tsx`
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v9.md` & `docs/code_review/code_review_2026_03_08_sync_v9.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v10.md` & `docs/code_review/code_review_2026_03_08_sync_v10.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_08_sync_v11.md` & `docs/code_review/code_review_2026_03_08_sync_v11.md`)
- [x] **Round 2** — Authenticated User Verification (`terranfund@gmail.com`)
  - Evidence: `tests/evidence/round2_area_*.png` (20+ screenshots, Desktop + Mobile)
  - **Hotfix 35.2**: Mobile Infinite Spinner — `UserContext.tsx` timeout fix (`dd995de`)
  - **Hotfix 35.3**: Google Sign-In Failure — `auth.py` redirect_uri sync (`b1d8746`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_10_sync_v12.md` & `docs/code_review/code_review_2026_03_10_sync_v12.md`)
- [x] **Round 3** — Multi-Account Login/Logout Verification (A→B→A Sequential)
  - Evidence: `tests/evidence/round3/` (6 screenshots: dashboard, settings, logged-out per account)
  - **Resolution:** `/auth/test-login` mock endpoint with `TESTING=true` gate implemented in `app/auth.py`.
  - **Re-run:** `round3_verification.py` verified 3-stage A→B→A account switching ✅.
  - **Hotfix 35.4**: `auth.py`/`auth/guest` now both inject mock users into SQLite + grant PREMIUM tier to avoid silent 500 errors on group creation.
  - **Hotfix 35.5**: `UserContext.tsx` auth timeout 10s→30s to prevent mobile spinner false-dismissal.
  - **Hotfix 35.6**: All Playwright scripts patched with `press_sequentially(delay=50)` to prevent React 18 event loss.
  - **Hotfix 35.7**: `round3_verification.py` now uses `127.0.0.1:3001` proxy routing instead of direct backend POST.
  - **BUG-020-CV CLOSED**: Mobile group locator issue resolved via PREMIUM tier auto-grant + sequential typing.
  - Full suite: `round3_verification.py` ✅ · `e2e_suite.py` (Desktop) ✅ · `test_mobile_portfolio.py` (Mobile) ✅
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_12_sync_v13.md` & `docs/code_review/code_review_2026_03_12_sync_v13.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_12_sync_v14.md` & `docs/code_review/code_review_2026_03_12_sync_v14.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_13_sync_v15.md` & `docs/code_review/code_review_2026_03_13_sync_v15.md`)
- [x] **Round 4** — Guest Mode Verification (`/auth/guest` Endpoint)
  - Evidence: `guest_mode_architecture_analysis.md`, `tests/evidence/1_portfolio_guest.png`
  - **Resolution:** Guest Mode rebuilt to rely 100% on `LocalStorage`. The backend session generation has been completely removed to prevent `users` table pollution. The frontend test suite `e2e_suite.py` was updated to accurately interact with the `Explore as Guest` UI element and successfully verified Group / Transaction handling.
  - **Dividend Sync Fix:** Resolved mapping discrepancy in `calculation_service.py`. Flattened `total_cash` to `total_dividend_cash` in the target summary API to match frontend expectations.
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_13_sync_v16.md` & `docs/code_review/code_review_2026_03_13_sync_v16.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_13_sync_v17.md` & `docs/code_review/code_review_2026_03_13_sync_v17.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_13_sync_v18.md` & `docs/code_review/code_review_2026_03_13_sync_v18.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_14_sync_v19.md` & `docs/code_review/code_review_2026_03_14_sync_v19.md`)
- [x] **Round 5** — Zeabur Remote Verification Campaign
  - Evidence: `tests/evidence/nonguest_*.png` and `state_gm.json` testing.
  - Verified Guest Mode via `e2e_suite.py` against Zeabur production URL.
  - Verified Authenticated (Premium GM) flow via `test_nonguest_remote.py` and manual BOSS verification of gated features.
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_14_sync_v20.md` & `docs/code_review/code_review_2026_03_14_sync_v20.md`)
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v22.md` & `docs/code_review/code_review_2026_03_15_sync_v22.md`)
- [x] **Round 6** — Local Isolation Verification Campaign
  - Executed via `@[/full-test]` triggering `full-test-local` worktree on ports 3001/8001.
  - Verified Guest flow on UI via `e2e_suite.py` and mobile layout.
  - Agents Sync Meeting (Ref: `docs/meeting/meeting_notes_2026_03_15_test_v23.md` & `docs/code_review/code_review_2026_03_15_test_v23.md`)

## 34. Phase 36: Mobile UX Polish & Error Tracking - [COMPLETED]
>
> Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v24.md`
> Evidence: `walkthrough.md`, `mobile_verify_1_portfolio.png`, `mobile_verify_2_switch_back.png`

- [x] **PWA Landing Page Fix** — `manifest.json` `start_url`: `/`.
- [x] **Portfolio Skeleton UI** — Added `animate-pulse` components for data hydration states.
- [x] **Global SWR Tab Caching** — Applied `keepPreviousData: true` to all primary tabs.
- [x] **Global Error Boundary** — Implemented `frontend/src/app/error.tsx` for production recovery.
- [x] **Public Showcase Sync** — Synchronized READMEs and images to `marffet-app` public repository.
- [x] **Agents Sync Meeting - 2026-03-15 v24** (Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v24.md` & `docs/code_review/code_review_2026_03_15_sync_v24.md`)
  - Code review: APPROVED. Perceived performance on mobile 🚀.
  - Phase 36 complete. Transitioning to Phase 37 Remote Sweep.


## 35. Phase 37: Full Feature Verification Campaign (Remote) — [IN PROGRESS]
>
> Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v26.md`

### BUG Fixes
- [x] **BUG-021** — Auth Account Switch Failure (`?error=auth_failed`)
  - Root Cause: Fire-and-forget logout race condition in `UserContext.tsx`
  - Fix 1: `await fetch('/auth/logout')` before `router.push('/')` in `UserContext.tsx`
  - Fix 2: `auth.py` logout returns JSON for `fetch()`, explicitly `delete_cookie("session")`
  - Ref: `docs/jira/BUG-021-PL_auth_account_switch_failure.md`
  - Commit: `c1a2b97`
- [x] **BUG-022-SPEC** — Frontend Auth Resilience (permanent Guest fallback on network error)
  - Root Cause: `UserContext.tsx` and `usePortfolioData.ts` fell back to Guest Mode on first network error.
  - Fix: 5-attempt retry with exponential backoff (2s/4s/8s/16s/32s) + 90s timeout.
  - Ref: `docs/jira/BUG-022-SPEC_frontend_auth_guest_fallback_no_retry.md`
  - Commits: `d824c07`, `270ff4f`
- [x] **Round 7 Final Verification** — 12 cells executed (Local 6/6 ✅, Zeabur Guest 2/2 ✅, Zeabur Auth 4/4 ⚠️ auth ok / data slow)
  - Evidence: `tests/evidence/round7_final/` (41 screenshots)

### Pending (Phase 37)
- [ ] Fix BUG-020 mobile E2E locator (`test_mobile_portfolio.py`)
- [ ] Add `isValidating` background-fetch spinner per tab
- [ ] Full remote Playwright E2E sweep on Zeabur production
- [ ] Physical device PWA install verification (Boss-led)
- [ ] Update `docs/product/feature_portfolio.md` (add skeleton loader note)
- [ ] Sync public GitHub (`marffet-app`)

### Agents Sync Meeting — 2026-03-15 v25, v26, v27 / 2026-03-18 v28
- [x] v25 Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v25.md` & `docs/code_review/code_review_2026_03_15_sync_v25.md`
- [x] v26 Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v26.md` & `docs/code_review/code_review_2026_03_15_sync_v26.md`
- [x] v27 Ref: `docs/meeting/meeting_notes_2026_03_15_sync_v27.md` & `docs/code_review/code_review_2026_03_15_sync_v27.md`
  - Mars Landing Protection & Cache Warm-up implemented and verified. Phase 37 accelerated.
- [x] v28 Ref: `docs/meeting/meeting_notes_2026_03_18_sync_v28.md` & `docs/code_review/code_review_2026_03_18_sync_v28.md`
  - BUG-022-SPEC CLOSED. Round 7 12/12 cells executed. Auth retry fix verified. Phase 38 backlog expanded.

## 36. Phase 38: Backlog Items
- [ ] CSRF token on `/auth/logout` endpoint
- [ ] Sentry error integration (deferred from Phase 36)
- [ ] AI Copilot feature (ref: `docs/product/feature_ai_copilot.md`)
- [ ] Extract `exponentialBackoffRetry<T>()` utility helper (`frontend/src/lib/utils.ts`)
- [ ] Tighten `lastError: any` → `Error | null` in `UserContext.tsx`
- [ ] Add "Content still loading…" status message after 10s of skeleton display
- [ ] Replace `asyncio.sleep()` with `page.wait_for_selector()` in `round7_full_suite.py`
- [ ] Add `--clean` flag to `round7_full_suite.py` to wipe evidence dir before runs
- [ ] Service Worker Data Persistence (last-known Portfolio state in Disk-Cache)
