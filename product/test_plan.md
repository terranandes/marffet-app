# Martian Investment System - Test Plan
**Version**: 2.4
**Date**: 2026-01-30
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We use **Playwright MCP** for End-to-End (E2E) verification.

### 1.1 Test Environments
| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ |
| Local Frontend | http://localhost:3000 | ✅ |
| Zeabur Backend | martian-api.zeabur.app | ✅ Deployed |
| Zeabur Frontend | martian-app.zeabur.app | ✅ Deployed |

### 1.2 Test Cases

| ID | Feature | Description | Criteria |
|----|---------|-------------|----------|
| TC-01 | Landing | Home page loads | Title contains "Martian" |
| TC-02 | Mars Strategy | Simulation works | Stock table shows 50 rows |
| TC-03 | BCR | Bar Chart Race | Wealth/CAGR toggle works |
| TC-04 | Guest Mode | Guest button | Creates guest session |
| TC-05 | Google Login | OAuth flow | Redirects to Google (Remote Only) |
| TC-06 | Portfolio | Group CRUD | Create, edit, delete groups |
| TC-07 | Admin Dashboard | System Ops | Buttons visible for GM |
| TC-08 | Year Range | History data | 21 years (2006-2026) |
| TC-09 | AI Copilot | Chat Logic | Server-side Key Fallback works |
| TC-10 | Legacy UI | Color Convention | Profit=Red, Loss=Green |
| TC-11 | Backup | Scheduler & Manual | Startup Log verified |
| TC-12 | Mobile UI | Card View | Cards replace Table on <md screens |
| TC-13 | Login Overlay | Intersection Check | Overlay doesn't block mobile interaction |
| **TC-14** | **Dividend Cache** | **Hybrid Access** | **File+DB sync verified** |
| **TC-15** | **Sync Admin** | **Batch Progress** | **Progress bar shows numeric %** |
| **TC-16** | **Dividend Chart** | **Visualization** | **Charts visible for 2330, 2383** |
| **TC-17** | **Zombie Stock** | **Delisted Logic** | **6238 flatlines post-2020** |
| **TC-18** | **Legacy Chart** | **Title Sync** | **"Yearly Cash Div. Received" (k/M)** |

### 1.3 Execution via Playwright MCP

```bash
# E2E Test Suite Command
pytest tests/e2e/test_full_suite.py
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
- [x] **Sync All Dividends (Hybrid) works**
- [x] Backup to GitHub works (Manual Trigger)

### AI Copilot (New)
- [x] FAB visible on Portfolio/Race pages
- [x] Chat works without client-side key
- [x] "Missing API Key" error properly handled

## 3. Regression Tests (v2.3)

| Test | Expected | Status |
|------|----------|--------|
| Guest mode button | Visible in Sidebar | ✅ |
| /auth/guest endpoint | Returns 200 | ✅ |
| System Ops in Legacy UI | 4 buttons visible | ✅ |
| AI Key Fallback | Chat works | ✅ |
| Backup Scheduler | Logs "Next Backup Job at..." | ✅ |
| **Hybrid Cache** | **App loads dividends without legacy file** | ✅ (New) |

## 4. Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| Zeabur frontend 404 | High | Resolved |
| Favicon 404 on legacy | Low | Cosmetic |
