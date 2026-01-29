
from fastapi import APIRouter, HTTPException, Depends
import dividend_cache
from app.auth import get_current_user
from app.portfolio_db import get_db

router = APIRouter()

@router.post("/sync/dividends")
async def sync_dividends(stock_ids: str = None):
    """
    Sync dividend cache for specific stocks or all cached if not provided.
    stock_ids: comma-separated list of stock IDs
    """
    ids_list = stock_ids.split(",") if stock_ids else None
    result = dividend_cache.sync_all_caches(ids_list)
    return result

@router.get("/sync/dividends/list")
async def list_cached_dividends():
    """List all cached stocks."""
    return dividend_cache.list_cached_stocks()

@router.post("/sync/my-dividends")
async def sync_my_dividends(user: dict = Depends(get_current_user)):
    """
    Sync dividend cache for current user's holdings only.
    User-facing: syncs only stocks in THEIR portfolio.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user['id']
    
    # Get user's stock holdings
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT gt.stock_id
            FROM group_targets gt
            JOIN user_groups ug ON gt.group_id = ug.id
            WHERE ug.user_id = ?
        """, (user_id,))
        stock_ids = [row['stock_id'] for row in cursor.fetchall()]
    
    if not stock_ids:
        return {"success": True, "message": "No stocks in portfolio", "synced": 0}
    
    # Sync only user's stocks
    result = dividend_cache.sync_all_caches(stock_ids)
    return {
        "success": True,
        "message": f"Synced dividends for {result['success_count']}/{len(stock_ids)} stocks",
        "synced": result['success_count'],
        "total_records": result['total_records']
    }

@router.post("/sync/all-users-dividends")
async def sync_all_users_dividends(user: dict = Depends(get_current_user)):
    """
    Admin endpoint: Sync dividend cache for ALL stocks held by ANY user.
    Comprehensive backup of all dividend data.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if admin (simple check - in production, use proper role system)
    # For now, allow any authenticated user with 'terran' in email
    if 'terran' not in user.get('email', '').lower() and user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get ALL unique stocks from ALL users
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT gt.stock_id
            FROM group_targets gt
        """)
        all_stock_ids = [row['stock_id'] for row in cursor.fetchall()]
    
    if not all_stock_ids:
        return {"success": True, "message": "No stocks in system", "synced": 0}
    
    # Sync all stocks (updates DB + files)
    result = dividend_cache.sync_all_caches(all_stock_ids)
    
    # ADMIN ONLY: Backup to GitHub
    from app.services.backup import BackupService
    backup_result = BackupService.backup_dividend_cache()
    
    return {
        "success": True,
        "message": f"Synced dividends for {result['success_count']}/{len(all_stock_ids)} stocks across all users",
        "synced": result['success_count'],
        "total_stocks": len(all_stock_ids),
        "total_records": result['total_records'],
        "git_backup": backup_result,
        "details": result.get('details', {})
    }

