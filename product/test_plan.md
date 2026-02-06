# Martian Investment System - Test Plan
**Version**: 2.3  
**Date**: 2026-01-24  
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
| TC-20 | Cache Singleton | Performance | Verify All Tabs load in <0.5s via Shared RAM |

### 1.3 Execution via Standard Suites
We have standardized Python test suites for CI/CD and local verification.

#### A. Full E2E Suite (Playwright)
```bash
uv run tests/e2e/e2e_suite.py
```
*   **Scope**: Guest Mode, Group/Stock CRUD, Mobile Layout, Transactions.
*   **Platform**: Desktop + Mobile viewports.

#### B. Backend Data Verification
```bash
uv run tests/integration/test_fetch_names.py
uv run scripts/verify_daily.py
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

## 3. Regression Tests (v2.3)

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
| Zeabur frontend 404 | High | Resolved (Port Fix) |
| Favicon 404 on legacy | Low | Cosmetic |
