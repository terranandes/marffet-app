# Meeting Notes: Agents Sync-Up (2026-01-20 v3)

**Date:** 2026-01-20
**Attendees:** [PM], [PL], [SPEC], [UI], [CV], [CODE]
**Topic:** Production Emergency Resolution & Stability Review

## 1. Project Progress & Status
- **Metric:** Crisis Mode (Stabilizing).
- **Summary:** We encountered two critical bugs in the Zeabur Production environment today. Both have been identified and patched. We are currently waiting for the final deployment to verify stability.

## 2. Bug Triage & Resolution

### 🐛 BUG-002: Stock Name 404 (Missing Data Files)
- **Symptoms:** Users adding stocks (e.g., 6533, 2330) saw "Not Found" errors. E2E tests timed out.
- **Root Cause:** Python packaging (`uv`/`hatchling`) logic excluded `.xlsx` reference files from the build artifact by default.
- **Fix:**
  1.  Enhanced `pyproject.toml` with explicit `[tool.hatch.build]` includes.
  2.  Sanitized `requirements.txt` to remove duplicate entries preventing clean installs.
  3.  Relied on `Dockerfile`'s `COPY . .` as the ultimate guarantee (Sanitization ensures it runs smoothly).
- **Status:** **Deployed** (Build `28ddb94`). Verification pending.

### 🐛 BUG-003: Default Portfolio Reappearance (Persistence Zombie)
- **Symptoms:** User deleted "My Portfolio", but it reappeared upon refresh.
- **Root Cause:** **Race Condition / Atomicity Failure**.
    - The `list_groups` function checked for initialization (`SELECT`), found 0, then called a helper `initialize_default_portfolio` which performed `INSERT`s in a *separate* transaction.
    - If the subsequent `UPDATE users SET is_initialized=1` failed or raced, the user remained in an "Uninitialized state" despite having groups.
- **Fix:**
    - Refactored `initialize_default_portfolio` to accept an existing DB connection.
    - Wrapped the entire "Create Groups + Update Flag" logic into a **Single Atomic Transaction**.
    - Added "Self-Healing" logic (deployed earlier) to auto-correct users who fall into this state.
- **Status:** **Deployed** (Build `07fab2b`). Verification pending.

## 3. Discrepancy Analysis (Local vs Cloud)
- **Local Run (`uv run`):** Works perfectly. Reference files are in place. DB is persistent.
- **Cloud Run (Zeabur):** 
    - **Files:** Failed due to packaging rules (Fixed).
    - **DB:** SQLite on Zeabur is persistent volume (`/data` or root). **Note:** If Zeabur redeploys, does it reset DB?
    - **[SPEC] Note:** We check `portfolio_db.py`: `DB_PATH` is `martian.db` (Relative). In Docker `WORKDIR /app`. So `/app/martian.db`.
    - **Risk:** If Zeabur container is stateless and no volume is mounted to `/app`, DB is lost on deploy.
    - **Mitigation:** We previously verified persistence works. But users reporting "Reappearance" suggests DB might be surviving (if it was wiped, they'd be new users anyway).
    - **Action:** Monitor `/app/martian.db` location. (Ideally should be `/data/martian.db` if mapped).

## 4. Next Steps
1.  **[CV]** Monitor Zeabur Deployment `07fab2b`.
2.  **[CV]** Verify 404 is gone (Add Stock 6533).
3.  **[CV]** Verify Persistence (Delete All -> Refresh -> Empty).
4.  **[CODE]** Prepare to switch DB path to `/data` if persistence proves flaky (Long term).

## 5. Deployment Instructions (For Terran)
To run the App locally to verify logic:
```bash
# 1. Install Credentials (if needed for Google GenAI, else skip)
# 2. Run App
uv run uvicorn app.main:app --reload
# 3. Visit http://localhost:8000
```
To Debug Zeabur:
```bash
uv run python tests/debug_zeabur_6533.py
```

## 6. Artifacts Updated
- `task.md`
- `app/portfolio_db.py` (Atomicity Fix)
- `pyproject.toml` (Packaging Fix)
- `requirements.txt` (Sanitization)

**[PL] Sign-off:** We are confident these fixes resolve the reported issues. Pending confirmation from live environment.
