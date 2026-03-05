# Code Review — 2026-03-06 Sync v1
**Date:** 2026-03-06  
**Reviewer:** [CV]  
**Target:** 6 commits (`27b43b3`→`8e061a8`) — Phase 31 Mobile App-Like Experience + Sidebar Reorder

## 1. Scope

Files modified (41 files, ~1,988 insertions, ~517 deletions):

| Commit | Scope | Risk |
|--------|-------|------|
| `27b43b3` | Docs only (meeting notes, plan, tasks) | LOW |
| `991af7a` | CSS + layout (breakpoints, safe areas) | LOW |
| `9f5dd4f` | **Architecture** (UserContext extraction, BottomTabBar) | **HIGH** |
| `bea5641` | PWA (manifest, service worker, icons, CSS) | MEDIUM |
| `99fa5fc` | UI (PageTransition, TargetList fixes) | LOW |
| `980c075` | **Large refactor** (MobileTopBar, SettingsModal, BottomTabBar, Sidebar) | **HIGH** |
| `8e061a8` | Sidebar tab order swap | LOW |

## 2. Findings

| Item | Result | Notes |
|------|--------|-------|
| UserContext.tsx architecture | ✅ PASS | Clean context extraction with `useUser()` hook |
| BottomTabBar.tsx | ✅ PASS | Proper pathname detection, i18n, "More" popup |
| MobileTopBar.tsx | ✅ PASS | Clean responsive top bar with notifications |
| PageTransition.tsx | ✅ PASS | Framer Motion fade wrapper in template.tsx |
| PWA manifest.json | ✅ PASS | `minimal-ui` display, correct theme colors |
| Service worker (sw.js) | ✅ PASS | Versioned cache, network-first API, offline fallback |
| globals.css safe areas | ✅ PASS | `env(safe-area-inset-*)` properly used |
| Mars page table scroll | ✅ PASS | `overflow-x-auto` + `min-w-[500px]` for mobile |
| AICopilot FAB position | ✅ PASS | `bottom-[90px]` clears BottomTabBar |
| SettingsModal close/auth | ✅ PASS | Close button + sign in/out restored |
| Sidebar.tsx tab order | ✅ PASS | Portfolio before CB correctly |
| **Sidebar.tsx User Profile** | **❌ FAIL** | Sign In/Guest/Sign Out UI removed during auth refactor |
| Workflow files updated | ✅ PASS | `full-test.toml` and `full-test-local.toml` include mobile |

## 3. Critical Regression

**`Sidebar.tsx` — User Profile Section Missing**

During commit `9f5dd4f` (Phase 2), auth logic was correctly extracted to `UserContext.tsx`. However, the UI rendering of the User Profile section (sign-in/guest/sign-out buttons) was also removed from the desktop sidebar JSX.

**Impact:** Desktop users cannot sign in, sign out, or switch to guest mode from the sidebar. E2E tests fail because the "Guest" button locator times out.

**Fix Location:** A partial fix exists in worktree `test-run-1772731926` (`Sidebar.tsx` line 281-436 restored) but has a minor JSX error (extra `</div>` tag) which was also fixed in the worktree.

**Recommendation:** Apply the worktree fix to `master`, rebuild, and run E2E.

## 4. Code Risk

**Risk Level: MEDIUM** — Architecture is clean but one regression blocks E2E testing. No backend changes. No business logic modified. PWA additions are additive and non-breaking.

## 5. Conclusion

**Status: CONDITIONAL PASS ⚠️**

All new code (UserContext, BottomTabBar, MobileTopBar, PWA, transitions) is well-structured and follows established patterns. One regression in `Sidebar.tsx` must be fixed before the Phase 31 milestone is fully complete.
