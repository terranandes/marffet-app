from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from app.auth import get_admin_user, get_current_user, GM_EMAILS
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

@router.post("/market-data/supplemental")
async def supplement_market_data(background_tasks: BackgroundTasks, user: dict = Depends(get_admin_user)):
    """
    Trigger Smart Supplemental Refresh (Held Stocks + Top Universe).
    Uses Background Task to run the python supplement script.
    """
    import subprocess
    import sys
    from pathlib import Path
    
    def run_supplement():
        script_path = Path("scripts/cron/supplement_prices.py")
        if script_path.exists():
            subprocess.run(["uv", "run", "python", str(script_path)], check=False)
            
    background_tasks.add_task(run_supplement)
    return {"status": "accepted", "message": "Smart Supplemental Refresh started in background."}

@router.post("/market-data/backfill")
async def backfill_market_data(
    background_tasks: BackgroundTasks,
    period: str = "max", 
    overwrite: bool = False,
    push: bool = False,
    deep: bool = False,
    user: dict = Depends(get_admin_user)
):
    """
    Trigger backfill of market data JSON files from Yahoo Finance (Background Task).
    Admin-only.
    """
    # Trigger via CrawlerService to manage background state
    background_tasks.add_task(
        CrawlerService.run_universe_backfill, 
        period=period, 
        overwrite=overwrite,
        push_to_github=push,
        include_warrants=deep
    )
    
    msg = "Universe Backfill started."
    if push: msg += " Will push to GitHub upon completion."
    
    return {
        "status": "accepted", 
        "message": f"{msg} Monitor status via Crawler Status."
    }
@router.post("/system/initialize")
async def manual_initialize(user: dict = Depends(get_admin_user)):
    """Manually trigger MarketCache loading if startup failed."""
    try:
        MarketCache.get_prices_db(force_reload=True)
        import app.services.market_cache as mc
        return {"status": "ok", "loaded": mc._IS_LOADED, "years": len(mc._PRICES_CACHE)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/backup")
async def trigger_backup(user: dict = Depends(get_admin_user)):
    """Trigger manual database backup to GitHub."""
    result = BackupService.backup_db()
    
    if result.get("status") == "success":
        return {"message": "Backup successful", "details": result}
    elif result.get("status") == "skipped":
        return {"message": "Backup skipped (missing config)", "details": result}
    else:
        raise HTTPException(status_code=500, detail=f"Backup failed: {result.get('reason')}")

@router.post("/refresh-prewarm")
async def trigger_prewarm_refresh(background_tasks: BackgroundTasks, user: dict = Depends(get_admin_user)):
    """Trigger pre-warm data refresh to GitHub (Background Task)."""
    if not user or user.get('email') not in GM_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run in background to prevent timeout
    async def run_bg_prewarm():
        await BackupService.annual_prewarm_with_rebuild()
        
    background_tasks.add_task(run_bg_prewarm)
    return {"message": "Pre-warm Rebuild & Push started in background.", "status": "accepted"}

@router.post("/market-data/push")
async def force_push_to_github(background_tasks: BackgroundTasks, user: dict = Depends(get_admin_user)):
    """
    Trigger immediate push of market data JSON files to GitHub.
    Admin-only.
    """
    background_tasks.add_task(BackupService.refresh_prewarm_data)
    return {"status": "accepted", "message": "Market data push-to-GitHub started in background."}

@router.post("/market-data/sync-dividends")
async def trigger_dividend_sync(background_tasks: BackgroundTasks, user: dict = Depends(get_admin_user)):
    """
    Trigger Global Dividend Sync (Universe) + GitHub Push.
    Admin-only.
    """
    background_tasks.add_task(BackupService.run_quarterly_dividend_sync)
    return {"status": "accepted", "message": "Global Dividend Sync started in background."}
