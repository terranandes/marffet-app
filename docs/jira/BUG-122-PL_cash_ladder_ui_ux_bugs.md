# BUG-122-PL: Cash Ladder UI Bugs (Sync Stats, Share Icons, Allocation Modal)
**Reporter:** [PL]
**Component:** Frontend & Backend (Cash Ladder)
**Severity:** Medium
**Status:** CLOSED

## Description
User reported three distinct UI/UX failures on the Cash Ladder (Leaderboard) tab:
1. **Sync My Stats Button Fails:** Clicking it did nothing visibly (failed silently in UI).
2. **Share Rankings Icon Duplicate:** The Share button displayed "📤 📤 Share Rankings" because the icon was hardcoded in both the component and the label prop.
3. **Player Profile Modal Empty:** Clicking a player showed the Allocation bar but an empty list of invested targets below it.

## Root Cause
1. **Sync Stats:** `POST /api/portfolio/sync-stats` crashed with HTTP 500 because `update_user_stats(user['id'])` implicitly returned `None`. The route explicitly checked `if not result: return JSONResponse(status_code=500, content={"error": "Failed to sync stats"})`.
2. **Share Icon:** The `ShareButton` wrapper in `frontend/src/components/ShareButton.tsx` automatically prepends an emoji icon if copied is false. But `frontend/src/app/ladder/page.tsx` was passing `label="📤 Share Rankings"`.
3. **Allocation Modal:** `frontend/src/app/ladder/page.tsx` expected `profileData.holdings` with `stock_id` and `stock_name`. But `app/services/portfolio_service.py` was returning `top_holdings` with `symbol` and `name`.

## Fix Implemented
1. Modified `update_user_stats` to confidently return `{"roi": roi}` on success, restoring the frontend's alert confirmation.
2. Removed `📤` from the label prop passed to `<ShareButton>` inside `ladder/page.tsx`.
3. Remapped Python JSON keys in `get_public_portfolio`: `top_holdings` -> `holdings`, `symbol` -> `stock_id`, and `name` -> `stock_name`. Also remapped `roi_pct` -> `roi` to restore the UI calculation accuracy.
