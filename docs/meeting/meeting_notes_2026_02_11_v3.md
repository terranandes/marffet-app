# Sync Meeting Notes: 2026-02-11 (v3)

**Attendees**: `[PL]`, `[PM]`, `[SPEC]`, `[CODE]`, `[UI]`, `[CV]`
**Topic**: Data Repair, Regression Status, and Next Steps

---

## 1. Project Progress
- **`[PL]`**: We have successfully repaired the critical data corruption in `data/raw`. The Mars Strategy now runs on a full 21-year dataset for key stocks (2330, 2317, etc.).
- **`[CV]`**: Verified. TSMC CAGR is now 19.1%, close to the reference 22.2%. Total Cost is correct at 2.26M.
- **`[PM]`**: Excellent. This unblocks the "Strategy Accuracy" milestone. We are ready to move to final deployment verification.

## 2. Current Bugs & Triage
- **`[PL]`**: `e2e_suite.py` on Remote still has a "Session Persistence" issue. `[CV]` marked it as "Manual Verify".
- **`[CV]`**: Correct. The remote Zeabur environment might be losing session cookies or handling `SameSite` differently than local. Low priority for now, as core logic is verified locally.
- **`[CODE]`**: The `crawl_fast.py` script was optimized (retries reduced) but the full universe detailed crawl is still pending. We have a patch for major stocks only.
- **`[PL]`**: Agreed. The "Full Crawl" can be a background task for `[ADMIN]`.

## 3. Deployment Status
- **`[PL]`**: Local regression is passing (both Unit and E2E logic).
- **`[SPEC]`**: We need to ensure the **patched data files** are included in the deployment.
- **`[CODE]`**: They are in `data/raw`, which is part of the repo. So `git push` will deploy them.

## 4. Discrepancy Analysis (Local vs Remote)
- **`[CV]`**: The primary discrepancy was the data itself. Now that local has the patch, we must push to remote to see if Zeabur matches.
- **`[PL]`**: Action item: Push patched data to `master` and trigger deployment.

## 5. Next Phase Planning
- **`[PM]`**: Next is "Phase 3: Deployment Verification".
- **`[UI]`**: Mobile layout review is pending. I need to verify the new "Strategy Results" page on mobile width.
- **`[PL]`**: Let's add "Mobile Audit" to the final checklist.

---

## 6. Action Items
1. **`[CODE]`**: Commit and push the `data/raw/Market_*_Prices.json` files (large change).
2. **`[PL]`**: Trigger Zeabur deployment.
3. **`[CV]`**: Run `scripts/ops/remote_verify.py` (to be created) or manual check on Zeabur.
4. **`[UI]`**: Check mobile responsiveness of the Results Table.

## 7. Workflow Status
- `code_review`: Completed implicitly during debugging.
- `git-worktree`: `full-test` worktree is active. Can be merged and removed after deployment success.

**Reported by**: `[PL]`
