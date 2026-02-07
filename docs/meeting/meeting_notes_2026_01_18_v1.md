# Agents Sync Meeting Notes

**Date:** 2026-01-18 01:00 UTC+8  
**Attendees:** [PM], [SPEC], [PL], [CODE], [UI], [CV]  
**Version:** v2

---

## [PL] Meeting Summary

### 1. Project Progress ✅

| Phase | Status | Notes |
|-------|--------|-------|
| UI Alignment | ✅ Complete | Legacy + New aligned |
| Guest Mode | ✅ **NEW** | Added today |
| Pre-warm Automation | ✅ Complete | Single commit |
| Cold Run | ✅ ~2 min | 3x faster |

**Commits Pushed (2026-01-17 ~ 01-18):**
- `0d5b16d` - feat: Add /auth/guest endpoint for guest mode login
- `357e536` - feat: Add Continue as Guest button to new frontend Sidebar
- `85d2351` - docs: Add agents sync meeting notes 2026-01-17
- `55d9cf2` - feat: Add System Operations to Legacy UI Admin tab

---

### 2. Current Bugs 🐛

| ID | Description | Severity | Owner | Status |
|----|-------------|----------|-------|--------|
| BUG-001 | Zeabur deployment needs verify | 🟡 Medium | [PL] | Open |
| BUG-002 | Favicon 404 | 🟢 Low | [UI] | Defer |

---

### 3. Features Implemented ✅

| Feature | Owner | Date |
|---------|-------|------|
| Guest Mode (Frontend) | [UI] | 2026-01-18 |
| /auth/guest endpoint | [CODE] | 2026-01-18 |
| System Ops in Legacy UI | [UI] | 2026-01-17 |
| Pre-warm automation | [CODE] | 2026-01-17 |
| Cold run optimization | [CODE] | 2026-01-17 |

---

### 4. Documents Updated 📄

| Document | Owner | Status |
|----------|-------|--------|
| `product/software_stack.md` | [PL][CODE][UI] | ✅ Updated |
| `product/test_plan.md` | [CV] | ✅ Updated |

---

### 5. Deployment Status

| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ |
| Local Frontend | http://localhost:3000 | ✅ |
| Zeabur | martian-app.zeabur.app | ⚠️ Needs recheck after push |

---

## How to Run the APP

### Local Development

```bash
# Terminal 1: Backend
cd /home/terwu01/github/martian
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd /home/terwu01/github/martian/frontend
npm run dev

# Access:
# - New Frontend: http://localhost:3000
# - Legacy UI: http://localhost:8000
```

---

**Next Actions:**
1. Wait for Zeabur redeploy
2. [CV] Run Playwright tests on production
3. [PL] Final verification with Boss

**Meeting Adjourned: 01:00 UTC+8**
