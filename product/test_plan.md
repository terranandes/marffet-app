# Martian Investment System - Test Plan
**Version**: 2.2  
**Date**: 2026-01-18  
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We use **Playwright MCP** for End-to-End (E2E) verification.

### 1.1 Test Environments
| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ |
| Local Frontend | http://localhost:3000 | ✅ |
| Zeabur Backend | martian-app.zeabur.app | ⚠️ Needs verification |

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

### 1.3 Execution via Playwright MCP

```bash
# Using Playwright MCP server for browser automation
# Test New Frontend
mcp_playwright_browser_navigate(url="http://localhost:3000/mars")
mcp_playwright_browser_wait_for(time=5)
mcp_playwright_browser_take_screenshot(filename="test_mars.png")

# Test Guest Mode
mcp_playwright_browser_click(element="Continue as Guest button")
mcp_playwright_browser_wait_for(time=2)
# Verify user appears in sidebar

# Test Race Tab
mcp_playwright_browser_navigate(url="http://localhost:3000/race")
mcp_playwright_browser_click(element="Play button")
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
- [x] Backup to GitHub works
- [x] Rebuild & Push Pre-warm works

## 3. Regression Tests (v2.2)

| Test | Expected | Status |
|------|----------|--------|
| Guest mode button | Visible in Sidebar | ✅ |
| /auth/guest endpoint | Returns 200 | ✅ |
| System Ops in Legacy UI | 4 buttons visible | ✅ |
| Cold run time | ~5-6 min | ✅ |
| Pre-warm (Rebuild + Push) | ~5 minutes | ✅ |
| Pre-warm single commit | 1 commit for all files | ✅ |

## 4. Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| Zeabur frontend 404 | High | Needs deploy check |
| Favicon 404 on legacy | Low | Cosmetic |
