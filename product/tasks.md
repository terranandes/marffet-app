# Martian Project Tasks
**Owner:** [PL] Project Leader
**Status:** Active

## 1. Immediate Stabilization (Auth & DB Recovery) - [COMPLETED]
- [x] **Fix Login Loop (Cookie Domain)** (`Domain=None` for localhost/Zeabur compatibility)
- [x] **Fix DB Crash (Missing Columns)** (Implemented Self-Healing Schema in `portfolio_db.py`)
- [x] **Fix Logout Redirect** (Implemented Smart Redirect & enforced HTTPS)
- [x] **Fix Frontend Fetch Logic** (Switched to Relative Paths for Cross-Domain support)
- [x] **Verify Localhost Login/Logout** (Legacy: 8000, App: 3000)
- [x] **Verify Zeabur Remote Login/Logout** (Legacy: `martian-api`, App: `martian-app`)

## 2. Next.js Migration Verification - [COMPLETED]
- [x] **Guest Mode localStorage Sync**
- [x] **Settings Modal Alignment** (Feedback Tab, Default Page, Leaderboard)
- [x] **Mobile Responsiveness Check** (Sidebar Relative Paths)

## 3. Pending User Verification (BOSS)
- [ ] **Mobile Login/Logout Correctness** (Zeabur)
    - *Note:* Infrastructure is ready. Pending final user check on actual device.

## 4. Feature Roadmap (Next Steps)
- [ ] **Tab: MoneyCome Compound Interest** (`stkCode=2330`)
- [ ] **Tab: MoneyCome Comparison** (Merge or New Tab?)
- [ ] **Mobile Optimization: Portfolio Card View** (Narrow Screen layout)
- [ ] **Functionality: Ensure Tab CB Works & Notifications Sent**
- [ ] **Multi-language Support** (i18n)
- [ ] **AICopilot Enhancement**
- [ ] **Email Support**

## 5. Maintenance & workflows
- [ ] **Full Test Suite (Automated)** - `tests/e2e_suite.py` (Passing locally, verify on generic CI eventually)
