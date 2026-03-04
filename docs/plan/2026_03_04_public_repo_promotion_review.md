# Plan Review: Public Repo `marffet-app` for Promotion

**Date:** 2026-03-04
**Reviewers:** [PM], [SPEC], [CODE], [UI], [CV]

---

## Multi-Agent Brainstorming Review

### [PM] Product Review — ✅ APPROVED with additions
- Option A (showcase) is correct for user/investor target → no code exposure risk
- Language switcher links are essential for the Taiwan market reach
- **Suggestion**: Leverage `social_media_promo.md` copy in the GitHub repo description
- **Suggestion**: Screenshots should highlight the most visually impressive views — compound chart, bar chart race, portfolio donut

### [SPEC] Architecture Review — ✅ APPROVED with note
- Discrepancy analysis is thorough; spec is the single source of truth
- **Note**: Plan correctly identifies 9 discrepancies but should also verify `datasheet.md` tier table for consistency
- **Note**: Should cross-check `config.py` tier limits (20/100/500) against spec to ensure backend matches

### [CODE] Implementation Review — ✅ APPROVED with prerequisite
- **Blocker**: `gh` CLI needs auth — `gh auth login` must be run first by BOSS, or use raw `git` commands
- LICENSE should be explicit: "All Rights Reserved" for proprietary (no MIT/Apache since no code shared)
- Playwright screenshot generation is solid — note Zeabur cold starts (10-15s) should be handled with `waitFor`

### [UI] Design Review — ✅ APPROVED with guidance
- Screenshots should be 1920×1080 for GitHub's optimal rendering
- Use **dark mode** screenshots to match the cyberpunk aesthetic
- **Suggestion**: Consider a hero banner image at the top of the README using `generate_image` tool
- Ensure screenshots have consistent padding and no visible browser chrome

### [CV] Security Review — ✅ APPROVED
- No security concerns with Option A (zero code exposure)
- **Check**: Should verify no `localhost` URLs or internal API paths leak into the READMEs before publishing
- The `gh auth` blocker should be noted as a prerequisite

---

## Consensus Additions to Plan

1. ✅ Add `gh auth login` prerequisite or fallback to raw `git` commands
2. ✅ LICENSE: "All Rights Reserved" (no open-source license needed for showcase)
3. ✅ Verify `datasheet.md` tier table matches spec (add to Part C)
4. ✅ Dark mode, 1920×1080 screenshots
5. ✅ Add GitHub repo description from `social_media_promo.md` tagline
6. ✅ Sanitize all READMEs for any `localhost` references before publishing

---

**Review outcome: APPROVED — proceed to execution with above additions.**
