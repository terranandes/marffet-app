from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.auth import get_current_user
from app.services import portfolio_service

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
    if not user:
        raise HTTPException(status_code=401)
    # Note: list_groups() handles initialization internally if needed
    return portfolio_service.create_group(user['id'], group.name)

@router.get("/groups")
async def api_list_groups(user: dict = Depends(get_current_user)):
    if not user:
        return []
    # list_groups() handles initialization internally with is_initialized flag
    return portfolio_service.list_groups(user['id'])

@router.delete("/groups/{group_id}")
async def api_delete_group(group_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    # TODO: Verify ownership? (Skipped for MVP)
    return {"success": portfolio_service.delete_group(group_id)}

# --- Targets ---
@router.post("/targets")
async def api_add_target(target: TargetCreate, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return portfolio_service.add_target(target.group_id, target.stock_id, target.stock_name, target.asset_type)

@router.get("/targets")
async def api_list_targets(group_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return portfolio_service.list_targets(group_id)

@router.delete("/targets/{target_id}")
async def api_delete_target(target_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return {"success": portfolio_service.delete_target(target_id)}

# --- Transactions ---
@router.post("/transactions")
async def api_add_transaction(tx: TransactionCreate, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return portfolio_service.add_transaction(tx.target_id, tx.type, tx.shares, tx.price, tx.date)

@router.get("/targets/{target_id}/transactions")
async def api_list_transactions(target_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return portfolio_service.list_transactions(target_id)

class TransactionUpdate(BaseModel):
    type: str
    shares: int
    price: float
    date: str

@router.put("/transactions/{tx_id}")
async def api_update_transaction(tx_id: str, tx: TransactionUpdate, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return {"success": portfolio_service.update_transaction(tx_id, tx.type, tx.shares, tx.price, tx.date)}

@router.delete("/transactions/{tx_id}")
async def api_delete_transaction(tx_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return {"success": portfolio_service.delete_transaction(tx_id)}

@router.get("/dividends/total")
async def api_dividends_total(user: dict = Depends(get_current_user)):
    if not user:
        return {"total_cash": 0, "dividend_count": 0}
    return portfolio_service.get_total_dividends(user['id'])

@router.post("/dividends/sync")
async def api_sync_dividends(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return portfolio_service.sync_all_dividends(user['id'])

from fastapi import Response # Added in thought block to inject into the file

@router.get("/targets/{target_id}/dividends")
async def api_target_dividends(target_id: str, response: Response, user: dict = Depends(get_current_user)):
    """Get dividend history for a specific target."""
    if not user:
        raise HTTPException(status_code=401)
    
    response.headers["Cache-Control"] = "no-store, max-age=0"
    raw_divs = portfolio_service.get_dividend_history(target_id)
    
    formatted = []
    for d in raw_divs:
        formatted.append({
            "date": d.get("ex_date"),
            "payment_date": None,
            "cash_dividend": d.get("amount_per_share", 0),
            "stock_dividend": 0,
            "held_shares": d.get("shares_held", 0),
            "amount": d.get("total_cash", 0)
        })
    return formatted



@router.get("/ladder")
async def api_portfolio_ladder(user: dict = Depends(get_current_user)):
    """Get Asset Distribution Ladder (Cash vs Stock vs ETF vs CB)."""
    if not user:
        return {"total_wealth": 0, "ladder": []}
    return portfolio_service.get_portfolio_ladder(user['id'])


@router.get("/race-data")
async def api_portfolio_race_data(user: dict = Depends(get_current_user)):
    """Get Race Bar Chart data for user portfolio."""
    if not user:
        return []
    
    # Run in threadpool
    from fastapi.concurrency import run_in_threadpool
    return await run_in_threadpool(portfolio_service.get_portfolio_race_data, user['id'])


@router.get("/by-type")
async def api_portfolio_by_type(user: dict = Depends(get_current_user)):
    """Get all targets grouped by type (stock, etf, cb)."""
    if not user:
        return {"stock": [], "etf": [], "cb": []}
    return portfolio_service.get_all_targets_by_type(user['id'])
