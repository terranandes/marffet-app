# Meeting Notes — 2026-03-03 Agents Sync v2
**Date:** 2026-03-03 16:30 HKT
**Attendees:** [PL], [PM], [CODE], [CV], [UI], [SPEC], BOSS (Terran)

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 25: Marffet Rebrand & Tier Gating | ✅ COMPLETED | All code changes done. BOSS tasks pending (repo rename, Zeabur). |

### 2. Commits Ahead of Origin

**7 commits on `master` ahead of `origin/master`** (not yet pushed):

| # | Commit | Description |
|---|--------|-------------|
| 1 | `1cc2f3a` | Plan + Review docs for rebrand |
| 2 | `24a1c2c` | Agents sync v5 — i18n reconciliation |
| 3 | `68a3c1d` | Agents sync v4 — BUG-012 code review |
| 4 | `7fcacbe` | **feat(rebrand)**: Martian → Marffet (21 files) |
| 5 | `64b6aff` | docs: meeting notes + BOSS checklist |
| 6 | `9614f2b` | fix: swap repo names (BOSS typo correction) |
| 7 | This session | fix: remaining Martian refs + full doc sweep |

### 3. Code Review

**Verdict: ✅ PASS** (Ref: `docs/code_review/code_review_2026_03_03_sync_v1.md`)

- All frontend/backend code clean of "Martian" (except intentional etymology "(Martian + Buffet)")
- All 14 product docs updated
- Root README.md updated
- Frontend build: ✅ All 13 routes compile

### 4. Jira Triage

| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-000 to BUG-009 | CLOSED | From previous phases |
| BUG-010 | OPEN (Deferred) | Mobile portfolio card click timeout — low priority |
| BUG-011 | CLOSED | Portfolio transaction edit failure — fixed |
| **Total: 11/12 CLOSED** | | |

No new bugs discovered during this session.

### 5. Worktree / Branch / Stash Status

| Item | Status |
|------|--------|
| Worktrees | ✅ Clean — only main worktree |
| Branches | ✅ Clean — only `master` |
| Stashes | ✅ Clean — none |
| Remote branches | ✅ Clean — only `origin/master` |

### 6. Deployment Completeness (`marffet-app.zeabur.app`)

| Item | Status |
|------|--------|
| Code rebrand complete | ✅ |
| Frontend build passes | ✅ |
| CORS origins updated | ✅ `marffet-app.zeabur.app` / `marffet-api.zeabur.app` |
| Pushed to origin | ❌ Not yet (pending BOSS approval) |
| Zeabur service rename | ❌ Pending BOSS manual action |
| Google OAuth redirect update | ❌ Pending BOSS manual action |
| `.env` FRONTEND_URL update | ❌ Pending BOSS manual action |
| `.env` GITHUB_REPO update | ❌ Pending BOSS manual action |

### 7. Private GitHub Repo (`terranandes/marffet`)

| Item | Status |
|------|--------|
| Code rebrand | ✅ Complete |
| Product docs updated | ✅ Complete |
| `backup.py` GITHUB_REPO comment | ✅ Updated to `terranandes/marffet` |
| Repo rename on GitHub | ❌ Pending BOSS manual action |

### 8. Public GitHub Repo (`terranandes/marffet-app`)

| Item | Status |
|------|--------|
| Repository created | ❌ Pending BOSS manual action |
| Product READMEs ready | ✅ (EN, zh-TW, zh-CN all updated) |

### 9. Product Document Sweep

**[PM]** completed full document-flow sweep. 14 product docs + root README updated:

| Document | Status |
|----------|--------|
| `README.md` (root) | ✅ |
| `docs/product/README.md` | ✅ |
| `docs/product/README-zh-TW.md` | ✅ |
| `docs/product/README-zh-CN.md` | ✅ |
| `docs/product/specification.md` | ✅ |
| `docs/product/datasheet.md` | ✅ |
| `docs/product/software_stack.md` | ✅ |
| `docs/product/social_media_promo.md` | ✅ |
| `docs/product/admin_operations.md` | ✅ |
| `docs/product/backup_restore.md` | ✅ |
| `docs/product/crawler_architecture.md` | ✅ |
| `docs/product/duckdb_architecture.md` | ✅ |
| `docs/product/mars_strategy_bcr.md` | ✅ |
| `docs/product/test_plan.md` | ✅ |
| `docs/product/tasks.md` | ✅ |

### 10. Known Advisory

| Item | Severity | Notes |
|------|----------|-------|
| `martian_banner.png` file not renamed | Low | OG image filename only — no user-visible impact |
| localStorage keys renamed | Info | Existing users lose saved preferences (BOSS-approved) |
| BUG-010 still open | Low | Mobile portfolio card click — deferred |

---

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Push `master` to origin | BOSS | High |
| 2 | Rename private repo to `terranandes/marffet` | BOSS | High |
| 3 | Create public repo `terranandes/marffet-app` | BOSS | Medium |
| 4 | Rename Zeabur services + update env vars | BOSS | High |
| 5 | Update Google OAuth redirect URIs | BOSS | High |
| 6 | Test full OAuth flow post-deploy | BOSS | High |
| 7 | Consider renaming `martian_banner.png` → `marffet_banner.png` | [CODE] | Low |

---

**Meeting adjourned at 16:50 HKT.**
