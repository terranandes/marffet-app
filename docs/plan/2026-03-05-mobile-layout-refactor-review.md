# Plan Review: Mobile Layout Refactor (Multi-Agent Brainstorming)

**Plan:** `docs/plan/2026-03-05-mobile-layout-refactor.md`
**Date:** 2026-03-05
**Disposition:** ✅ APPROVED with amendments

---

## 2️⃣ Skeptic / Challenger Agent

| # | Objection | Severity | Resolution |
|---|-----------|----------|------------|
| S1 | iOS Safari horizontal scroll can feel non-native | Medium | Add `scroll-snap-type: x mandatory` + `scroll-snap-align: center` for snappy tab swiping |
| S2 | 8-9 tabs at ~60px ≈ 540px; user sees ~6.5 on 390px screen, rest hidden behind scroll | Low | Same as reference app pattern. Acceptable by user directive |
| S3 | `SettingsModal` returns `null` if `!user` (line 169). Logged-out users can't open Settings to log in | **High** | **Must modify** SettingsModal to render in logged-out state for auth access |
| S4 | Removing sidebar hamburger is a UX breaking change | Low-Med | Bottom tabs provide better access. No action needed |
| S5 | Top bar (56px) + bottom bar (64px+safe area) = ~140px lost vertically | Medium | Standard app pattern. User explicitly requested this layout |

---

## 3️⃣ Constraint Guardian Agent

| Area | Verdict | Notes |
|------|---------|-------|
| Performance | ✅ | No new API calls; UserContext already polls notifications |
| Desktop regression | ✅ | All new code behind `lg:hidden`; sidebar cleanup removes mobile-only code |
| Bundle size | ✅ | No new libraries; Framer Motion already installed |
| SEO/SSR | ✅ | Nav components are client-only — appropriate for navigation |

---

## 4️⃣ User Advocate Agent

| # | Observation | Suggestion | Accepted? |
|---|-------------|------------|-----------|
| U1 | Logged-out users might not find Sign In inside ⚙️ | Show pulsing dot or "Sign In" label on ⚙️ when not logged in | ✅ Accepted |
| U2 | FREE tier badge might annoy users seeing "FREE" constantly | Use muted styling for FREE; proud badge for paid tiers | ✅ Partially accepted |
| U3 | Notification bell for logged-out users? | Keep hidden for logged-out (matches desktop) | ✅ Accepted |

---

## 5️⃣ Integrator / Arbiter Decisions

### Amendments to Original Plan

1. **Task 3 (SettingsModal):** Must explicitly handle `!user` state — allow rendering the modal with a "Sign In" prompt when user is null. Remove the `if (!isOpen || !user) return null` guard and instead conditionally render auth-only content when `!user`.

2. **Task 2 (BottomTabBar):** Add `scroll-snap-type: x mandatory` to the tab strip and `scroll-snap-align: center` to each tab for native-feeling momentum scrolling on iOS.

3. **Task 2 (BottomTabBar):** When user is NOT logged in, the ⚙️ button should display a subtle "Sign In" text below the gear icon (like other tab labels) instead of "Settings".

4. **Task 1 (MobileTopBar):** FREE tier uses muted zinc color. Only show tier badge when user is logged in.

### Final Verdict

> The plan is **APPROVED** with the 4 amendments above incorporated. All reviewer objections are resolved or explicitly accepted.
