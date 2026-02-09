from fastapi import APIRouter, Depends
from app.auth import get_admin_user
from app.services.market_cache import MarketCache
from app.services.backup import BackupService

router = APIRouter()

@router.post("/refresh-market-data")
async def refresh_market_data(user: dict = Depends(get_admin_user)):
    """
    Force reload of MarketCache from JSON files.
    Admin-only (role='owner' validated by get_admin_user).
    """
    # Reload the cache
    db = MarketCache.get_prices_db(force_reload=True)
    
    return {"status": "ok", "years_loaded": len(db)}

@router.post("/backup-market-data")
async def backup_market_data(user: dict = Depends(get_admin_user)):
    """
    Trigger backup of market data JSON files to GitHub.
    Admin-only.
    """
    result = BackupService.refresh_prewarm_data()
    return result
