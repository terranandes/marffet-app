# Agents Sync Meeting - 2026-02-27 Sync 0130

**Date:** 2026-02-27 01:30 HKT
**Status:** Active
**Agents:** [PL], [PM], [SPEC], [CV], [UI], [CODE]

## 1. Project Live Progress & Status `[PL]`
- Ongoing focus on Phase 17/18 Data Integrity and discrepancy fixes.
- Git Worktree/Branch/Stash: `master` branch is clean. No lingering stashes or rogue branches.

## 2. Bug Triages & End-User Feedback `[CV]` & `[PM]`
- **TSMC 2006 BCR Discrepancy (End-User reported):** 
  - *Finding:* BCR duplicate year bug was fixed by `[CODE]` (`start_year - 1` baseline offset applied). 
  - *Mismatch Analysis:* MoneyCome reported Final Value 1.25M vs our 1.23M for TSMC 2006. Reverse-engineering shows MoneyCome calculates Year 1 (2006) Cash Dividend as exactly 40,969 across *all* strategies (BAO, BAH, BAL). This mathematically proves MoneyCome uses a static share calculation for Year 1 (likely based on the previous year's close or an arbitrary VWAP of ~61.02) rather than the actual strategy execution price.
  - *Resolution:* `[PM]` decides our current mathematical engine (`roi_calculator.py`) is technically superior and accurate (calculating distinct dividends based on actual purchase prices). We will **defer** aligning to MoneyCome's bugged Year 1 logic.
- **BUG-110-CV (Local Frontend Env Missing):** Pending full-test workflow generation.
- **BUG-111-CV (Zeabur Copilot Auth):** Blocked on Boss enabling GCP Generative Language API.
- **BUG-114-CV (Mobile Portfolio click timeout):** E2E test timeout. Low priority.
- **BUG-115-PL (YFinance Adj Div Mismatch):** Fixed through Phase 18 DuckDB nominal rebuild.

## 3. Discrepancy: Local vs Deployment `[CV]`
- Zeabur deployment matches local DuckDB instances exactly for Mars simulation. Memory streaming chunk logic works flawlessly. No discrepancy in calculation; the only discrepancy is against legacy MoneyCome logic.

## 4. UI/UX Review `[UI]`
- Mobile Web Layout requirements discussed. Current UI cards for Portfolio need tap target enhancement to avoid BUG-114-CV failures. Next phase will focus on elegant "Premium UI" overhauls.

## 5. Artifact & Plan Multi-Agent Brainstorming `[SPEC]`
- Investigated whether to build an entirely new "MoneyCome Exact Match" calculation toggle. 
- *Decision:* Unnecessary complexity. We will formally document the legacy MoneyCome Year 1 dividend inaccuracy in our `docs/product/` architecture definitions. Our DuckDB Nominal Price engine + BAO/BAH/BAL logic will be the new gold standard.
- `docs/product/tasks.md` remains the central source of truth for ongoing fixes.

## 6. Next Actions `[PL]`
- Finalize Code Review for `roi_calculator.py`.
- Commit all documentation updates (`commit-but-push` workflow).
