# Martian Investment System - Test Plan
**Version**: 3.0
**Date**: 2026-02-07
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We use **Playwright MCP** for End-to-End (E2E) verification.

### 1.1 Test Environments
| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ |
| Local Frontend | http://localhost:3000 | ✅ |
| Zeabur Backend | martian-api.zeabur.app | ✅ Deployed |

### 1.2 Test Cases

| ID | Feature | Description | Criteria |
|----|---------|-------------|----------|
| TC-01 | Landing | Home page loads | Title contains "Martian" |
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

### 1.3 Execution via Standard Suites
We have standardized Python test suites for CI/CD and local verification.

#### A. Integration Test Suite (pytest)
```bash
uv run pytest tests/integration/test_all_tabs.py -v
```
*   **Scope**: All 8 sidebar tabs (Mars Strategy, Bar Chart Race, Compound, CB Strategy, Portfolio, Trend, My Race, Cash Ladder).
*   **Coverage**: API endpoints + frontend page accessibility.
*   **Last Run**: 2026-02-07, **15/15 PASSED** in 56.70s.

#### B. Full E2E Suite (Playwright)
```bash
uv run python tests/e2e/e2e_suite.py
```
*   **Scope**: Guest Mode, Group/Stock CRUD, Add Transactions, Mobile Layout verification.
*   **Platform**: Desktop (1280x800) + Mobile (iPhone 12 viewport).
*   **Last Run**: 2026-02-07, **PASSED** (0 regressions).

#### C. Backend Data Verification
```bash
uv run tests/integration/test_fetch_names.py
uv run tests/integration/verify_daily.py
```
*   **Scope**: Verifies "O(1) Stock List" fetching, Convertible Bond (CB) identification, and **Daily Data (Phase 4)** integrity.

#### C. Mobile Specifics
```bash
uv run tests/unit/test_mobile_portfolio.py
```


## 2. Manual Verification Checklist

### Mars Strategy
- [x] Table sorts by Simulated Final (default)
- [x] Table sorts by CAGR when clicked
- [x] Shows Top 50 only
- [x] Export Excel button works

### Authentication
- [x] Google Login redirects properly
- [x] Guest Mode creates local session
- [x] Logout clears session

### Admin Dashboard (GM Only)
- [x] System Operations visible
- [x] Update Market Data works
- [x] Rebuild All works
- [x] Backup to GitHub works (Manual Trigger)
- [x] Rebuild & Push Pre-warm works

### AI Copilot (New)
- [x] FAB visible on Portfolio/Race pages
- [x] Chat works without client-side key (if server key set)
- [x] "Missing API Key" error properly handled

## 3. Regression Tests

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

### v3.2 (2026-02-22) - Zeabur Stabilization & DuckDB Rehydration
| Test | Expected | Status |
|------|----------|--------|
| DuckDB Rehydration | _is_db_empty logic triggers on boot | ✅ PASSED |
| Mars Chunked Stream | Peak RAM < 100MB | ✅ PASSED |
| NumPy Sanitizer | Deep recursion avoids 500 errors | ✅ PASSED |
| TSMC CAGR (2010) | 19.4% (Nominal Baseline) | ✅ Verified (19.41%) |
| Match Rate | >84% Correlation vs MoneyCome | ✅ 84.71% |

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
| BUG-011 (Transaction Edit) | Medium | Fixed in master, verification deferred |
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
*   **Same as 5.1**, but executed against `https://martian-api.zeabur.app` and `https://martian-app.zeabur.app`.
*   Verify API health endpoint.

### 5.3 Evidence Capture
*   Screenshots will be saved to `tests/evidence/`.
*   Bugs will be filed to `docs/jira/BUG-<ID>-CV_<desc>.md`.
