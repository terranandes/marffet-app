# 🔍 Code Review Note — v27

**Date:** 2026-03-15
**Version:** v27
**Author:** [CV] Code Verification Manager
**Scope:** Mars Landing Protection & Zeabur Cache Warm-up

---

## 1. Review: `frontend/src/app/page.tsx` — Landing Guard

### Change
```diff
+    // Pages that are NEVER allowed as the default landing page.
+    const DISALLOWED_DEFAULT_PAGES = new Set(["/mars", "/race", "/ladder"]);
+
     let defaultPage = localStorage.getItem("marffet_default_page");
-    if (defaultPage === "/mars") {
-      defaultPage = "/portfolio";
-      localStorage.setItem("marffet_default_page", defaultPage);
+
+    if (defaultPage && DISALLOWED_DEFAULT_PAGES.has(defaultPage)) {
+      localStorage.setItem("marffet_default_page", "/");
+      defaultPage = "/";
     }
```

- **Analysis:** Replaces a fragile if-statement with a scalable `Set` lookup.
- **Improvement:** Proactively includes `/race` and `/ladder` (other compute-heavy routes).
- **Correctness:** ✅ Ensures a fast first-paint by forcing use of the dashboard.
- **Finding:** ✅ APPROVED

---

## 2. Review: `app/main.py` — Background Cache Warm-up

### Change
```diff
-        if os.getenv("ZEABUR_ENVIRONMENT_NAME") is None and os.getenv("ENVIRONMENT") != "production":
-            asyncio.create_task(warm_mars_cache())
+        delay_seconds = 60 if os.getenv("ZEABUR_ENVIRONMENT_NAME") else 5
+        # ...
+        asyncio.create_task(warm_mars_cache())
```

- **Analysis:** Removes the environment guard that completely blocked warm-up on Zeabur.
- **Safety:** ✅ Uses a 60-second delay on Zeabur. This is critical because it moves the spike outside the initial OOM-sensitive startup window.
- **Optimization:** ✅ Populates `SIM_CACHE` for the default params (2006, 1M, 60k).
- **Finding:** ✅ APPROVED

---

## 3. Overall Status: ✅ APPROVED

The combination of frontend blocking and backend pre-warming creates a "Double Lock" system:
1. Users aren't sent to Mars by default (Prevention).
2. If they navigate there, the data is likely already ready (Performance).

No regressions to existing Phase 36 UI features.
