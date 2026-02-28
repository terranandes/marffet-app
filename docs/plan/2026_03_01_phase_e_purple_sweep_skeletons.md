# Phase E: Cross-Tab Purple Sweep + Loading Skeletons — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eliminate all purple/violet CSS remnants across the frontend and replace plain-text "Loading..." states with animated skeleton placeholders.

**Architecture:** Two workstreams: (1) Purple-to-warm color migration across 10 files, (2) Shared Skeleton component creation and integration across 8 pages.

**Tech Stack:** Tailwind CSS v4, React 19, framer-motion (already installed)

---

## Brainstorming Summary

### Purple Inventory (21 occurrences, 10 files)

| File | Count | Purple Usage |
|:---|:---|:---|
| `compound/page.tsx` | 5 | Buttons, focus borders, text accents |
| `race/page.tsx` | 4 | Bar gradient colors |
| `RaceChart.tsx` | 3 | Hex `#bc13fe`, gradient text, toggle button |
| `trend/page.tsx` | 3 | Dividend button/checkbox/text |
| `mars/page.tsx` | 1 | Page title gradient |
| `ladder/page.tsx` | 1 | Rank gradient (top 10) |
| `myrace/page.tsx` | 1 | Bar gradient |
| `viz/page.tsx` | 1 | Page heading gradient |
| `doc/page.tsx` | 1 | Section heading |
| `TargetList.tsx` | 1 | Dividend tag |

### Replacement Color Palette (Purple Ban Compliance)

| Current Purple Context | Replacement | Rationale |
|:---|:---|:---|
| **Interactive buttons/toggles** | `amber-500` / `amber-400` | Warm CTA, high contrast on dark bg |
| **Gradient text decorative** | `cyan-400` → `teal-500` | Cool tech aesthetic, avoids purple entirely |
| **Data viz bar gradients** | `cyan-500`, `teal-500`, `amber-500`, `rose-500` | Diverse, distinguishable, non-purple |
| **Focus borders** | `cyan-500` | System CTA color consistency |
| **Accent text** | `amber-400` or `emerald-400` | Warm/natural, premium feel |
| **Hex `#bc13fe`** | `#06b6d4` (cyan-500) | Direct hex replacement |

### Loading State Analysis

| Page | Current Loading UX | Skeleton Needed |
|:---|:---|:---|
| `mars/page.tsx` | Plain text "Loading..." | ✅ Table skeleton |
| `race/page.tsx` | Plain text "Loading..." | ✅ Chart skeleton |
| `trend/page.tsx` | Plain text "Loading..." | ✅ Chart skeleton |
| `ladder/page.tsx` | Plain text "Loading..." | ✅ Leaderboard skeleton |
| `myrace/page.tsx` | Plain text "Loading..." | ✅ Chart skeleton |
| `viz/page.tsx` | Plain text "Loading..." | ✅ Card grid skeleton |
| `compound/page.tsx` | ✅ Has skeletons already | ❌ No work needed |
| `admin/page.tsx` | ✅ Has `<Spinner />` | ❌ No work needed |

---

## Task 1: Create Shared Skeleton Component

**Files:**
- Create: `frontend/src/components/Skeleton.tsx`

**Step 1: Create the Skeleton component**

```tsx
// frontend/src/components/Skeleton.tsx
"use client";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circle" | "rect" | "chart" | "table-row";
  count?: number;
}

export function Skeleton({ className = "", variant = "rect", count = 1 }: SkeletonProps) {
  const baseClass = "animate-pulse bg-zinc-800/60 rounded";

  const variantClass = {
    text: "h-4 w-3/4 rounded",
    circle: "h-10 w-10 rounded-full",
    rect: "h-20 w-full rounded-lg",
    chart: "h-64 w-full rounded-lg",
    "table-row": "h-10 w-full rounded",
  }[variant];

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`${baseClass} ${variantClass} ${className}`} />
      ))}
    </>
  );
}

export function TableSkeleton({ rows = 8, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2 p-4">
      {/* Header */}
      <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="animate-pulse bg-zinc-700/50 h-8 rounded" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="grid gap-3" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="animate-pulse bg-zinc-800/40 h-10 rounded" />
          ))}
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton({ height = "h-64" }: { height?: string }) {
  return (
    <div className={`animate-pulse bg-zinc-800/40 ${height} w-full rounded-lg flex items-end justify-center gap-1 p-6`}>
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="bg-zinc-700/50 rounded-t w-full"
          style={{ height: `${20 + Math.random() * 60}%` }}
        />
      ))}
    </div>
  );
}

export function LeaderboardSkeleton({ rows = 10 }: { rows?: number }) {
  return (
    <div className="space-y-3 p-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 animate-pulse">
          <div className="bg-zinc-700/50 h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="bg-zinc-800/40 h-4 w-1/3 rounded" />
            <div className="bg-zinc-800/40 h-3 w-full rounded" />
          </div>
          <div className="bg-zinc-800/40 h-6 w-16 rounded" />
        </div>
      ))}
    </div>
  );
}

export function CardGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse bg-zinc-800/40 rounded-xl p-6 space-y-3">
          <div className="bg-zinc-700/50 h-6 w-1/2 rounded" />
          <div className="bg-zinc-700/40 h-4 w-3/4 rounded" />
          <div className="bg-zinc-700/30 h-32 w-full rounded-lg" />
        </div>
      ))}
    </div>
  );
}
```

**Step 2: Commit**
```bash
git add frontend/src/components/Skeleton.tsx
git commit -m "feat: add shared Skeleton component library (Phase E)"
```

---

## Task 2: Purple Sweep — compound/page.tsx (5 changes)

**Files:**
- Modify: `frontend/src/app/compound/page.tsx`

**Replacements:**

| Line | From | To |
|:---|:---|:---|
| 220 | `bg-purple-500 text-white` | `bg-amber-500 text-black` |
| 235 | `focus:border-purple-500` | `focus:border-cyan-500` |
| 251 | `bg-purple-500 text-white` | `bg-amber-500 text-black` |
| 265 | `text-purple-400` | `text-amber-400` |
| 366 | `text-purple-400 font-bold` | `text-amber-400 font-bold` |

**Step 1: Apply all 5 replacements**
**Step 2: Commit** `git commit -m "fix: purple sweep — compound/page.tsx (5 occurrences)"`

---

## Task 3: Purple Sweep — RaceChart.tsx (3 changes)

**Files:**
- Modify: `frontend/src/components/RaceChart.tsx`

**Replacements:**

| Line | From | To |
|:---|:---|:---|
| 86 | `'#bc13fe'` | `'#06b6d4'` (cyan-500) |
| 197 | `to-purple-500` | `to-teal-500` |
| 219 | `bg-purple-600 ... shadow-purple-500/30` | `bg-cyan-600 ... shadow-cyan-500/30` |

**Step 1: Apply all 3 replacements**
**Step 2: Commit** `git commit -m "fix: purple sweep — RaceChart.tsx (3 occurrences)"`

---

## Task 4: Purple Sweep — race/page.tsx (4 changes)

**Files:**
- Modify: `frontend/src/app/race/page.tsx`

**Replacements:**

| Line | From | To |
|:---|:---|:---|
| 206 | `from-indigo-500 to-violet-500` | `from-teal-500 to-cyan-500` |
| 207 | `from-violet-500 to-purple-500` | `from-cyan-500 to-teal-500` |
| 208 | `from-purple-500 to-fuchsia-500` | `from-amber-500 to-orange-500` |
| 223 | `from-violet-400 to-purple-400` | `from-teal-400 to-cyan-400` |

**Step 1: Apply all 4 replacements**
**Step 2: Commit** `git commit -m "fix: purple sweep — race/page.tsx (4 occurrences)"`

---

## Task 5: Purple Sweep — trend/page.tsx (3 changes)

**Files:**
- Modify: `frontend/src/app/trend/page.tsx`

**Replacements:**

| Line | From | To |
|:---|:---|:---|
| 144 | `bg-purple-500/20 border-purple-500 text-purple-400 ... hover:bg-purple-500` | `bg-amber-500/20 border-amber-500 text-amber-400 ... hover:bg-amber-500` |
| 195 | `accent-purple-400` | `accent-amber-400` |
| 196 | `text-purple-400` | `text-amber-400` |

**Step 1: Apply all 3 replacements**
**Step 2: Commit** `git commit -m "fix: purple sweep — trend/page.tsx (3 occurrences)"`

---

## Task 6: Purple Sweep — Remaining Files (6 changes across 6 files)

**Files:**
- Modify: `frontend/src/app/mars/page.tsx` (L303)
- Modify: `frontend/src/app/ladder/page.tsx` (L81)
- Modify: `frontend/src/app/myrace/page.tsx` (L134)
- Modify: `frontend/src/app/viz/page.tsx` (L57)
- Modify: `frontend/src/app/doc/page.tsx` (L53)
- Modify: `frontend/src/app/portfolio/components/TargetList.tsx` (L159)

**Replacements:**

| File | Line | From | To |
|:---|:---|:---|:---|
| mars/page.tsx | 303 | `from-purple-400 to-pink-600` | `from-cyan-400 to-rose-500` |
| ladder/page.tsx | 81 | `from-purple-500 to-violet-700` | `from-amber-500 to-orange-700` |
| myrace/page.tsx | 134 | `from-purple-400 to-violet-500` | `from-teal-400 to-cyan-500` |
| viz/page.tsx | 57 | `via-purple-500` | `via-teal-500` |
| doc/page.tsx | 53 | `text-purple-400` | `text-amber-400` |
| TargetList.tsx | 159 | `bg-purple-500/20 text-purple-400 ... hover:bg-purple-500` | `bg-amber-500/20 text-amber-400 ... hover:bg-amber-500` |

**Step 1: Apply all 6 replacements**
**Step 2: Commit** `git commit -m "fix: purple sweep — 6 remaining files (complete purple ban)"`

---

## Task 6.5: BUG-119-UI — Date Picker Dark Mode Fix

> Per multi-agent review: Skeptic flagged this as missing from Phase E scope.

**Files:**
- Modify: `frontend/src/app/portfolio/components/TransactionFormModal.tsx`
- Possibly modify: `frontend/src/app/globals.css`

**Step 1: Add `color-scheme: dark` to the date input**

In `TransactionFormModal.tsx`, find the `<input type="date">` element and add inline style or Tailwind class:
```tsx
<input type="date" style={{ colorScheme: "dark" }} ... />
```

Alternatively, add a global CSS rule in `globals.css`:
```css
input[type="date"] {
  color-scheme: dark;
}
```

**Step 2: Verify the calendar picker icon is visible on dark background**
**Step 3: Commit** `git commit -m "fix: BUG-119-UI date picker dark mode color-scheme"`

---

## Task 7: Loading Skeletons — mars/page.tsx

**Files:**
- Modify: `frontend/src/app/mars/page.tsx`

**Step 1: Import `TableSkeleton` from Skeleton component**
```tsx
import { TableSkeleton } from "@/components/Skeleton";
```

**Step 2: Replace the loading text block with `<TableSkeleton rows={10} cols={7} />`**

**Step 3: Commit** `git commit -m "feat: skeleton loading — mars/page.tsx"`

---

## Task 8: Loading Skeletons — race, trend, myrace, ladder, viz pages

**Files:**
- Modify: `frontend/src/app/race/page.tsx` — Replace loading with `<ChartSkeleton />`
- Modify: `frontend/src/app/trend/page.tsx` — Replace loading with `<ChartSkeleton />`
- Modify: `frontend/src/app/myrace/page.tsx` — Replace loading with `<ChartSkeleton />`
- Modify: `frontend/src/app/ladder/page.tsx` — Replace loading with `<LeaderboardSkeleton />`
- Modify: `frontend/src/app/viz/page.tsx` — Replace loading with `<CardGridSkeleton />`

**Step 1: Import appropriate skeleton variant in each file**
**Step 2: Replace plain-text loading blocks with skeleton components**
**Step 3: Commit** `git commit -m "feat: skeleton loading — race, trend, myrace, ladder, viz pages"`

---

## Task 9: Final Verification

**Step 1: Run `bun run build` in frontend to verify zero TypeScript errors**
```bash
cd frontend && bun run build
```

**Step 2: Visual verification — navigate all 8 tabs in the browser to confirm:**
- No purple/violet colors visible anywhere
- Loading states show animated skeleton placeholders (pulse animation)
- All interactive elements (buttons, toggles, focus borders) use warm palette

**Step 3: Commit any fixups**
```bash
git commit -m "chore: Phase E complete — purple sweep + loading skeletons"
```

---

## Verification Plan

### Automated Tests
```bash
cd frontend && bun run build  # Zero TypeScript errors
```

### Purple-Free Grep Validation
```bash
grep -rn --include="*.tsx" --include="*.css" -iE "purple|violet|#bc13fe" frontend/src/
# Expected: 0 results
```

### Visual Verification (Playwright MCP)
Navigate each page and take screenshots to confirm:
1. `/mars` — No purple in title or table
2. `/race` — No purple bar gradients
3. `/compound` — No purple buttons or text
4. `/trend` — No purple dividend controls
5. `/ladder` — No purple rank gradients
6. `/myrace` — No purple bar colors
7. `/viz` — No purple in heading
8. `/portfolio` — No purple dividend tags
