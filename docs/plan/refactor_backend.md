
# [Refactor] Backend Monolith Split (COMPLETED)

**Goal:** Decompose `app/portfolio_db.py` (2.6k lines) into a modular, cleaner architecture without changing business logic.

## User Review Required
> [!NOTE]
> This is a pure refactor. No new features.
> **Safety Net:** `tests/unit/safety_net_portfolio.py` MUST pass before and after every major step.

## Proposed Changes

### 1. Foundation
#### [NEW] `app/database.py`
- Move `get_db`, `init_db`, `PERSISTENT_DIR`, `REPO_DB_PATH`.
- Ensure `init_db` initializes the schema exactly as before.

#### [NEW] `app/config.py` (or `app/constants.py`)
- Move constants: `FREE_MAX_GROUPS`, `STOCK_NAME_CACHE`, `SUPPLEMENTARY_NAME_CACHE`.

### 2. Repositories (Data Access Layer)
Pure SQL execution. No business logic (tiers/limits).
#### [NEW] `app/repositories/user_repo.py`
- `update_user_login`
- `update_user_nickname`, `update_user_stats`, `get_leaderboard`

#### [NEW] `app/repositories/group_repo.py`
- `create_group` (SQL only), `list_groups`, `delete_group`

#### [NEW] `app/repositories/target_repo.py`
- `add_target` (SQL only), `list_targets`, `delete_target`

#### [NEW] `app/repositories/transaction_repo.py`
- `add_transaction` (SQL only), `list_transactions`, `update_transaction`, `delete_transaction`

### 3. Services (Business Logic Layer)
Contains tier checks, name fetching, calculations.
#### [NEW] `app/services/portfolio_service.py`
- `create_group` (Checks tier -> Calls Repo)
- `add_target` (Checks tier -> Fetches Name -> Calls Repo)
- `add_transaction` (Checks tier -> Calls Repo)
- `list_groups` (Handles default initialization logic)

#### [NEW] `app/services/calculation_service.py`
- `get_target_summary` (The complex P&L logic)
- `get_public_portfolio`

#### [NEW] `app/services/market_data_service.py`
- `fetch_stock_name`, `fetch_live_prices`, `load_stock_name_cache`

### 4. Integration & Consumer Updates
Update strict imports in:
- `app/main.py`
- `app/routers/portfolio.py`
- `app/routers/sync.py`
- `app/services/backup.py`
- `app/dividend_cache.py`

#### [DELETE] `app/portfolio_db.py`
Once all consumers are updated.

## Verification Plan

### Automated Tests
1. **Safety Net Regression:**
   ```bash
   PYTHONPATH=. python3 tests/unit/safety_net_portfolio.py
   ```
2. **Existing Unit Tests:**
   ```bash
   python3 -m unittest tests/unit/test_notifications.py
   ```

### Manual Verification
1. Start App: `./start_app.sh`
2. Login and verify Portfolio loads.
3. Check "Mars Strategy" page (uses market data).
