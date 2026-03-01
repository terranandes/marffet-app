# BUG-123 — Portfolio TargetList: Missing AnimatePresence Import Causes Full Browser Freeze

**Type:** BUG  
**Serial ID:** 123  
**Reporter:** `[CV]` (Antigravity)  
**Date:** 2026-03-01  
**Status:** ✅ CLOSED  

---

## Discovery

**Discovered by:** `[CV]` during the `/full-test-local` pipeline execution.  
`bun run build` inside the isolated `.worktrees/martian-test-local` worktree emitted the following TypeScript compile error:

```
./src/app/portfolio/components/TargetList.tsx:198:50
Type error: Cannot find name 'AnimatePresence'.
```

The Next.js dev server silently swallowed this error and served an unresponsive overlay, causing the browser tab to completely freeze and blocking all Playwright tests with 60s timeouts.

---

## Root Cause

During the Phase F "Full Webull" Portfolio refactor, `<AnimatePresence>` was added to the dropdown menu inside `TargetList.tsx` (line 198), but the import statement only included `motion`:

```tsx
// BEFORE (broken)
import { motion } from "framer-motion";
```

---

## Fix Applied

```tsx
// AFTER (fixed)
import { motion, AnimatePresence } from "framer-motion";
```

Additionally, `"use client"` was added to the top of `TargetList.tsx`, `StatsSummary.tsx`, and `TargetCardList.tsx` to ensure correct Next.js App Router client component hydration.

**Fixed by:** `[UI]` (Antigravity)  
**Commit:** `e944b2b` — `chore: sync meeting v2 and bug-120-ui hotfix for missing AnimatePresence causing portfolio crash`

---

## Verification

Playwright navigated successfully to `/portfolio` on the clean worktree server (port 3001) after the fix with no hydration errors or error overlays.
