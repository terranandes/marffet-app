# Phase 37 Remaining TODOs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Resolve the 5 remaining development items in Phase 37 to formally close the Verification Campaign.
**Architecture:** 
1. Fix test flakiness in mobile E2E tests by forcing clicks and using more specific locators.
2. Introduce a global `SyncIndicator` for SWR `isValidating` states to improve UX during background fetches.
3. Update documentation and perform final remote verification.

**Tech Stack:** Playwright (Python), React (Next.js), SWR, Tailwind.

---

### Task 1: Fix BUG-020 mobile E2E locator (`test_mobile_portfolio.py`)

**Files:**
- Modify: `/home/terwu01/github/marffet/tests/unit/test_mobile_portfolio.py`

**Step 1: Update locators to handle mobile overlaps and duplicates**

Modify `test_mobile_portfolio.py`:
1. Line 84: Change `new_group_btn.click()` to `new_group_btn.click(force=True)` to handle possible mobile overlay blocking.
2. Line 126-127: Remove the duplicate `stock_input.fill("2330")`.
3. Line 130: Change `page.locator("button", has_text=re.compile(r"\+ (Add Asset|新增資產)")).click()` to `.first.click(force=True)`.
4. Line 178: Change `page.get_by_text("TSMC", exact=True).click()` to `page.locator(".cursor-pointer").filter(has_text="TSMC").first.click(force=True)` to avoid strictness violations and click interception.

**Step 2: Run test to verify it passes**

Run: `pytest tests/unit/test_mobile_portfolio.py -v`
Expected: PASS 

**Step 3: Commit**

```bash
git add tests/unit/test_mobile_portfolio.py
git commit -m "test: fix BUG-020 mobile portfolio e2e locators"
```

---

### Task 2: Add `isValidating` background-fetch spinner per tab

**Context:** We want users to know when SWR is checking for updates in the background.

**Files:**
- Create: `/home/terwu01/github/marffet/frontend/src/app/components/SyncIndicator.tsx`
- Modify: `/home/terwu01/github/marffet/frontend/src/app/mars/page.tsx`
- Modify: `/home/terwu01/github/marffet/frontend/src/app/race/page.tsx`
- Modify: `/home/terwu01/github/marffet/frontend/src/app/cb/page.tsx`
- Modify: `/home/terwu01/github/marffet/frontend/src/app/ladder/page.tsx`

**Step 1: Create `SyncIndicator`**

Create a small, absolute-positioned ping or spinner that only shows when `isValidating` is true.

```tsx
// frontend/src/app/components/SyncIndicator.tsx
import { RefreshCw } from "lucide-react";

export function SyncIndicator({ isSyncing }: { isSyncing: boolean }) {
  if (!isSyncing) return null;
  return (
    <div className="fixed bottom-4 right-4 bg-terran-blue/20 backdrop-blur-md border border-terran-blue/30 text-terran-blue px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 z-50 animate-in fade-in slide-in-from-bottom-4 shadow-[0_0_15px_rgba(0,195,255,0.2)]">
      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
      <span>Syncing...</span>
    </div>
  );
}
```

**Step 2: Inject into main pages**

For each of the 4 pages (mars, race, cb, ladder), import the component and add it to the bottom of the main `<main>` or `<div>` return block, passing the SWR `isValidating` variable from the main hook structure.

*(Note: Portfolio already has its own syncing indicator in PortfolioHeader. We only need it for the other 4).*

**Step 3: Verify visually**

Run the local dev server and trigger a window focus or manual revalidation to see the `Syncing...` toast appear at the bottom right.

**Step 4: Commit**

```bash
git add frontend/src/app/components/SyncIndicator.tsx frontend/src/app/*/page.tsx
git commit -m "feat: add global background sync indicator for SWR revalidation"
```

---

### Task 3: Update `docs/product/feature_portfolio.md`

**Files:**
- Modify: `/home/terwu01/github/marffet/docs/product/feature_portfolio.md`

**Step 1: Add skeleton Note**

Add a note explaining the skeleton loader strategy implemented in Phase 35 (Round 5-7). Specifically mention:
- First paint uses standard Next.js loading skeletons for instant perceived performance.
- SWR revalidations use background `isValidating` state without replacing the UI with skeletons (no layout shift).

**Step 2: Commit**

```bash
git add docs/product/feature_portfolio.md
git commit -m "docs: add skeleton loader strategy to portfolio specs"
```

---

### Task 4: Full remote Playwright E2E sweep on Zeabur

**Step 1: Run the suite**

Run: `python ./tests/integration/round7_full_suite.py --url https://marffet-app.zeabur.app`
Expected: 100% Pass.

*(Note: PWA verification and Public GitHub Sync are manual Boss-led tasks and will be marked as such in the PR).*
