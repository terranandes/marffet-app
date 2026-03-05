# Plan Review: Mobile App-Like Experience

**Reviewed:** 2026-03-05
**Plan:** `docs/plan/2026-03-05-mobile-app-like-experience.md`
**Method:** Multi-Agent Brainstorming (Skeptic → Constraint Guardian → User Advocate → Integrator)

---

## Skeptic / Challenger Findings

| ID | Objection | Severity |
|----|-----------|----------|
| S1 | Auth state lives in Sidebar, but BottomTabBar also needs it → duplication risk | 🔴 High |
| S2 | "More" drawer with swipe-to-dismiss is over-engineered for MVP | 🟡 Medium |
| S3 | Service Worker without proper cache-busting → stale deploys | 🟡 Medium |
| S4 | Card layout for Mars 50-row table breaks comparative scanning | 🟡 Medium |

## Constraint Guardian Findings

| ID | Constraint | Severity |
|----|------------|----------|
| C1 | Framer Motion page transitions may cause jank on low-end Android | 🟡 Medium |
| C2 | `"display": "standalone"` removes browser chrome → user can't "Request Desktop Site" | 🔴 **CRITICAL** |
| C3 | Must handle `safe-area-inset-top` for notched iPhones in PWA mode | 🟡 Medium |
| C4 | iPad Split View can create 320px viewport (below 375px minimum) | ⚪ Low |

## User Advocate Findings

| ID | Concern | Severity |
|----|---------|----------|
| U1 | Tab icons need visible labels (not icon-only) | 🟡 Medium |
| U2 | Hiding 3+ features behind "More" reduces discoverability | ⚪ Low |

---

## Integrator Decisions

| # | Resolution | Action |
|---|------------|--------|
| S1 | **ACCEPTED** | Lift auth state to `ClientProviders` context; BottomTabBar consumes it |
| S2 | **ACCEPTED** | Simplify "More" to a popup list overlay, no swipe gestures in v1 |
| S3 | **ACCEPTED** | Add versioned cache names + `skipWaiting` + `clients.claim` to SW |
| S4 | **PARTIALLY ACCEPTED** | Use compact horizontal-scroll table with sticky rank column, not cards |
| C1 | **NOTED** | Prefer CSS `view-transition` API where supported; Framer as fallback |
| C2 | **ACCEPTED** | Change `"display": "standalone"` → `"display": "minimal-ui"` |
| C3 | **ACCEPTED** | Add safe-area-inset-top padding in PWA mode |
| C4 | **NOTED** | Document as known limitation |
| U1 | **ACCEPTED** | Always show text labels under tab bar icons |
| U2 | **NOTED** | Re-evaluate tab grouping after user feedback |

---

**Final Disposition: ✅ APPROVED with revisions**

*Reviewed by: [PL] using multi-agent-brainstorming skill*
