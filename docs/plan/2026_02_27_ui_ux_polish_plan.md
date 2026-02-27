# UI/UX Polish Plan — Phase 23
**Date:** 2026-02-27
**Author:** [PL] + [UI] + [PM]
**Status:** DRAFT — Awaiting Boss Review

---

## 0. Scope & Priority

Boss confirmed **no urgent bugs**. This plan focuses on polishing four specific areas he flagged, plus general cross-tab improvements.

| Priority | Area | Current State | Goal |
|:---------|:-----|:-------------|:-----|
| **P0** | GM Dashboard (`/admin`) | Functional but flat | Premium command center |
| **P0** | Settings Modal | 36KB monolith, functional | Refined UX with transitions |
| **P1** | AI Bot (Copilot) | Basic floating chat | Polished chat with markdown |
| **P1** | Notification Trigger | Polling works, backend wired | Actionable real-time alerts |
| **P2** | Cross-Tab Polish | Consistent but basic | Micro-animations & skeletons |

---

## Phase A: GM Dashboard Overhaul (`/admin`)

> **File:** `frontend/src/app/admin/page.tsx` (795 lines)

### Current Issues
- Flat button layout — no visual priority hierarchy
- No section collapsibility — overwhelming for daily use
- Crawler progress is simulated, not real-time
- Feedback triage cards lack quick-action UX
- No mobile responsiveness

### Proposed Changes

#### A1. Collapsible Section Cards
- Wrap each section (Metrics, Pipeline, Crawler, DB, Feedback) in a `<details>`-style collapsible glass-card
- Remember open/closed state in `localStorage`
- Default: Metrics + Feedback open, others collapsed

#### A2. Pipeline Button States
- Add loading spinners + disabled states during async ops
- Add success/error toast notifications after operations complete
- Color-code buttons: 🟢 Safe (Initialize), 🟡 Moderate (Refresh), 🔴 Destructive (Cold Crawl)

#### A3. Real-Time Crawler Progress
- Replace simulated progress bar with actual `/api/admin/crawl/status` polling
- Show elapsed time, progress %, and live status messages
- Auto-refresh metrics after crawl completes

#### A4. Feedback Triage UX
- Add inline status dropdown (instead of separate update call)
- Add expandable agent_notes textarea per feedback item
- Add "Copy to JIRA" button formatting feedback as markdown
- Status color badges: 🔵 new, 🟡 reviewing, 🟢 fixed, ⚫ wontfix

#### A5. Mobile Responsive
- Stack button grids vertically on `< md` breakpoints
- Collapsible sidebar auto-closes on admin page

---

## Phase B: Settings Modal Refinement

> **File:** `frontend/src/components/SettingsModal.tsx` (36KB, ~584 lines)

### Current Issues
- Monolithic component (could split into tab sub-components)
- Tab switching is instant (no transition animations)
- Save confirmations are basic `alert()` calls
- Feedback form categories missing Cash Ladder & Compound Interest

### Proposed Changes

#### B1. Tab Transition Animations
- Add Framer Motion `AnimatePresence` for tab content transitions
- Subtle slide + fade between tabs

#### B2. Save Confirmation Toasts
- Replace `alert()` with inline toast notifications (green success bar)
- Auto-dismiss after 2 seconds

#### B3. Missing Feedback Categories
- Add `cash_ladder` and `compound_interest` to `FEATURE_CATEGORIES` in `feedback_db.py`
- Frontend will auto-populate from `/api/feedback/categories`

#### B4. Profile Tab Enhancement
- Show user's current leaderboard rank inline
- Add avatar upload placeholder (future)
- Show "Last Synced" timestamp

#### B5. Component Decomposition (Optional, P2)
- Extract each tab into its own component file
- Reduces cognitive load for future maintenance

---

## Phase C: AI Bot (Copilot) Polish

> **File:** `frontend/src/components/AICopilot.tsx` (189 lines)
> **Blocker:** BUG-111-CV (GCP API must be enabled by Boss)

### Current Issues
- Plain text responses (no markdown rendering)
- No typing indicator during AI response
- No conversation persistence (resets on page change)
- Mobile: chat panel overlaps content

### Proposed Changes

#### C1. Markdown Response Rendering
- Parse AI responses with `react-markdown` or lightweight inline parser
- Support bold, lists, code blocks in AI advice

#### C2. Typing Indicator
- Show animated "..." dots while waiting for `/api/chat` response
- Disable send button during loading

#### C3. Conversation Persistence
- Store chat history in `localStorage` (keyed by user ID)
- "Clear Chat" button to reset
- Limit to last 20 messages to avoid bloat

#### C4. Mobile Responsiveness
- Full-screen chat panel on mobile (`< md`)
- Slide-up animation from bottom
- Close button clearly visible

#### C5. Premium Badge Indicator
- Show "Free" or "Premium" tier badge in chat header
- Subtle visual difference in AI response styling per tier

---

## Phase D: Notification Trigger System

> **Files:** `Sidebar.tsx` (notification bell) + Backend engines

### Current Issues
- Polling exists (30s interval) but actual notification generation unclear
- No toast/push notifications — only sidebar bell dropdown
- No notification types differentiation
- No "mark all as read" with visual feedback

### Proposed Changes

#### D1. Notification Engine Triggers (Backend)
- **CB Premium Alert:** Fire when a tracked CB's premium crosses -1% (buy) or +30% (sell)
- **Price Movement Alert:** Fire when a portfolio stock moves ±5% intraday
- **System Alert:** Fire after crawler/backup completion
- **Dividend Alert:** Fire when dividend ex-date approaches for held stocks

#### D2. Toast Notifications (Frontend)
- Add a global toast provider (`react-hot-toast` or custom)
- New notifications pop up as bottom-right toasts
- Click toast to navigate to relevant page

#### D3. Notification Type Badges
- Color-code by type: 🔴 CB Alert, 🟢 Price Up, 🔵 System, 💰 Dividend
- Icon per notification type in dropdown

#### D4. Sound Alert (Optional, P2)
- Subtle notification sound for Premium users
- Configurable in Settings → Preferences

---

## Phase E: Cross-Tab Polish (P2)

### E1. Loading Skeletons
- Replace "Loading..." text with shimmering skeleton cards on Mars, BCR, Portfolio tabs
- Consistent skeleton pattern across all pages

### E2. Error States
- Unified error boundary component
- Friendly "Something went wrong" card with retry button

### E3. Micro-Animations
- Page entrance animations (staggered card reveals)
- Number counters for financial values (count-up effect)
- Smooth chart transitions on data refresh

### E4. Mobile Layout Audit
- Review all tabs on 375px viewport
- Fix overflow issues, touch target sizes
- BUG-114-CV: Resolve mobile portfolio card click timeout

---

## Execution Strategy

| Phase | Estimated Effort | Dependencies |
|:------|:----------------|:-------------|
| A (GM Dashboard) | 3-4 hours | None |
| B (Settings Modal) | 2-3 hours | `feedback_db.py` category fix |
| C (AI Bot) | 2-3 hours | **BUG-111-CV** (GCP API enable) |
| D (Notifications) | 4-5 hours | Backend engine work |
| E (Cross-Tab) | 3-4 hours | None |

### Suggested Execution Order
1. **Phase B** (Quick win — Settings + feedback categories)
2. **Phase A** (GM Dashboard — high Boss visibility)
3. **Phase D** (Notifications — engagement driver)
4. **Phase C** (AI Bot — blocked on GCP)
5. **Phase E** (Cross-tab — ongoing polish)

---

## Review Checklist
- [ ] Boss reviews and approves priority ordering
- [ ] Boss enables GCP Generative Language API (unblocks Phase C)
- [ ] Agents agree on toast notification library choice
- [ ] Mobile breakpoint standards confirmed (375px min)
