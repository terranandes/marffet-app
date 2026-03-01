# UI/UX Polish & Beautification Plan (Brainstorming)
**Date:** 2026-03-01
**Owner:** [UI] & [PM]
**Context:** Reviewing tabs, modals, and notifications for the Martian App to reach a premium "Webull-style" aesthetic.

---

## 1. Modals (e.g. SettingsModal, TransactionForms)
### Current State:
- `SettingsModal` uses a nice dark cyberpunk theme with `framer-motion` transitions, but is slightly cluttered.
- Extensive use of borders (`border-cyan-500/30`, `border-white/10`) which can feel heavy.
- Scrollable areas can sometimes lack clear visual hierarchy.

### Proposed Polish:
- **Unified Glassmorphism**: Standardize the backdrop blur and background opacity across all modals (e.g., `bg-black/40 backdrop-blur-xl border-white/10`).
- **Typography Hierarchy**: Use clear grouping headers with subtle gradient text rather than solid bright colors.
- **Interactive States**: Improve hover states on buttons (e.g., subtle scale `hover:scale-[1.02]` and glow effects).
- **Accessibility/Focus**: Ensure keyboard navigation is clearly visible with focus rings (`focus:ring-cyan-500/50`).

## 2. Notifications (ToasterProvider)
### Current State:
- Using `react-hot-toast` in bottom-right with standard dark styling: `#1a1a2e` background, `#e0e0e0` text.
- Simple border `rgba(255,255,255,0.1)`.

### Proposed Polish:
- **Premium Toast Styling**: Align toasts with the main app's cyberpunk aesthetic.
  - Background: `rgba(14, 17, 23, 0.9)` with `backdrop-filter: blur(8px)`.
  - Borders: Left-accented borders denoting success/error (e.g., a solid cyan or red 4px left border).
  - Shadows: Introduce a subtle glow shadow matching the toast type (e.g., `box-shadow: 0 4px 20px rgba(0, 242, 234, 0.2)` for success).
- **Custom Icons**: Replace default icons with premium SVGs or animated Lottie SVGs for success/error states.

## 3. Tabs & Navigation (Sidebar, Page Headers)
### Current State:
- Sidebar uses standard active/inactive states.
- In-page tabs (like in `SettingsModal`) use a sidebar format or simple button rows.

### Proposed Polish:
- **Framer Motion Shared Layout Magic**: Use `layoutId` for the active tab indicator to create a smooth sliding pill effect when switching tabs.
- **Micro-interactions**: Add subtle click ripples or spring animations to tab changes.
- **Breadcrumbs/Headers**: Unify page headers to include dynamic breadcrumbs or contextual action buttons (e.g., "Export" or "Settings" contextual to the active tab).

## 4. Cards (e.g. TargetCardList, Mobile Views)
### Current State:
- `TargetCardList` uses `framer-motion` stagger effects and a functional expanded view.
- Information density is high but can be overwhelming on small screens.

### Proposed Polish:
- **Sparklines**: Integrate tiny ECharts sparklines directly into the collapsed card view for a quick visual trend indicator.
- **Skeleton Loaders**: Ensure the newly added `Skeleton.tsx` exactly matches the card layout to prevent layout shift.
- **Swipe Actions (Mobile)**: Implement swipe-to-delete or swipe-to-trade on mobile cards instead of only relying on the expanded view buttons.

---

## Next Steps for Execution
1. Implement the Toast styling upgrade in `ToasterProvider.tsx`.
2. Refactor modal base classes into a reusable generic layout component to enforce consistency.
3. Add Framer Motion `layoutId` sliding indicators to primary tab navigations.
4. (Optional/Future) Investigate adding mobile swipe gestures using `framer-motion`.
