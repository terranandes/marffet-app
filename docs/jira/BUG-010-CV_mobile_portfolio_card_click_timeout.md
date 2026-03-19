# BUG-010 — Mobile Portfolio Card Click Timeout

**Type:** BUG  
**Serial ID:** 010  
**Reporter:** `[CV]` (Antigravity)  
**Date:** 2026-02-20  
**Status:** ✅ CLOSED (2026-03-20) — Addressed via Phase 37 mobile UI redesign and verified during mobile E2E testing passes.

---

## Discovery

**Discovered by:** `[CV]` during E2E test pass on Feb 20, 2026.

The mobile Portfolio card expand/collapse interaction timed out during Playwright E2E tests. The card tap target was not responding within the expected timeout window.

---

## Symptoms

- Mobile Portfolio card click does not expand/collapse reliably during E2E automation.
- Tap target appears insufficient on small screen viewports.
- Intermittent — passes on slower test runs but fails on fast Playwright automation.

---

## Status History

- `2026-02-20`: Discovered by `[CV]`. Filed.
- `2026-03-01`: Still OPEN. Deferred to next UI polishing sprint. Phase F brought card redesign which may partially address this — needs re-verification.

---

## Next Action

`[UI]` to verify after Phase F TargetCardList mobile redesign. If the new Framer Motion expand animation resolves the timeout, close this ticket.
