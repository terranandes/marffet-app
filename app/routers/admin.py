from fastapi import APIRouter, Depends
from app.auth import get_admin_user
from app.services.market_cache import MarketCache
from app.services.backup import BackupService
from app.services.market_data_service import backfill_all_stocks

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

@router.post("/market-data/backfill")
async def backfill_market_data(period: str = "max", user: dict = Depends(get_admin_user)):
    """
    Trigger backfill of market data JSON files from Yahoo Finance.
    Admin-only.
    WARNING: This is a heavy operation (downloads all stock history).
    """
    # Run synchronously for now (or background task if preferred, but PRD implies direct call)
    # Ideally should be a BackgroundTask in FastAPI, but user instruction didn't specify async requirement explicitly.
    # Given "heavy operation", letting it block might timeout, but for now I will implement as requested.
    # If it's too slow, we can wrap in BackgroundTasks.
    # For "One logical commit", I will implement direct call.
    result = backfill_all_stocks(period=period)
    return result
