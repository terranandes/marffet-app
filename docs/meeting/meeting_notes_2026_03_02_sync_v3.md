# Agents Sync Meeting - 2026-03-02 v3
**Date:** 2026-03-02 16:28 HKT
**Topic:** VIP vs PREMIUM Tier Definition, GitHub Public Publishing Strategy, Membership Injection & Sponsorship Recap

## Attendees
- **[PM] Terran**: BOSS, directives on VIP/PREMIUM diff & GitHub publishing
- **[PL] (Antigravity)**: Meeting lead, worktree cleanup, task tracking
- **[SPEC]**: Tier enforcement architecture, public repo structure proposal
- **[CODE]**: Backend `auth.py` gating analysis, `.gitignore` audit
- **[UI]**: Frontend `is_premium` gating audit (3 files), sponsor tab integration
- **[CV]**: Security audit on repo exposure risk, JIRA triage

---

## 1. Project Live Progress (`docs/product/tasks.md`)

### Completed This Session (Since v2 Meeting)
| Item | Status | Details |
|------|--------|---------|
| VIP/PREMIUM Injection (Backend) | ✅ Complete | `user_memberships` table in `portfolio.db`, admin API endpoints |
| VIP/PREMIUM Injection (Frontend) | ✅ Complete | Admin Dashboard form + active membership table |
| Tier Precedence Logic | ✅ Complete | `GM > VIP > PREMIUM` in `/auth/me` merging static + dynamic |
| Sponsorship Links (Sidebar) | ✅ Complete | "Sponsor Us" button above user panel |
| Sponsorship Links (Settings) | ✅ Complete | New "☕ Sponsor Us" tab in SettingsModal |
| i18n Sponsor Keys | ✅ Complete | `en.json`, `zh-TW.json`, `zh-CN.json` |
| Document Flow | ✅ Complete | Updated 11 product docs with membership & sponsorship info |
| Push to GitHub | ✅ Complete | Commit `6eb65ff` pushed to `origin/master` |

### Open Work
| Item | Status | Priority |
|------|--------|----------|
| i18n Phase 3 (~40% pages pending) | 🔄 In Progress | Medium |
| VIP vs PREMIUM Feature Gating | 🆕 Needs Planning | **HIGH** — Boss Focus |
| GitHub Public Repo | 🆕 Needs Execution | **HIGH** — Boss Focus |
| BUG-010-CV (Mobile Card Timeout) | OPEN | Low (deferred) |

---

## 2. Focus Topic: VIP vs PREMIUM Tier Definition

### Current State Analysis
- Backend `auth.py` returns `tier` field (`FREE`, `VIP`, `PREMIUM`, `GM`) and boolean `is_premium`.
- `is_premium = true` only for `PREMIUM` and `GM` tiers. VIP gets `is_premium = false`.
- Frontend gates on `is_premium` in 3 files: `race/page.tsx`, `viz/page.tsx`, `AICopilot.tsx`.
- **Result: VIP currently = Free functionally.** Zero differentiation.

### Proposed Tier Matrix (PM Recommendation)

| Feature | Guest | Free | PREMIUM | VIP | GM |
|:--------|:------|:-----|:--------|:----|:---|
| Mars Strategy | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bar Chart Race | Basic | Basic | **CAGR Metrics** | CAGR Metrics | Full |
| Compound Interest | ✅ | ✅ | ✅ | ✅ | ✅ |
| Portfolio Groups | 3 | 11 | **20** | 30 | ∞ |
| Targets/Group | 10 | 50 | **100** | 200 | ∞ |
| Transactions/Target | 10 | 100 | **500** | 1,000 | ∞ |
| AI Copilot | ❌ | Educator | **Educator** | Wealth Manager | Full |
| CB Notifications | ❌ | ❌ | **In-App** | In-App + Email | Full |
| Rebalancing Alerts | ❌ | ❌ | ❌ | ✅ In-App + Email | Full |
| Data Export | ❌ | Unfiltered | **Unfiltered** | Filtered Excel | Full |
| Advanced Viz | ❌ | ❌ | **✅** | ✅ | ✅ |

### PREMIUM Key Differentiators (vs Free)
PREMIUM unlocks BCR CAGR metrics, Advanced Viz, higher capacity limits, and In-App CB notifications — but NOT the Ruthless Wealth Manager AI or Email Alerts.

### VIP Key Differentiators (vs PREMIUM)
VIP additionally unlocks the Wealth Manager AI, Email Alerts, Filtered Excel Export, and even higher capacity limits. VIP is the top paid tier.

### Implementation Plan (Deferred to Next Sprint)
1. Backend: Add `is_vip` boolean to `/auth/me` response (or use `tier` string).
2. Frontend: Refactor gating from `is_premium` to tier-aware checks.
3. Backend: Add tier-aware limits in portfolio CRUD endpoints.

**Status: BOSS APPROVAL NEEDED on the tier matrix before implementation.**

---

## 3. Focus Topic: GitHub Public Publishing Strategy

### Problem
BOSS wants to publish on GitHub to promote the product. The current private repo (`terranandes/martian`) contains:
- All source code (Python backend, Next.js frontend)
- `app/portfolio.db` (user data backup)
- `Dockerfile` (infrastructure details)
- `data/backup/*.parquet` (6M+ rows market data)
- `.env.example`, scripts, tests, agent configs

**This repo MUST remain private.**

### Recommendation: Separate Public Repo (Option A — Unanimous)

Create `terranandes/martian-app` (or `marffet` if renaming):

```
martian-app/                    # PUBLIC repo
├── README.md                   # Product showcase (EN + zh-TW + zh-CN combined)
├── LICENSE                     # MIT or chosen
├── screenshots/                # App screenshots
│   ├── mars_strategy.png
│   ├── portfolio.png
│   └── ...
└── .github/
    └── FUNDING.yml             # GitHub Sponsor button (ko_fi + buy_me_a_coffee)
```

### What Goes in the Public README
- Product description from `docs/product/README.md` (zero technical details)
- Feature list with screenshots
- Live app URL: `https://martian-app.zeabur.app`
- Sponsorship links (Ko-fi, Buy Me a Coffee)
- zh-TW and zh-CN sections appended

### What NEVER Goes Public
- Source code (Python, TypeScript, configs)
- Database files, Parquet backups
- Docker/deployment configs
- `.env`, API keys, agent rules
- Technical architecture docs

### Security Audit (CV)
- `.gitignore` correctly blocks `.env`, `*.db`, `*.duckdb` ✅
- `app/portfolio.db` is committed (backup mechanism) — **private repo only** ✅
- No secrets in git history (verified via `git ls-files` audit) ✅
- `.github/FUNDING.yml` is the proper GitHub-native mechanism for sponsor buttons ✅

**Status: BOSS APPROVAL NEEDED on repo name and timing before execution.**

---

## 4. Bug Triage (JIRA)

| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-010-CV | OPEN | Mobile Portfolio Card Click Timeout. Deferred. |
| All others (0-9, 11) | CLOSED | Resolved in prior phases. |

No new bugs filed.

---

## 5. Worktree / Branch / Stash Cleanup

| Item | Before | After |
|------|--------|-------|
| `.worktree/PL_full-test-local` | Active (idle) | **REMOVED** ✅ |
| `.worktrees/PL_full-test-local` | Active (idle) | **REMOVED** ✅ |
| Branch `PL-test-i18n` | Local only | **DELETED** ✅ |
| Branch `PL_full-test-local-branch` | Local only | **DELETED** ✅ |
| Stashes | None | ✅ Clean |

**Current state: Only `master` branch remains. Clean workspace.**

---

## 6. Deployment Status
- **Local:** Running via `./start_app.sh` (ports 8000/5173). All features working.
- **Zeabur:** Up to date with `origin/master` (commit `6eb65ff`).
- **Public Repo:** Not yet created. Pending BOSS approval.

---

## [PL] Summary Report to Terran

> **Boss, here are the two decisions that need your input:**
>
> **1. VIP vs PREMIUM Tier Matrix:**
> I've drafted a concrete feature differentiation table. VIP would unlock BCR CAGR metrics, Advanced Viz, higher capacity limits, and In-App CB notifications — but NOT the Ruthless Wealth Manager AI, Email Alerts, or Filtered Exports. Those stay PREMIUM-exclusive. **Please review the table above and confirm or adjust.**
>
> **2. GitHub Public Publishing:**
> We unanimously recommend creating a **separate public repo** (e.g., `terranandes/martian-app`) containing only product READMEs, screenshots, and sponsor links. The current private repo stays untouched. We'll also add a `.github/FUNDING.yml` for the native GitHub Sponsor button. **Please confirm the repo name and I'll execute it.**
>
> **Housekeeping:** All worktrees and stale branches have been cleaned up. Workspace is now clean — only `master` remains.

---

## Next Actions
1. [BOSS] Approve VIP vs PREMIUM tier matrix → [CODE] implements backend gating
2. [BOSS] Confirm public repo name (`martian-app` vs `marffet`) → [PL] creates repo with `gh`
3. [PL] Continue i18n Phase 3 string extraction
4. [PL] Save meeting notes → `commit-but-push`
