# BUG-011-CV: Portfolio Transaction Edit Button Failure

## Description
When clicking the "Edit" (✏️) button on a transaction within the `TransactionHistoryModal`, the edit form (`TransactionFormModal`) fails to open.

## Root Cause
The `onEdit(tx)` callback in `page.tsx` relies on `tx.target_id` to determine which target the transaction belongs to in order to open the form modal (`setShowTxForm(tx.target_id)`). However, the backend `list_transactions` query in `app/repositories/transaction_repo.py` selected only `id, type, shares, price, date` and omitted `target_id`. As a result, `tx.target_id` was undefined in the frontend, preventing the form state from toggling.

## Impact
Users cannot edit their historical transactions and are forced to delete and recreate them. This issue only affected logged-in users; Guest Mode calculates transactions differently and always preserved `target_id`.

## Resolution
1. Added `target_id` to the `SELECT` statement in `transaction_repo.py`.
2. Verified that `useTransactions.ts` successfully issues a `PUT` request with `id` preserving the updated values.

**Status**: Fixed in master.
**Agent**: [CV]
