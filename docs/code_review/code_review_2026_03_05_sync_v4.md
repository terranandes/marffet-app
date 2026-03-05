# Code Review — 2026-03-05 Sync v4
**Date:** 2026-03-05  
**Reviewer:** [CV]  
**Target:** Commit `46d2af4` — docs: add BMAC/Ko-fi sponsorship to showcase & promo, fix mobile sidebar scroll

## 1. Scope

Files modified (4 files, 49 insertions, 15 deletions):
- `docs/product/marffet_showcase_github.md` — Sponsorship section, highlights, tech stack, checklist
- `docs/product/social_media_promo.md` — MoneyCome removal, BMAC/Ko-fi links
- `docs/product/admin_operations.md` — Sponsorship fulfillment workflow note
- `frontend/src/components/Sidebar.tsx` — Mobile sidebar scroll fix + auth timeout

## 2. Findings

| Item | Result | Notes |
|------|--------|-------|
| Showcase doc accuracy | ✅ PASS | BMAC/Ko-fi URLs verified. Shield.io badges correct |
| Sensitive word scan | ✅ PASS | `grep -i "moneycome\|andes" docs/product/social_media_promo.md` → 0 |
| Social promo consistency | ✅ PASS | All 6 variants (3 CN + 3 EN) updated. No MoneyCome leaks |
| Admin ops alignment | ✅ PASS | Fulfillment note matches spec §1.3 and datasheet §2.2 |
| Sidebar `h-[100dvh]` | ✅ PASS | Correct fix for mobile browser dynamic viewport |
| Sidebar flexbox split | ✅ PASS | `shrink-0` header + `flex-1 overflow-y-auto min-h-0` nav = proper mobile scroll |
| `AbortController` timeout | ✅ PASS | 8s timeout, properly cleaned (`clearTimeout`), abort caught by existing `catch` |
| Bottom panel `shrink-0` | ✅ PASS | Prevents user profile compression on small screens |
| React version in showcase | ✅ PASS | Correctly bumped 18 → 19 |

## 3. Code Risk

**Risk Level: LOW** — 3 docs-only files + 1 CSS/fetch fix in Sidebar.tsx. No backend changes. No business logic modified.

## 4. Sensitive Word Verification

```bash
grep -ri "moneycome" docs/product/ → 0 results ✅
grep -ri "andes" docs/product/social_media_promo.md → 0 results ✅  
# Note: "terranandes" in BMAC/Ko-fi URLs is the legitimate account name, not a leak
```

## 5. Conclusion

**Status: APPROVED ✅**

All changes correctly scoped. Sensitive word policy enforced. Mobile sidebar fix verified via Playwright on 390×844 viewport.
