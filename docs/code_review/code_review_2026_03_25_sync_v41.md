# Code Review Note — 2026-03-25 v41

**Date**: 2026-03-25
**Reviewer**: `[CV]`
**Reviewees**: `[CODE]` (backend), `[UI]` (frontend)
**Commits reviewed**: `fd21ef6`, `7c37796` (HEAD~2..HEAD)

---

## Code Review Summary

**Files reviewed**: 4 core source files, ~40 lines changed
**Overall assessment**: **APPROVE** (with noted P2/P3 suggestions for follow-up)

---

## Findings

### P0 — Critical

*None.*

### P1 — High

*None.*

### P2 — Medium

#### 1. `usePortfolioData.ts:102` — `loading` hides group-switching skeleton

```diff
-const loading = (!service && !isGuest) || (!targets && targetsLoading);
+const loading = (!service && !isGuest) || targetsIsLoading;
```

`targetsIsLoading` is a SWR flag that is only `true` on the **first mount** (when there is no cached data). On the second group switch it is always `false`, so the loading skeleton never appears and the table shows stale empty data for 1–2 seconds while the new fetch completes.

**Suggested fix**: Also show a loading indicator when `targetsLoading` (= `isValidating`) is true after a group switch:

```ts
const loading = (!service && !isGuest) || targetsIsLoading;
const groupSwitchLoading = targetsLoading && !targetsIsLoading; // revalidating, not first load
```

Pass `groupSwitchLoading` to `TargetList` so it can show a subtle opacity/spinner instead of the full skeleton.

#### 2. `portfolioService.ts:163` — `AbortSignal.timeout` fallback always evaluates to `undefined`

```ts
signal: typeof AbortSignal !== 'undefined' && AbortSignal.timeout ? AbortSignal.timeout(5000) : undefined
```

In Next.js SSR and modern browsers, `AbortSignal.timeout` is always available. More importantly, on environments where it is missing the `signal: undefined` branch means the fetch has **no timeout at all** — the very scenario you're trying to prevent. 

**Better approach**: Use a `Promise.race` pattern or a custom `AbortController` timeout for guaranteed fallback:

```ts
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), 5000);
try {
  const pRes = await fetch(url, { credentials, signal: controller.signal });
  ...
} finally {
  clearTimeout(timer);
}
```

### P3 — Low

#### 3. `Sidebar.tsx:39` — Defensive optional chaining on `pathname` is unnecessary

```diff
-const active = pathname === href || (pathname?.startsWith(href + "/") ?? false);
+const active = pathname === href || pathname.startsWith(href + "/");
```

`usePathname()` from Next.js is typed as `string` (non-nullable). The optional chain creates confusion and suggests `null` is possible. It is safe to drop `?.` and `?? false` — the Hydration fix itself is correct and valuable, the optional chain is just cosmetic.

#### 4. `strategy_service.py` — `asyncio.sleep(0)` has no comment explaining *why*

The injected `await asyncio.sleep(0)` is correct but completely invisible as to why it exists. If a future developer sees a bare `sleep(0)` they may remove it thinking it's dead code.

**Suggested**: Add an inline comment:
```python
await asyncio.sleep(0)  # yield event loop to avoid blocking auth/other requests during heavy chunk processing
```

---

## Removal / Iteration Plan

| Item | Action | Priority |
|------|--------|----------|
| `(!targets && targetsLoading)` legacy condition | Already removed ✅ | — |
| `AbortSignal.timeout` pattern in `portfolioService.ts` | Replace with `AbortController` + `setTimeout` | P2 follow-up |
| `pathname?.startsWith(...)` | Simplify to `pathname.startsWith(...)` | P3 housekeeping |

---

## Additional Suggestions

- Consider adding a `data-testid="targets-loading"` on the group-switch skeleton/spinner so future Playwright tests can assert on loading transitions.
- The `priceCache` module-level variable in `portfolioService.ts` is a potential memory leak in a long-lived SPA session — worth adding a TTL eviction for the cache entries (currently entries accumulate indefinitely until it exceeds 1 entry per unique stock seen).

---

## Conclusion

The three bug-fixes reviewed are **correct, targeted, and production-safe**:
- Event-loop yielding in `strategy_service.py` is the minimal non-disruptive fix.
- Sidebar active-state fix eliminates the React Hydration warning properly.
- SWR key-based fetcher pattern is the idiomatic solution for this race condition.

No P0/P1 blockers found. The P2 items are improvement opportunities for the next sprint.

**Status: APPROVED** ✅
