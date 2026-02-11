from fastapi import APIRouter, BackgroundTasks, Depends
from app.auth import get_admin_user
from app.services.market_cache import MarketCache
from app.services.backup import BackupService
from app.services.crawler_service import CrawlerService

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
async def backfill_market_data(
    background_tasks: BackgroundTasks,
    period: str = "max", 
    overwrite: bool = False,
    user: dict = Depends(get_admin_user)
):
    """
    Trigger backfill of market data JSON files from Yahoo Finance (Background Task).
    Admin-only.
    """
    # Trigger via CrawlerService to manage background state
    background_tasks.add_task(CrawlerService.run_universe_backfill, period=period, overwrite=overwrite)
    
    return {
        "status": "accepted", 
        "message": "Universe Backfill started in background. Monitor status via Crawler Status."
    }
