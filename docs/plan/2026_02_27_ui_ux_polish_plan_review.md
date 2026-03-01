# Plan Review — UI/UX Polish (Phase 23)
**Date:** 2026-02-27
**Reviewers:** [CV], [SPEC], [PM], [CODE]

---

## Agent Reviews

### [CV] — Security & Risk
- **Phase A (GM Dashboard):** `localStorage` for collapse state is fine. No auth concerns.
- **Phase C (AI Bot):** Storing chat history in `localStorage` is acceptable since it's user-side only. However, limit payload size (20 messages cap is good).
- **Phase D (Notifications):** Backend engine triggers must respect user subscription tier — Free users should NOT receive Premium-only CB alerts.
- **Verdict:** ✅ No blockers.

### [SPEC] — Architecture
- **Phase B3:** Adding categories to `feedback_db.py` is a trivial dict append — zero risk.
- **Phase D1:** The `NotificationEngine` pattern is already scaffolded in `app/engines/`. The CB premium calculation should reuse existing `ROICalculator` logic, not duplicate it.
- **Phase E:** Loading skeletons should use a shared `<Skeleton />` component, not inline per-page.
- **Verdict:** ✅ Architecturally sound. Recommend shared Skeleton component.

### [PM] — User Impact
- **Execution Order Approved:** Settings (quick win) → Dashboard (GM visibility) → Notifications → AI Bot → Cross-Tab.
- **Concern:** Phase C is blocked on BUG-001-CV. Boss must enable GCP API or we skip it entirely.
- **Suggestion:** Phase A should be highest priority since Boss uses the admin dashboard daily.
- **Verdict:** ✅ Approved with priority adjustment: A before B.

### [CODE] — Feasibility
- **Phase A:** Refactoring 795-line `admin/page.tsx` into collapsible sections is feasible using `<details>` or a custom `CollapsibleCard` component. ~2 hours.
- **Phase B5:** Component decomposition is P2 and optional. The 36KB file works fine as-is.
- **Toast Library:** Recommend `react-hot-toast` (5KB gzip, zero deps, SSR-safe). Already compatible with our Next.js setup. No need to roll a custom one.
- **Verdict:** ✅ All phases feasible within estimates.

---

## Consensus Adjustments

| Original | Adjusted |
|:---------|:---------|
| Phase B first | **Phase A first** (Boss uses daily) |
| Custom toast system | **`react-hot-toast`** library |
| Phase B5 (split SettingsModal) | Deferred to P3 |

## Final Execution Order
1. **Phase A** — GM Dashboard Overhaul
2. **Phase B** — Settings Modal + Feedback Categories
3. **Phase D** — Notification Engine Triggers
4. **Phase C** — AI Bot Polish (blocked on GCP)
5. **Phase E** — Cross-Tab Skeletons & Animations
