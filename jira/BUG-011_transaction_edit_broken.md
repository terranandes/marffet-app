# BUG-011: Transaction Edit Not Working
**Reporter:** [CV] Agent
**Date:** 2026-01-28
**Severity:** High
**Environment:** Both Legacy UI and Next.js UI (localhost and Zeabur)

## Description
Transaction history edit functionality was broken:
1. **Next.js UI:** Edit button (✏️) could not be clicked / didn't open the edit form
2. **Legacy UI:** Edit button could be clicked, but changes were not saved

## Root Cause Analysis

### Issue 1: Next.js Edit Button Not Clickable
The edit button onClick handler used `tx.target_id`:
```typescript
onClick={() => {
    setShowTxForm(tx.target_id);  // <- tx.target_id was undefined!
}}
```

But the API endpoint `list_transactions()` in `portfolio_db.py` did NOT include `target_id` in the response:
```python
# BEFORE (missing target_id)
"SELECT id, type, shares, price, date, created_at FROM transactions ..."
```

### Issue 2: Legacy Edit Button Not Saving
The `update_transaction` function signature requires 5 arguments:
```python
update_transaction(tx_id, tx_type, shares, price, tx_date)
```

But `main.py` line 1093 was passing only 4:
```python
# BEFORE (missing tx_type)
success = update_transaction(tx_id, data.shares, data.price, data.date)
```

### Issue 3: Missing Import in Router
`routers/portfolio.py` called `update_transaction()` but never imported it.

## Resolution

### Fix 1: portfolio_db.py (line 610)
```diff
-"SELECT id, type, shares, price, date, created_at FROM transactions ..."
+"SELECT id, target_id, type, shares, price, date, created_at FROM transactions ..."
```

### Fix 2: main.py (line 1093)
```diff
-success = update_transaction(tx_id, data.shares, data.price, data.date)
+success = update_transaction(tx_id, data.type, data.shares, data.price, data.date)
```

### Fix 3: routers/portfolio.py (line 8)
```diff
-add_transaction, list_transactions, delete_transaction,
+add_transaction, list_transactions, delete_transaction, update_transaction,
```

## Commit
`51de4aa` - fix(portfolio): transaction edit functionality
