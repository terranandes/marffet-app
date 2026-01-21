from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
from app.auth import get_current_user
from app.portfolio_db import (
    create_group, list_groups, delete_group,
    add_target, list_targets, delete_target,
    add_transaction, list_transactions, delete_transaction,
    sync_all_dividends, get_total_dividends, get_dividend_history,
    get_all_targets_by_type,
    initialize_default_portfolio
)

router = APIRouter()

# --- Pydantic Models ---
class GroupCreate(BaseModel):
    name: str

class TargetCreate(BaseModel):
    group_id: str
    stock_id: str
    stock_name: Optional[str] = None
    asset_type: str = "stock"

class TransactionCreate(BaseModel):
    target_id: str
    type: str # buy/sell
    shares: int
    price: float
    date: str # YYYY-MM-DD

# --- Groups ---
@router.post("/groups")
async def api_create_group(group: GroupCreate, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    # Note: list_groups() handles initialization internally if needed
    return create_group(group.name, user['id'])

@router.get("/groups")
async def api_list_groups(user: dict = Depends(get_current_user)):
    if not user: return []
    # list_groups() handles initialization internally with is_initialized flag
    return list_groups(user['id'])

@router.delete("/groups/{group_id}")
async def api_delete_group(group_id: str, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    # TODO: Verify ownership? (Skipped for MVP)
    return {"success": delete_group(group_id)}

# --- Targets ---
@router.post("/targets")
async def api_add_target(target: TargetCreate, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return add_target(target.group_id, target.stock_id, target.stock_name, target.asset_type)

@router.get("/targets")
async def api_list_targets(group_id: str, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return list_targets(group_id)

@router.delete("/targets/{target_id}")
async def api_delete_target(target_id: str, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return {"success": delete_target(target_id)}

# --- Transactions ---
@router.post("/transactions")
async def api_add_transaction(tx: TransactionCreate, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return add_transaction(tx.target_id, tx.type, tx.shares, tx.price, tx.date)

@router.get("/targets/{target_id}/transactions")
async def api_list_transactions(target_id: str, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return list_transactions(target_id)

class TransactionUpdate(BaseModel):
    type: str
    shares: int
    price: float
    date: str

@router.put("/transactions/{tx_id}")
async def api_update_transaction(tx_id: str, tx: TransactionUpdate, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return {"success": update_transaction(tx_id, tx.type, tx.shares, tx.price, tx.date)}

@router.delete("/transactions/{tx_id}")
async def api_delete_transaction(tx_id: str, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return {"success": delete_transaction(tx_id)}

@router.get("/dividends/total")
async def api_dividends_total(user: dict = Depends(get_current_user)):
    if not user: return {"total_cash": 0, "dividend_count": 0}
    return get_total_dividends(user['id'])

@router.post("/dividends/sync")
async def api_sync_dividends(user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return sync_all_dividends(user['id'])

@router.get("/targets/{target_id}/dividends")
async def api_target_dividends(target_id: str, user: dict = Depends(get_current_user)):
    """Get dividend history for a specific target."""
    if not user: raise HTTPException(status_code=401)
    return get_dividend_history(target_id)
