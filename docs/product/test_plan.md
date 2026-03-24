# Marffet Investment System - Test Plan
**Version**: 5.0
**Date**: 2026-03-03
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We use **Playwright MCP** for End-to-End (E2E) verification.

### 1.1 Test Environments
| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ |
| Local Frontend | http://localhost:3000 | ✅ |
| Zeabur Backend | marffet-api.zeabur.app | ✅ Deployed |
| Zeabur Frontend | marffet-app.zeabur.app | ✅ Deployed |

### 1.2 Test Cases

| ID | Feature | Description | Criteria |
|----|---------|-------------|----------|
| TC-01 | Landing | Home page loads | Title contains "Marffet" |
| TC-02 | Mars Strategy | Simulation works | Stock table shows 50 rows |
| TC-03 | BCR | Bar Chart Race | Wealth/CAGR toggle works |
| TC-04 | Guest Mode | Guest button | Creates guest session |
| TC-05 | Google Login | OAuth flow | Redirects to Google |
| TC-06 | Portfolio | Group CRUD | Create, edit, delete groups |
| TC-07 | Admin Dashboard | System Ops | Buttons visible for GM |
| TC-08 | Year Range | History data | 21 years (2006-2026) |
| TC-09 | AI Copilot | Chat Logic | Server-side Key Fallback works |
| TC-10 | Legacy UI | Color Convention | Profit=Red, Loss=Green |
| TC-11 | Backup | Scheduler & Manual | Startup Log verifies UTC Next Run |
| TC-12 | Mobile UI | Card View | Verify Cards replace Table on <md screens |
| TC-13 | Login Overlay | Intersection Check | Verify Overlay doesn't block mobile interaction |
| TC-14 | CB Support | Data Fetch | Can search/add Convertible Bonds (e.g., 11011) |
| TC-15 | Admin Sync | Smart Update | "Smart Update" refreshes Stock List (O(1)) |
| TC-16 | Daily Data | High Res Data | Verify 2330 has Daily Data (200+ rows/year) |
| TC-17 | Mars Strategy | Split Detector | 0050 CAGR > 12% (Split Adjusted) |
| TC-18 | Mars Strategy | Logic Compliance | Buy Logic = First Close |
| TC-19 | DuckDB Rehydration | Persistence | `/health` returns healthy on empty volume |
| TC-20 | Cache Singleton | Performance | Verify All Tabs load in <0.5s via Shared RAM |
| TC-21 | Mars Memory | Zeabur Stability | `/mars/analyze` doesn't 502 with >5M rows |
| TC-22 | JSON Serialization | FastAPI Compliance | No 500 errors from nested NumPy types |
| TC-23 | Data Accuracy | Nominal Consistency | TSMC CAGR 2010-2025 ~19.4% |
| TC-24 | Premium Access | Access Tier Logic | PREMIUM_EMAILS grants premium status, GM_EMAILS grants admin+premium |
| TC-25 | Tier Matrix | 5-Tier Enforcement | Guest/FREE/PREMIUM/VIP/GM tiers resolve correctly in `/auth/me` |
| TC-26 | Home Page i18n | BUG-012 Regression | Verify standard text is shown instead of raw keys like `Home.Title` |
| TC-27 | Mobile Navigation | Bottom Tab Bar | Verify Mobile Top Bar and Bottom 5 tabs appear |
| TC-28 | Mobile Interaction | Touch Targets | Verify horizontal scroll on tables in mobile view |
| TC-29 | Sidebar | User Profile | Verify Guest/Login/Logout visible in Desktop Sidebar |
| TC-30 | Tab Switching | SWR Caching | Verify switching between tabs takes <0.1s without showing loading skeletons on mobile/desktop |
| TC-31 | Auth Smoothness | Google OAuth | Verify Login and Logout UI updates instantly without loops or freezing |
| TC-32 | Auth Resilience | Retry Logic | `/auth/me` network failures retry up to 5× (2s/4s/8s/16s/32s) before Guest fallback |
| TC-33 | Zeabur Cold-Start | Auth Recovery | Authenticated user identity visible on Zeabur within 90s of page load |

### 1.3 Execution via Standard Suites
We have standardized Python test suites for CI/CD and local verification.

#### A. Integration Test Suite (pytest)
```bash
uv run pytest tests/integration/test_all_tabs.py -v
```
*   **Scope**: All 8 sidebar tabs (Mars Strategy, Bar Chart Race, Compound, CB Strategy, Portfolio, Trend, My Race, Cash Ladder).
*   **Coverage**: API endpoints + frontend page accessibility.
*   **Last Run**: 2026-03-08, **15/15 PASSED** in 48.31s.

#### B. Full E2E Suite (Playwright)
```bash
uv run python tests/e2e/e2e_suite.py
```
*   **Scope**: Guest Mode, Group/Stock CRUD, Add Transactions, Mobile Layout verification.
*   **Platform**: Desktop (1280x800) + Mobile (iPhone 12 viewport).
*   **Last Run**: 2026-03-08, **PASSED Local**. Remote Zeabur Failed Desktop (Added BUG-017-CV Timeout Flake).

#### C. Backend Data Verification
```bash
uv run tests/integration/test_fetch_names.py
uv run tests/integration/verify_daily.py
```
*   **Scope**: Verifies "O(1) Stock List" fetching, Convertible Bond (CB) identification, and **Daily Data (Phase 4)** integrity.

#### D. Mobile Specifics
```bash
uv run tests/unit/test_mobile_portfolio.py
```

#### E. Full Local Pipeline (Isolated Worktree)
```bash
# via workflow shortcut
@[/full-test-local]
```
*   **Scope**: Full end-to-end framework verification (Build + Start + Playwright MCP) executed in an isolated git worktree (`.worktrees/martian-test-local`) on alternate ports (3001/8001) to prevent impacting the developer's main environment. Highly effective for catching Next.js hydration and build-time compilation errors.


## Phase 41: Minor Enhancements & Sentry Tuning (`dfafb8c`)
**Date:** 2026-03-24
**Type:** Regression & Feature Verification
**Status:** In Progress

| Feature | Action | Expected Output | Actual | Status |
| --- | --- | --- | --- | --- |
| **Mobile Nav Layout** | View mobile via Playwright | `data-testid="bottom-tab-bar"` locator works for elements. | Locator successfully bounds the nav elements. | ✅ PASSED |
| **Backend Notifications** | Inspect `upgrade_cta` object returned by api | Object contains `timestamp` (ISO) and `is_read`. | Backend API effectively formats and delivers timestamp. | ✅ PASSED |
| **Sentry Config** | Zeabur build | Sentry Next config passes TS check and UI builds correctly. | Passed tsc checks and deployed functional build. | ✅ PASSED |

## 2. Full Feature Verification Checklist (One Round Pass)

**Goal:** Exhaustively verify every designed feature in the Marffet system across Desktop and Mobile viewports for a single full-coverage pass.
**Evidence:** Ensure screenshot evidence is collected for each step to validate UI integrity without side-effects.

### Area A: Global Navigation & Landing
- [ ] Home page loads with title "Marffet"
- [ ] Desktop sidebar shows 8+ nav links
- [ ] Mobile Bottom Tab Bar shows 5 scrollable tabs
- [ ] Default page is NOT `/mars` (must be portfolio or home)
- [ ] Clicking each tab routes to correct page

### Area B: Mars Strategy Tab
- [ ] Simulation table loads with 50 rows
- [ ] Table sortable by CAGR column
- [ ] Clicking a row → line chart appears (NOT stuck loading)
- [ ] Chart shows wealth over time for that stock
- [ ] Excel export button works (downloads file)
- [ ] Mobile view shows card layout

### Area C: Bar Chart Race Tab
- [ ] BCR chart renders with stock bars
- [ ] Wealth / CAGR / Dividend toggle works
- [ ] Year slider responds
- [ ] Play button animates race
- [ ] No duplicate year 2006 bug

### Area D: Compound Interest Tab
- [ ] Single stock mode renders chart
- [ ] Comparison Mode gated for Guest/FREE (shows lock icon)
- [ ] Premium user sees Comparison Mode
- [ ] BAO/BAH/BAL strategy toggle works
- [ ] CAGR and ROI values displayed correctly

### Area E: Portfolio Tab
- [ ] Group creation works
- [ ] Group deletion works
- [ ] Target (stock) add to group works
- [ ] Transaction add (Buy) works
- [ ] Transaction history shows added transactions
- [ ] Dividend sync button works
- [ ] Stats summary shows Market Value / P&L
- [ ] Mobile card view replaces table on narrow viewport

### Area F: Trend Dashboard & My Race
- [ ] Trend area chart renders with data (for logged-in user)
- [ ] Toggle Cost/Value/Unrealized P&L checkboxes update chart
- [ ] Active Holdings section shows stocks by type
- [ ] My Race tab renders personalized race animation

### Area G: Auth System & Convertible Bond (CB) Tab
- [ ] "Sign In with Google" redirects to accounts.google.com
- [ ] Guest mode sets guest session and shows badge
- [ ] Logout cleanly and elegantly clears session via Next.js router
- [ ] In-flight fetches intentionally abort on logout (zero side effects)
- [ ] `/auth/me` returns correct tier
- [ ] Compound Comparison gated for Guest/FREE
- [ ] CB Tab loads and allows CB search / add to portfolio
- [ ] Option B (AuthGuard) blocks heavy load execution for unauthenticated states

### Area H: Notifications & Modals
- [ ] Notification bell shows alert count badge
- [ ] Clicking bell opens notification panel
- [ ] SMA alert shows stock + recommendation
- [ ] Settings Modal opens with 4+ tabs
- [ ] Start Page dropdown explicitly does NOT show "Mars Strategy"
- [ ] Transaction & Dividend History modals open correctly
- [ ] Premium Filter drops premium alerts for Guest/FREE users
- [ ] "Upgrade to Premium" CTA displayed in Sidebar and MobileTopBar for `upgrade_cta` type

### Area I: AI Copilot
- [ ] FAB (floating rocket ✨ button) visible on Portfolio page
- [ ] Clicking FAB opens chat panel with slide-in animation
- [ ] Message sent returns AI response (using server key fallback)
- [ ] Free tier gets Education persona / Premium tier gets Wealth Manager
- [ ] API Key input field visible in Settings Modal

### Area J: Admin Dashboard & Mobile Full Test
- [ ] Admin Dashboard visible to `terranfund` (if GM)
- [ ] System Ops buttons visible + User growth chart renders
- [ ] Membership Injection form visible
- [ ] All 9 tabs load on iPhone 12 viewport
- [ ] Bottom Tab Bar scrollable horizontally

## 3. Regression Tests

### v3.12 (Phase 40) - Full Local E2E Verification (2026-03-24)
| Test | Expected | Status |
|------|----------|--------|
| Backend Health | `/` returns 200 | ✅ PASSED Local |
| Desktop > All 6 Tabs | Portfolio, Mars, BCR, Trend, CB, Ladder load clean | ✅ PASSED Local |
| Mobile > All 6 Tabs | Same 6 tabs load clean on iPhone 12 viewport | ✅ PASSED Local |
| Core CRUD Suite | Guest entry, Group create, Stock add (2330), Transaction add | ✅ PASSED Local |
| Mobile Card Layout | Table hidden, Card visible, Card expand, Trade/History buttons | ✅ PASSED Local |
| `upgrade_cta` Fields | `id`, `title`, `is_read`, `message`, `action_url` present in source | ✅ Verified (Code) |
| Notification Auth Gate | `/api/notifications` requires auth (500 without session) | ✅ Expected Behavior |
| Sentry Backend | `sentry-sdk` loaded without crash | ✅ PASSED Local |

### v3.11 (Phase 39) - Notification Tier Gating & Sentry
| Test | Expected | Status |
|------|----------|--------|
| Tier Gating Backend | Non-premium users receiving premium alerts get `upgrade_cta` injection | ✅ PASSED Remote |
| CTA Frontend Render | `MobileTopBar` and `Sidebar` render the Upgrade CTA correctly | ✅ PASSED Remote |
| Sentry Backend | `sentry-sdk` initialized correctly without throwing error | ✅ PASSED Remote |
| Sentry Frontend | `@sentry/nextjs` initialized on client/server/edge configurations | ✅ PASSED Remote |

### v3.6 (Current) - Auth, Admin Dashboard & DB Locks
| Test | Expected | Status |
|------|----------|--------|
| Auth Proxy Middleware | Login and Logout properly set/clear cookies and redirect | ✅ PASSED Remote |
| Admin User Growth API | `/api/admin/user-growth` returns cumulative metrics over time | ✅ PASSED Remote |
| Admin Dashboard UI | ECharts line chart renders Registered, Premium, and VIP lines | ✅ PASSED Remote |
| SQLite WAL Concurrency | Simultaneous DB connections don't hang (timeout=15.0) | ✅ PASSED Remote |
| GM Tier Documentation | `marffet-app/README*` sanitized of GM mentions | ✅ PASSED Local |

### v3.10 (Current) - Mobile UX Polish & Error Tracking
| Test | Expected | Status |
|------|----------|--------|
| PWA Start URL | `manifest.json` start_url is `/`, allowing user preference redirection | ⏳ Pending |
| Portfolio Skeletons | Skeleton loaders appear while portfolio data is fetching | ⏳ Pending |
| Global SWR Cache | All tabs (Mars, Race, Portfolio, Trend, CB, Ladder) switch instantly with `keepPreviousData: true` | ⏳ Pending |
| Error Boundary | App shows recovery UI on render crashes (`error.tsx`) | ⏳ Pending |

### v3.9 (Current) - App Behavior Modifications
| Test | Expected | Status |
|------|----------|--------|
| Default Tab Redirection | `/mars` default preference gets intercepted and redirects to `/portfolio` | ⏳ Pending Local |
| Settings Tab Mars Removal | "Mars Strategy" is not available in Start Page dropdown | ⏳ Pending Local |
| Mars Chart Error Handling | Shows "Error" gracefully instead of hanging | ⏳ Pending Local |
| Mars Background Cache | `SIM_CACHE` warms up automatically on startup without blocking REST API | ⏳ Pending Local |

### v3.8 (2026-03-06) - Google Auth Fixes & UI Settings
| Test | Expected | Status |
|------|----------|--------|
| Google Auth Smoothness | Login/Logout flow is seamless without freezing; UI updates instantly | ⏳ Pending Local + Remote |
| Tab Switching Snap | SWR caching allows instant tab switching on mobile and desktop | ⏳ Pending Local + Remote |
| Settings Dashboard Translation | "Sidebar.Dashboard" changed to "Trend Dashboard" and correctly translated | ⏳ Pending Remote |
| Settings CB Translation | "Sidebar.CB" changed to "Convertible Bond" and correctly translated | ⏳ Pending Remote |
| Trophy Icon Duplication | No double "🏆" icons in the Settings leaderboard text | ⏳ Pending Remote |
| Google Sign-In Button | Settings Modal "Sign In with Google" triggers redirect properly | ⏳ Pending Remote |

### v3.7 (2026-03-06) - Mobile App-Like UI & Sidebar Regression
| Test | Expected | Status |
|------|----------|--------|
| Bottom Tab Bar | Mobile layout displays BottomTabBar with scrollable tabs (touch-pan-x, no vertical scroll) | ✅ PASSED Local + Remote |
| PWA Service Worker | sw.js is registered and intercepts network requests | ⏳ Pending |
| Sidebar User Profile | Desktop Sidebar displays Sign In/Guest/Sign Out buttons | ✅ PASSED Local + Remote |
| BUG-010-CV Retest | Mobile Card view click targets are easily tappable | ✅ PASSED Local |
| E2E Suite (Remote) | Guest mode, Group creation, Stock add, Transaction add on Zeabur | ✅ PASSED Remote |
| Mobile Top/Bottom Bar (Remote) | MobileTopBar and BottomTabBar visible on mobile viewport | ✅ PASSED Remote |

### v3.5 (2026-03-01) - UI/UX Polish Verification (Modals, Notifications, Tabs)
| Test | Expected | Status |
|------|----------|--------|
| BUG-004-UI | Transaction Date Picker calendar icon visible in dark mode | ⏳ Pending |
| UI/UX Modals | Settings and Transaction modals have glassmorphism background | ⏳ Pending |
| UI/UX Tabs | Settings modal tabs feature smooth sliding animation | ⏳ Pending |
| UI/UX Toaster | Notifications have cyberpunk themes and accent borders | ⏳ Pending |
| BUG-010-CV | Portfolio Card Click Timeout | ⏳ Pending |

### v3.1 (2026-02-11) - Phase 2 Refactoring Verification
| Test | Expected | Status |
|------|----------|--------|
| Strategy Unified | `run_mars_simulation` removed | ✅ |
| Dividend Patches | `dividend_patches.json` loaded | ✅ |
| Split Logic | Unit tests cover 2:1, reverse splits | ✅ |
| Integration Suite | `test_main_refactor.py` passes | ✅ |
| E2E Compliance | TSMC CAGR ~22.2% | ✅ |

### v3.3 (2026-02-25) - Mars Tab Unification & Branch Cleanup
| Test | Expected | Status |
|------|----------|--------|
| Detail API Alignment | `/api/results/detail` uses same ROICalculator as `/api/results` | ✅ PASSED |
| DuckDB ORDER BY | `strategy_service.py` query has `ORDER BY stock_id, date ASC` | ✅ PASSED |
| Dividend Patches | `dividend_patches.json` applied in detail API | ✅ PASSED |
| TSMC Final Value Match | Summary (90,629,825) == Detail BAO (90,629,825) | ✅ PASSED |
| Branch Cleanup | Only `master` exists locally and remotely | ✅ PASSED |
| Stash Cleanup | `git stash list` returns empty | ✅ PASSED |

### v3.4 (2026-02-27) - BCR and Portfolio Bug Fixes
| Test | Expected | Status |
|------|----------|--------|
| BUG-002-PL | BCR duplicate year 2006 removed | ✅ PASSED Remote |
| BUG-003-PL | Portfolio Dividend Sync shows values, not NaN | ✅ PASSED (Via Code/Local) |
| BUG-004-UI | Portfolio Date Picker has dark color-scheme | ✅ PASSED Local |
| BUG-005-PL | Trend Value matches Live Dashboard | ✅ PASSED Remote |
| BUG-006-PL | Race Target Names merged and unique | ✅ PASSED Remote |
| BUG-007-PL | Cash Ladder Sync works, Share icon unique, Profile shows targets | ✅ PASSED Remote |

### v3.2 (2026-02-22) - Zeabur Stabilization & DuckDB Rehydration
| Test | Expected | Status |

### v3.0 (2026-02-07) - Phase 3 Verification
| Test | Expected | Status |
|------|----------|--------|
| Split Detector | 0050 CAGR > 12% | ✅ Verified |
| First Close Buy Logic | Matches MoneyCome | ✅ Verified |
| MarketCache Performance | All tabs < 0.5s load | ✅ Verified |
| Integration Suite | 15/15 tests pass | ✅ PASSED |
| E2E Desktop | Guest + CRUD flow | ✅ PASSED |
| E2E Mobile | Card layout + Actions | ✅ PASSED |
| numpy JSON Fix | /api/results no 500 | ✅ PASSED |

### v2.3 (Prior Verification)
| Test | Expected | Status |
|------|----------|--------|
| Guest mode button | Visible in Sidebar | ✅ |
| /auth/guest endpoint | Returns 200 | ✅ |
| System Ops in Legacy UI | 4 buttons visible | ✅ |
| AI Key Fallback | Chat works with empty client input | ✅ |
| Backup Scheduler | Logs "Next Backup Job at ... UTC" | ✅ |
| Zeabur Build | Build logs are Green | ✅ |

## 4. Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| BUG-011-CV (Transaction Edit) | Medium | ✅ Fixed in master, Verified |
| Zeabur frontend 404 | High | Resolved (Port Fix) |
| Favicon 404 on legacy | Low | Cosmetic |

## 5. Automated Heuristic Bug Hunt
**Executed by**: `[CV]` via Playwright MCP (`tests/e2e/mcp_bug_hunt.py`)

### 5.1 Local Verification Scenarios
*   **Mars Strategy Loading**: Navigate to `/mars`, verify that the data table populates correctly (checking for the 0-results regression).
*   **BCR Loading**: Navigate to `/race`, verify that the chart renders.
*   **Portfolio Groups**: Navigate to `/portfolio`, verify group creation or correct fetching.
*   **Admin Dashboard**: Verify the dashboard shows up correctly (if logged in as GM).

### 5.2 Remote Verification Scenarios
*   **Same as 5.1**, but executed against `https://marffet-api.zeabur.app` and `https://marffet-app.zeabur.app`.
*   Verify API health endpoint.

### 5.3 Evidence Capture
*   Screenshots will be saved to `tests/evidence/`.
*   Bugs will be filed to `docs/jira/BUG-<ID>-CV_<desc>.md`.
