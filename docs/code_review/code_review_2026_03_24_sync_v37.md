# 🔍 Code Review Note — v37

**Date:** 2026-03-24
**Version:** v37
**Author:** [CV] Code Verification Manager
**Scope:** Since v36 — Sentry SDK Zeabur Build Hotfix
**Baseline Commit:** `ace008c` (HEAD)
**Previous Review Baseline:** `2f3557e` (v36)

---

## Files in Scope

| File | Change |
| --- | --- |
| `frontend/next.config.ts` | 1 file changed, 10 insertions(+), 14 deletions(-) |

**Total: 1 file changed**

---

## 1. Frontend — `next.config.ts`

**Issue:** The Zeabur Docker build failed during `bun run build` with the error:
`Type error: Expected 0-2 arguments, but got 3.` on the `withSentryConfig` call.

**Root Cause:** The recently added `@sentry/nextjs` SDK was installed at version `^10.45.0` (Sentry v10). The API for `withSentryConfig` in v10 changed significantly from v8/v9:
- It now only accepts up to 2 arguments: `(config, options)`. The older 3-argument form `(config, cliOptions, runtimeOptions)` was deprecated.
- Several properties were renamed or removed, specifically `hideSourceMaps` was removed in favor of `sourcemaps: { deleteSourcemapsAfterUpload: true }`.
- `transpileClientSDK` was removed completely as v10 handles this natively.

**Fix Applied (Commit `ace008c`):**
```typescript
export default withSentryConfig(nextConfig, {
  silent: true,
  org: "marffet",
  project: "frontend",
  widenClientFileUpload: true,
  tunnelRoute: "/monitoring",
  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },
  disableLogger: true,
});
```

- ✅ Merged into 2-argument API correctly.
- ✅ Replaced `hideSourceMaps` with valid v10 `sourcemaps` object.
- ✅ Removed `transpileClientSDK`.
- ✅ V10 TypeScript compiler (`tsc --noEmit`) passes cleanly with no errors.

**Risk:** None. This simply aligns the Next.js build config with the installed Sentry v10 typings, unblocking the production Zeabur build.

---

## 2. Overall Status: ✅ APPROVED

**Summary:**
- Sentry SDK Next.js configuration hotfix applied correctly.
- Code matches Sentry v10 typing requirements.
- Fix was rebased cleanly over the `portfolio.db` nightly backups on the remote and pushed as `ace008c`.

---

**Reviewer:** [CV]
**Date:** 2026-03-24 22:15 HKT
