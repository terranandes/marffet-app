# Mobile Layout Refactor — App-Like Sliding Tabs

> **Review:** See [plan-review](./2026-03-05-mobile-layout-refactor-review.md) for multi-agent brainstorming results. Plan is **APPROVED** with 4 amendments incorporated below.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign the mobile bottom tab bar to use a horizontally-scrollable sliding tab system mirroring all desktop sidebar navigation items, with a fixed Settings tab, top-bar notification/tier indicators, and 1:1 feature parity between desktop and mobile.

**Architecture:** Replace the current 5-tab `BottomTabBar.tsx` (which uses a "More" popup to reach hidden pages) with a new two-zone bottom bar: a scrollable tab strip containing all 8-9 sidebar nav items (zone 3), and a fixed ⚙️ Settings button (zone 4). Add a mobile-only top bar with notification bell (zone 1) and tier badge (zone 2). The desktop sidebar remains untouched.

**Tech Stack:** Next.js 15 (App Router), React, Framer Motion, CSS custom properties

**Key Constraint:** Desktop experience MUST remain completely unchanged. All changes are behind `lg:hidden` / mobile-only breakpoints.

---

## Current State Analysis

### Desktop Sidebar (`Sidebar.tsx`)
- 9 navigation items: Mars Strategy, Bar Chart Race, Compound Interest, Convertible Bond, Portfolio, Trend Dashboard, My Portfolio Race, Cash Ladder, Admin Dashboard (GM-only)
- Notification bell (top-right of header)
- User auth card (bottom: avatar, nickname, sign-out)
- Sponsor button
- Settings modal trigger (gear icon inside user card)

### Current Mobile Bottom Bar (`BottomTabBar.tsx`)
- 5 fixed tabs: Mars, Portfolio, Race, Trend, More (⋯)
- "More" opens a popup grid with: Compound Interest, Convertible Bond, Cash Ladder, My Race, Admin
- **Problems:** Not all features are directly accessible; "More" popup is clunky; no notification/tier indicators on mobile; no settings/auth access from bottom bar

### SettingsModal (6 tabs)
- Profile, Preferences, AI Keys, Sponsor Us, Help, Support
- Already fully functional, opens as a full-screen modal overlay

### Backend `/auth/me` Response
- Already returns `tier` field (`FREE`, `PREMIUM`, `VIP`, `GM`)
- Also returns `is_admin`, `is_premium` booleans
- `UserContext.tsx` already exposes `user` and `notifications` globally

---

## Proposed Changes

### Component: MobileTopBar [NEW]

#### [NEW] `MobileTopBar.tsx` — `frontend/src/components/MobileTopBar.tsx`

A fixed top bar visible only on mobile (`lg:hidden`), positioned above the main content. Contains:
- **Zone 1 (left):** Notification bell with unread badge dot (reuse logic from `Sidebar.tsx` lines 122-174)
- **Zone 2 (right):** Tier badge button showing user's current tier (FREE/VIP/PREMIUM/GM) with color coding. Tap opens a small popover showing tier privileges summary.
- **Center:** "MARFFET" brand text or current page title

Implementation details:
- Consumes `useUser()` for `user`, `notifications`, `unreadCount`, `markAsRead`, `clearNotifications`
- **[AMENDMENT #4]** Tier colors: FREE = zinc-500 (muted/subtle), PREMIUM = yellow-400, VIP = purple-400, GM = amber-400/gold. Only show when user is logged in.
- Tier popover shows max groups/targets/transactions for the tier (reuse data from `SettingsModal.tsx` lines 483-490 Premium Features accordion)
- Notification dropdown renders below the bell, same as desktop but mobile-optimized (full-width)
- Height: `h-14` with `safe-area-inset-top` padding
- Background: `bg-[#050510]/95 backdrop-blur-xl border-b border-zinc-800/80`

---

### Component: BottomTabBar [MAJOR REWRITE]

#### [MODIFY] `BottomTabBar.tsx` — `frontend/src/components/BottomTabBar.tsx`

Complete rewrite with two-zone layout:

**Zone 3 — Sliding Tabs (left, ~85% width):**
- Horizontally scrollable `<nav>` with `overflow-x: auto` and `-webkit-overflow-scrolling: touch`
- Contains all 8 sidebar items (+ Admin Dashboard if GM):
  1. 🪐 Mars Strategy → `/mars`
  2. 📊 Bar Chart Race → `/race`
  3. 📈 Compound Interest → `/compound`
  4. � Portfolio → `/portfolio`  ← **moved up for first-glance visibility**
  5. � Convertible Bond → `/cb`
  6. 📈 Trend Dashboard → `/trend`
  7. ⏱️ My Portfolio Race → `/myrace`
  8. 🪜 Cash Ladder → `/ladder`
  9. ⚙️ Admin Dashboard → `/admin` (GM only, conditional)

> **Note:** This tab ordering applies to BOTH the mobile sliding tabs AND the desktop sidebar (`Sidebar.tsx`) for consistency.
- Active tab has: bottom indicator line, highlighted text color `var(--color-cta)`
- Auto-scroll to active tab on mount/route change using `scrollIntoView({ behavior: 'smooth', inline: 'center' })`
- Hide scrollbar with CSS: `scrollbar-width: none; -ms-overflow-style: none; ::-webkit-scrollbar { display: none }`
- **[AMENDMENT #2]** Add `scroll-snap-type: x mandatory` on container and `scroll-snap-align: center` on each tab for native iOS momentum feel
- Each tab: icon (emoji or SVG inline) + label text, compact layout `gap-0.5`

**Zone 4 — Fixed Settings Button (right, ~15% width):**
- Separated from sliding tabs by a subtle vertical divider (`border-l border-zinc-800`)
- Fixed ⚙️ icon button, does NOT scroll
- Opens the existing `SettingsModal` with `initialTab="profile"`
- The SettingsModal will need a new "Account" section added (see Task 3)
- **[AMENDMENT #3]** When user is NOT logged in, show "Sign In" label below ⚙️ icon instead of "Settings"
- Background slightly different shade to visually separate: `bg-zinc-900/80`

**Layout:**
```
┌──────────────────────────────────┬────┐
│ [Mars|Race|Comp|CB|Port|...→→]   │ ⚙️ │
└──────────────────────────────────┴────┘
```

---

### Component: Sidebar [MINOR MODIFY]

#### [MODIFY] `Sidebar.tsx` — `frontend/src/components/Sidebar.tsx`

- Remove the mobile hamburger toggle button (lines 85-98) — no longer needed since mobile uses bottom tabs
- Remove the mobile backdrop overlay (lines 100-106)
- Remove the mobile `translate-x` animation logic
- Keep the `aside` as desktop-only by ensuring `lg:translate-x-0 -translate-x-full` (hidden on mobile, no toggle)
- This simplifies the sidebar to be purely a desktop component

---

### Component: SettingsModal [MINOR MODIFY]

#### [MODIFY] `SettingsModal.tsx` — `frontend/src/components/SettingsModal.tsx`

- **[AMENDMENT #1]** Remove the `if (!isOpen || !user) return null` guard on line 169. Instead, conditionally render auth-only content (Sign In / Guest buttons) when `!user`, and full settings when `user` is present.
- Add a new "Account" tab (or merge into "Profile" tab) containing:
  - Google Sign In / Sign Out button (move auth logic from `Sidebar.tsx` lines 357-436)
  - Guest mode button
  - Sponsor Us links (already has its own tab, keep as-is)
- The modal is already responsive with `flex-col md:flex-row` layout, so mobile compatibility is already handled.

---

### Component: Layout [MINOR MODIFY]

#### [MODIFY] `layout.tsx` — `frontend/src/app/layout.tsx`

- Add `<MobileTopBar />` import and render it above `<main>` (only on mobile via `lg:hidden` inside the component)
- Adjust main padding-top on mobile to account for MobileTopBar: `pt-14 lg:pt-0`
- Keep existing `pb-24 lg:pb-8` for bottom tab clearance

---

## Task Breakdown

### Task 1: Create MobileTopBar Component
**Files:**
- Create: `frontend/src/components/MobileTopBar.tsx`
- Modify: `frontend/src/app/layout.tsx` (import + render)

**Steps:**
1. Create `MobileTopBar.tsx` with notification bell (left) and tier badge (right)
2. Import `useUser()` for user data and notification state
3. Implement tier badge with color variants and tap-to-show privileges popover
4. Implement notification dropdown (reuse Sidebar notification logic)
5. Add to `layout.tsx` above `<main>`
6. Add `pt-14 lg:pt-0` to main element

### Task 2: Rewrite BottomTabBar with Sliding Tabs
**Files:**
- Modify: `frontend/src/components/BottomTabBar.tsx` (complete rewrite)

**Steps:**
1. Replace the current 5-tab + More popup with a two-zone layout
2. Implement Zone 3: scrollable tab strip with all 8-9 nav items
3. Implement Zone 4: fixed ⚙️ settings button
4. Add auto-scroll-to-active-tab behavior
5. Add hidden scrollbar CSS
6. Wire up Settings button to open `SettingsModal`
7. Handle GM-conditional Admin tab visibility via `useUser()`

### Task 3: Add Auth Controls to SettingsModal
**Files:**
- Modify: `frontend/src/components/SettingsModal.tsx`

**Steps:**
1. Add "Account" section to the Profile tab containing:
   - Google Sign In button
   - Google Sign Out button
   - Guest mode button
2. Move auth logic from `Sidebar.tsx` into reusable actions
3. Ensure `SettingsModal` can work without `user` prop (for logged-out state, allowing login from settings)

### Task 4: Clean Up Sidebar for Desktop-Only
**Files:**
- Modify: `frontend/src/components/Sidebar.tsx`

**Steps:**
1. Remove mobile hamburger toggle button
2. Remove mobile backdrop overlay
3. Remove `translate-x` animation toggle state
4. Ensure the sidebar is purely `lg:block hidden` — never shown on mobile
5. Verify desktop sidebar still works identically

### Task 5: Verify 1:1 Feature Parity
**Files:**
- None (verification only)

**Steps:**
1. Desktop sidebar feature list vs. mobile bottom tab feature list — all 9 items match
2. Notification bell: desktop sidebar vs. mobile top bar
3. Tier indicator: mobile top bar (desktop has it in SettingsModal Profile tab)
4. Settings + Auth: desktop sidebar vs. mobile bottom tab ⚙️
5. AI Copilot FAB: already present on both
6. Sponsor: accessible from Settings tab on both

### Task 6: Visual Polish & Edge Cases
**Files:**
- Various CSS tweaks

**Steps:**
1. Ensure sliding tabs have smooth momentum scrolling on iOS/Android
2. Test safe area insets (top + bottom) for notch devices
3. Verify AI Copilot FAB doesn't overlap with the new top bar
4. Test landscape orientation
5. Verify no horizontal overflow issues on any page

---

## Verification Plan

### Automated Browser Tests (Playwright)
- Existing test: `tests/e2e/mobile_portfolio.spec.ts` — run to verify nothing is broken
- Command: `cd frontend && bunx playwright test tests/e2e/mobile_portfolio.spec.ts`

### Visual Verification (Browser Subagent)
1. **Mobile viewport (390×844):**
   - Top bar shows notification bell + tier badge
   - Bottom bar shows scrollable tabs with all nav items visible via swipe
   - Fixed ⚙️ Settings button on far right of bottom bar
   - Tapping ⚙️ opens SettingsModal
   - All 9 nav tabs navigate to correct pages
   - AI Copilot FAB is visible and not overlapping

2. **Desktop viewport (1440×900):**
   - Desktop sidebar is unchanged (no visual regression)
   - No mobile top bar visible
   - No bottom tab bar visible
   - Settings gear in sidebar user card still works

3. **Tablet viewport (768×1024):**
   - Bottom tab bar visible (below lg breakpoint)
   - Sidebar hidden
   - Content still readable with proper padding

### Manual Verification (User)
1. Open the deployed Zeabur app on a real mobile phone
2. Confirm swipe-to-scroll works natively on the bottom tabs
3. Confirm notification bell shows notifications when tapped
4. Confirm tier badge shows correct tier and privileges popup
5. Confirm Settings → Account shows login/logout options

---

## Decision Log

| # | Decision | Alternatives Considered | Rationale |
|---|----------|------------------------|-----------|
| 1 | Horizontal scroll tabs (not pagination/grid) | Grid popup, pagination dots | Reference app uses horizontal scroll; most native-feeling UX |
| 2 | Fixed Settings button separated from scroll zone | Settings as last tab in scroll | User directive: Settings is fixed, NOT in sliding tabs |
| 3 | MobileTopBar as new component (not modifying Sidebar) | Reuse Sidebar header on mobile | Clean separation; Sidebar stays desktop-only |
| 4 | Move auth into SettingsModal (not a separate screen) | Dedicated auth page | User directive: Account Auth inside Settings modal |
| 5 | Keep using existing `SettingsModal` (not creating new modal) | New mobile-specific settings sheet | Reuse existing code; already responsive |
| 6 | Emoji icons for tabs (not SVG) | SVG icons from Sidebar | Simpler, more compact for small tab labels, matches reference app feel |
