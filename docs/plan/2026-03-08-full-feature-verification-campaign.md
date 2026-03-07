# Marffet Full Feature Verification Campaign — Plan v1.0

> **For Agents:** Execute using `subagent-driven-development` skill. Each iteration is a new verification round with Playwright evidence required.

**Goal:** Exhaustively verify every designed feature in the Marffet system across Desktop and Mobile viewports, producing screenshot evidence for each step.

**Architecture:** Browser-based E2E testing via Playwright MCP, targeting both local backend (`port 8001` with `terranfund` mock) and remote Zeabur deployment. Progress persists in `progress.txt`.

**Scope:** 10 Iterations, human-reviewable after each one.

**Tech Stack:** Python + Playwright + Next.js + FastAPI

---

## Brainstorm Notes (Phase 1 — Understanding Lock)

### Core Questions Answered
- **Who verifies?** `[CV]` agent using Playwright MCP
- **What environment?** Local (port 8001/3001) preferred; Remote Zeabur for regression
- **What account?** `terranfund@gmail.com` (mocked via worktree Guest login override)
- **What role does Terran play?** BOSS reviews after each iteration; can approve, request re-test, or pivot
- **What happens on failure?** File JIRA ticket, attempt fix, re-run specific iteration
- **Progress tracking:** `progress.txt` updated after each iteration

---

## Feature Manifest (Complete)

### 🗂️ Tabs (9 Total)
| # | Route | Tab Name | Key Features |
|---|-------|----------|-------------|
| 1 | `/mars`      | Mars Strategy         | Simulation table (Top 50), CAGR sort, target click → line chart, Excel export |
| 2 | `/race`       | Bar Chart Race        | Animated BCR chart, Toggle Wealth/CAGR/Dividend, Year slider, Play/Pause |
| 3 | `/compound`   | Compound Interest     | Single stock simulator, Comparison Mode (Premium), BAO/BAH/BAL strategies |
| 4 | `/portfolio`  | Portfolio             | Group CRUD, Target CRUD, Transaction CRUD, Dividend Sync, Stats cards |
| 5 | `/cb`         | Convertible Bond      | CB search, Add to portfolio, CB-specific metrics |
| 6 | `/trend`      | Trend Dashboard       | Area chart (Cost/Value/P&L), Holdings breakdown by type |
| 7 | `/myrace`     | My Portfolio Race     | Personalized race animation vs benchmark |
| 8 | `/ladder`     | Cash Ladder           | Cash flow projection table |
| 9 | `/admin`      | Admin Dashboard       | System Ops, Membership injection, User growth chart |

### 🔔 Notification Engine
- SMA Pair Rebalancing (Gravity Alert)
- Market Cap Rebalancing (Size Authority)
- CB Arbitrage Alerts

### 🪟 Modals
- Settings Modal (Preferences, Account, API Keys, Sponsor Us)
- Transaction Form Modal (Buy/Sell)
- Transaction History Modal
- Dividend History Modal
- Login Overlay / Auth wall

### 🔐 Auth System
- Google OAuth flow (Login/Logout)
- Guest Mode (localStorage-only)
- 5-Tier entitlement (Guest/FREE/PREMIUM/VIP/GM)
- Session cookie persistence
- `/auth/me` tier resolution

### 🤖 AI Copilot (AICopilot.tsx)
- Floating FAB visible on all pages
- Chat panel open/close animation
- Free Tier persona (Investment Educator)
- Premium Tier persona (Wealth Manager)
- Server-side API key fallback
- Portfolio context injection

---

## Iterations (10 Rounds)

### Iteration 1: Global Navigation & Landing
**Scope:** Home page, tab navigation, sidebar, mobile bottom bar
**Checklist:**
- [ ] Home page loads with title "Marffet"
- [ ] Desktop sidebar shows 8 nav links
- [ ] Mobile Bottom Tab Bar shows 5 scrollable tabs
- [ ] Default page is NOT `/mars` (must be portfolio or home)
- [ ] Clicking each tab routes to correct page
**Evidence:** `iter1_desktop_home.png`, `iter1_mobile_home.png`, `iter1_mobile_tabs.png`

---

### Iteration 2: Mars Strategy Tab
**Scope:** `/mars` full feature set
**Checklist:**
- [ ] Simulation table loads with 50 rows
- [ ] Table sortable by CAGR column
- [ ] Clicking a row → line chart appears (NOT stuck loading)
- [ ] Chart shows wealth over time for that stock
- [ ] Excel export button works (downloads file)
- [ ] Mobile view shows card layout
**Evidence:** `iter2_mars_table.png`, `iter2_mars_chart.png`, `iter2_mars_mobile.png`

---

### Iteration 3: Bar Chart Race Tab
**Scope:** `/race` full feature set
**Checklist:**
- [ ] BCR chart renders with stock bars
- [ ] Wealth / CAGR / Dividend toggle works
- [ ] Year slider responds
- [ ] Play button animates race
- [ ] No duplicate year 2006 bug
**Evidence:** `iter3_bcr_loaded.png`, `iter3_bcr_playing.png`

---

### Iteration 4: Compound Interest Tab
**Scope:** `/compound`
**Checklist:**
- [ ] Single stock mode renders chart
- [ ] Comparison Mode gated for Guest/FREE (shows lock icon)
- [ ] Premium user sees Comparison Mode
- [ ] BAO/BAH/BAL strategy toggle works
- [ ] CAGR and ROI values displayed correctly
**Evidence:** `iter4_compound_single.png`, `iter4_compound_premium_gate.png`

---

### Iteration 5: Portfolio Tab
**Scope:** `/portfolio` full CRUD
**Checklist:**
- [ ] Group creation works
- [ ] Group deletion works
- [ ] Target (stock) add to group works
- [ ] Transaction add (Buy) works
- [ ] Transaction history shows added transactions
- [ ] Dividend sync button works
- [ ] Stats summary shows Market Value / P&L
- [ ] Mobile card view replaces table on narrow viewport
**Evidence:** `iter5_portfolio_groups.png`, `iter5_portfolio_transaction.png`, `iter5_portfolio_mobile.png`

---

### Iteration 6: Trend Dashboard & My Race
**Scope:** `/trend` and `/myrace`
**Checklist:**
- [ ] Trend area chart renders with data (for logged-in user)
- [ ] Toggle Cost/Value/Unrealized P&L checkboxes update chart
- [ ] Active Holdings section shows stocks by type
- [ ] My Race tab renders personalized race animation
**Evidence:** `iter6_trend_chart.png`, `iter6_myrace.png`

---

### Iteration 7: Auth System
**Scope:** Login / Logout / Tier / Session
**Checklist:**
- [ ] "Sign In with Google" button redirects to accounts.google.com
- [ ] Guest mode sets guest session and shows "Guest Mode" badge
- [ ] Logout clears session cookie
- [ ] `/auth/me` returns correct tier for `terranfund@gmail.com`
- [ ] Admin Dashboard visible only to GM tier
- [ ] Compound Comparison gated for Guest/FREE
**Evidence:** `iter7_auth_login.png`, `iter7_auth_me_response.png`, `iter7_guest_mode.png`

---

### Iteration 8: Notifications & Modals
**Scope:** Bell icon, Settings Modal, Transaction Modals
**Checklist:**
- [ ] Notification bell shows alert count badge
- [ ] Clicking bell opens notification panel
- [ ] SMA alert shows stock + recommendation
- [ ] Settings Modal opens with 4+ tabs (Preferences / Account / API Keys / Sponsor Us)
- [ ] Start Page dropdown does NOT show "Mars Strategy"
- [ ] Transaction Form Modal opens from Portfolio target dropdown
- [ ] Dividend History Modal opens correctly
**Evidence:** `iter8_notifications.png`, `iter8_settings_modal.png`, `iter8_transaction_modal.png`

---

### Iteration 9: AI Copilot
**Scope:** AICopilot.tsx FAB and chat functionality
**Checklist:**
- [ ] FAB (floating rocket ✨ button) visible on Portfolio page
- [ ] Clicking FAB opens chat panel with slide-in animation
- [ ] Message sent returns AI response (using server key fallback)
- [ ] Free tier gets Education persona
- [ ] Premium tier gets Wealth Manager persona
- [ ] API Key input field visible in Settings Modal
**Evidence:** `iter9_ai_collapsed.png`, `iter9_ai_chat.png`, `iter9_ai_response.png`

---

### Iteration 10: Admin Dashboard & Mobile Full Test
**Scope:** `/admin` (GM only) + full mobile E2E
**Checklist (Admin):**
- [ ] Admin Dashboard visible to `terranfund` (if GM)
- [ ] System Ops buttons visible
- [ ] User growth chart renders
- [ ] Membership Injection form visible

**Checklist (Mobile):**
- [ ] All 9 tabs load on iPhone 12 viewport
- [ ] Bottom Tab Bar scrollable horizontally
- [ ] Portfolio cards tappable
- [ ] Mars table horizontally scrollable
**Evidence:** `iter10_admin_dashboard.png`, `iter10_mobile_all_tabs.png`

---

## Multi-Agent Review Notes (Phase 2)

### 🔴 [Skeptic] — Assumptions That Could Fail
- Mars chart clicking requires a specific click event + `activeBar` state. If `detailResult.error` check is wrong, chart never shows.
- Guest mode override in the worktree is a hack. Any restart resets it.
- Notifications require a live portfolio + backend trigger — empty DB shows nothing.
- Mobile viewport at 390px may not show Desktop sidebar (desired), so "Trend" link might only be in Bottom Tab.

### 🟡 [Constraint Guardian] — Non-Functional Constraints
- Zeabur 512MB RAM: Do NOT run Mars background cache on Zeabur (`ZEABUR_ENVIRONMENT_NAME` guard is now in place ✅).
- Local test on port 3001 requires `next` binary from `frontend/node_modules/.bin`. Must use full path.
- Evidence screenshots must NOT be committed to git.
- SQLite WAL may lock if two processes write simultaneously; worktree runs different port so this is safe.

### 🟢 [User Advocate] — UX Concerns
- If tabs show skeletons for >3s on first load, the user experiences it as "stuck". SWR revalidation interval should be tested.
- Empty portfolio state must show a helpful message ("Create your first group!") not a blank white area.
- Mobile Bottom Tab Bar must not block Floating Action Buttons (FAB) on Portfolio page.

### ⚖️ [Integrator] Verdict: **APPROVED with conditions**
- Condition 1: Each iteration must start by checking `curl http://localhost:8001/health` before Playwright
- Condition 2: Screenshots taken at both 1280×800 (Desktop) and 390×844 (iPhone 12)
- Condition 3: `progress.txt` updated with ✅/❌ per iteration after BOSS approves

---

## Verification Plan

### Per Iteration
```bash
# 1. Health check
curl -m 5 -s http://127.0.0.1:8001/health

# 2. Playwright MCP automation
# (using browser_subagent for screenshots)

# 3. Update progress.txt
echo "Iteration X: [✅ PASSED / ❌ FAILED] - YYYY-MM-DD" >> progress.txt
```

### Evidence Storage
- **Local:** `tests/evidence/<prefix>_<description>.png`
- **Remote:** `tests/evidence/remote_<prefix>_<description>.png`
- **Do NOT commit** screenshots (already in `.gitignore`)

---

## Execution Protocol

1. **Boss (Terran)** reviews this plan and approves to start
2. **[CV] Agent** runs Iteration 1 and provides `notify_user` with screenshots
3. **Boss** gives feedback: "PASS" / "FAIL: <note>" / "skip to next"
4. Agent runs next iteration
5. Repeat 10 times
6. Final `progress.txt` committed with overall status

**Human Gate:** After every iteration, execution pauses for Boss review.
