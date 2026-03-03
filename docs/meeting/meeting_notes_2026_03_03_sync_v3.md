# Meeting Notes — 2026-03-03 Agents Sync v3
**Date:** 2026-03-03 20:10 HKT
**Attendees:** [PL], [PM], [SPEC], [CODE], [CV], [UI], BOSS (Terran)

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 25: Marffet Rebrand & Tier Gating | ✅ COMPLETED | All code + docs complete. BOSS tasks done. |
| Phase 23: UI/UX Polish | ✅ Phase A-F COMPLETED | BUG-010 deferred (low priority) |

### 2. Git Status

| Item | Status |
|------|--------|
| Branch | `master` — even with `origin/master` (f0e0921) |
| Worktrees | ✅ Clean — only main worktree |
| Branches | ✅ Clean — only `master` + `origin/master` |
| Stashes | ✅ Clean — none |
| Untracked | 3 test evidence PNGs (gitignored) |

### 3. JIRA Triage

| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-000 through BUG-009 | CLOSED | From previous phases |
| BUG-010 | OPEN (Deferred) | Mobile portfolio card click timeout — low priority |
| BUG-011 | CLOSED | Portfolio transaction edit failure — fixed |
| **Total: 11/12 CLOSED** | | No new bugs this session |

### 4. Deployment Completeness

| Check | Result |
|-------|--------|
| `marffet-app.zeabur.app` | ✅ HTTP 200 |
| `marffet-api.zeabur.app/health` | ✅ `{"status":"healthy","service":"marffet-backend","version":"1.0.2"}` |
| Frontend build | ✅ 13 routes compile (exit code 0) |
| Repo rename | ✅ Complete (terranandes/marffet) |
| Public repo | ✅ Complete (terranandes/marffet-app) |

### 5. Document Flow — Tier Definition & Rebrand Cleanup

**BOSS requested formal tier definition (Guest → FREE → PREMIUM → VIP → GM).** This session formalized the complete 5-tier access model across all product documentation.

**Residual Findings:** 10 product docs still contained `martian-app.zeabur.app`, `martian-api.zeabur.app`, `terranandes/martian`, and `martian_premium` references from the v2 rebrand sweep that only covered code files.

#### [SPEC] Updates
| Document | Change |
|----------|--------|
| `specification.md` | v4.0 → v5.0: Full 5-tier access matrix, feature comparison table, tier definitions, URLs updated, changelog added |
| `auth_db_architecture.md` | v1.0 → v2.0: Complete rewrite. 5-tier model with precedence logic, env vars, DB injection, frontend sync, sponsorship flow |
| `backup_restore.md` | Fixed `GITHUB_REPO` example `terranandes/martian` → `terranandes/marffet` |
| `mars_strategy_bcr.md` | Fixed `martian_premium` → `marffet_premium` localStorage key |

#### [PM] Updates
| Document | Change |
|----------|--------|
| `README.md` (product) | URL fixed, "Free vs Premium" → "Membership Tiers" 5-column table, v5.0 |
| `README-zh-TW.md` | URL fixed: `martian-app` → `marffet-app` |
| `README-zh-CN.md` | URL fixed: `martian-app` → `marffet-app` |
| `social_media_promo.md` | All 6 URLs fixed globally |
| `datasheet.md` | 3-column → 5-column tier table, VIP vs PREMIUM description added |

#### [PL][CODE][UI] Updates
| Document | Change |
|----------|--------|
| `software_stack.md` | Already current ✅ — no changes needed |

#### [CV] Updates
| Document | Change |
|----------|--------|
| `test_plan.md` | v4.2 → v5.0: URLs fixed, TC-25 added (tier matrix test), tier precedence order corrected, Zeabur frontend env added |

### 6. Code Review

**Verdict: ✅ PASS** (Ref: `docs/code_review/code_review_2026_03_03_sync_v2.md`)

- 10 files changed, 205 insertions, 80 deletions — all documentation-only
- Zero residual `martian-*` references in `docs/product/` (verified via grep)
- No code files modified — zero risk of runtime regression
- Tier definitions are consistent across all 4 specification-level documents

### 7. BOSS_TBD Status Check

| Item | Status |
|------|--------|
| ✅ Multi-language | Completed (Phase 22) |
| ✅ Buy-me-coffee buttons | Completed (Phase 24) |
| ✅ Rename Martian to Marffet | Completed (Phase 25) |
| ✅ Rename private repo | Completed by BOSS |
| ✅ Create public repo | Completed by BOSS |
| ✅ Rename Zeabur services | Completed by BOSS |
| **[NEW]** Define GM/VIP/PREMIUM/FREE/Guest | ✅ **Formalized this session** |
| ⏳ Publish to GitHub (public showcase) | Pending BOSS |
| ⏳ Adjust license to MIT | Pending BOSS |
| ⏳ Add buy-me-coffee to public README | Pending BOSS |
| ⏳ Accounts-over-time chart on GM Dashboard | Not started |
| ⏳ Google advertisement | Not started |
| ⏳ AICopilot enhancement | Not started |
| ⏳ Cloud Run evaluation | Not started |
| ⏳ DB/Warm Static optimization | Not started |
| ⏳ Email support | Not started |

---

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Review the 5-tier definitions and confirm VIP vs PREMIUM differentiation | BOSS | Medium |
| 2 | Publish product README to public repo `terranandes/marffet-app` | BOSS | Medium |
| 3 | Address remaining BOSS_TBD items (accounts chart, ads, AICopilot, Cloud Run) | [PL] + BOSS | Low |
| 4 | Investigate BUG-010 (mobile portfolio card click) after next UI sprint | [UI] | Low |

---

**Meeting adjourned at 20:15 HKT.**
