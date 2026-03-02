from pathlib import Path
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from app.auth import get_admin_user, GM_EMAILS
from app.services.market_data_provider import MarketDataProvider
from app.services.backup import BackupService
from app.services.crawler_service import CrawlerService

router = APIRouter()

@router.post("/refresh-market-data")
async def refresh_market_data(user: dict = Depends(get_admin_user)):
    """
    Force reload of latest price cache.
    """
    MarketDataProvider.warm_latest_cache()
    return {"status": "ok", "message": "Latest price cache warmed."}

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
    deep: Optional[bool] = Query(None),
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
    if push:
        msg += " Will push to GitHub upon completion."
    
    return {
        "status": "accepted", 
        "message": f"{msg} Monitor status via Crawler Status."
    }

@router.get("/market-data/stats")
async def get_market_data_stats(user: dict = Depends(get_admin_user)):
    """
    Return DuckDB row counts and stats.
    """
    try:
        stats = MarketDataProvider.get_stats()
        return stats
    except Exception as e:
        return {"status": "error", "error": str(e)}
@router.post("/system/initialize")
async def manual_initialize(user: dict = Depends(get_admin_user)):
    """Manually trigger MarketDataProvider warming."""
    try:
        from app.services.market_db import init_schema
        init_schema()
        MarketDataProvider.warm_latest_cache()
        return {"status": "ok", "warmed": True}
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


# ==================== Backup Download Endpoints ====================

@router.get("/backup/duckdb")
async def download_duckdb(user: dict = Depends(get_admin_user)):
    """Download the market DuckDB database file."""
    from app.services.market_db import DB_PATH
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="DuckDB file not found")
    return FileResponse(
        path=str(DB_PATH),
        filename="market.duckdb",
        media_type="application/octet-stream"
    )

@router.get("/backup/portfolio")
async def download_portfolio(user: dict = Depends(get_admin_user)):
    """Download the portfolio SQLite database file."""
    from pathlib import Path
    # Check /data/ volume first, then local
    for p in [Path("/data/portfolio.db"), Path("data/portfolio.db")]:
        if p.exists():
            return FileResponse(
                path=str(p),
                filename="portfolio.db",
                media_type="application/octet-stream"
            )
    raise HTTPException(status_code=404, detail="portfolio.db not found")


# ==================== Membership Injection Endpoints ====================

from pydantic import BaseModel

class MembershipInjectRequest(BaseModel):
    email: str
    tier: str  # 'PREMIUM' or 'VIP'
    duration_months: int

@router.post("/memberships")
async def inject_membership(req: MembershipInjectRequest, user: dict = Depends(get_admin_user)):
    """
    Manually inject a VIP or Premium membership for a Google Account email.
    Creates or extends the membership by the given duration.
    """
    from app.database import get_db
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    email = req.email.strip().lower()
    tier = req.tier.strip().upper()
    if tier not in ("PREMIUM", "VIP"):
        raise HTTPException(status_code=400, detail="Invalid tier. Must be PREMIUM or VIP.")
    
    with get_db() as conn:
        cursor = conn.cursor()
        # Check existing
        cursor.execute("SELECT valid_until FROM user_memberships WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        now = datetime.now()
        if existing and datetime.fromisoformat(existing["valid_until"]) > now:
            # Extend from current expiration
            current_expiry = datetime.fromisoformat(existing["valid_until"])
            new_expiry = current_expiry + relativedelta(months=req.duration_months)
        else:
            # New or expired, start from now
            new_expiry = now + relativedelta(months=req.duration_months)
            
        cursor.execute("""
            INSERT INTO user_memberships (email, tier, valid_until, injected_by, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(email) DO UPDATE SET 
                tier=excluded.tier, 
                valid_until=excluded.valid_until, 
                injected_by=excluded.injected_by,
                updated_at=CURRENT_TIMESTAMP
        """, (email, tier, new_expiry.isoformat(), user.get("email")))
        
    return {
        "status": "ok", 
        "message": f"Membership {tier} injected for {email}",
        "valid_until": new_expiry.isoformat()
    }

@router.get("/memberships")
async def list_memberships(user: dict = Depends(get_admin_user)):
    """
    List all active manual memberships.
    """
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_memberships ORDER BY valid_until DESC")
        records = [dict(row) for row in cursor.fetchall()]
    return records

@router.delete("/memberships/{email}")
async def revoke_membership(email: str, user: dict = Depends(get_admin_user)):
    """
    Revoke a manual membership for a given email.
    """
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_memberships WHERE email = ?", (email.strip().lower(),))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Membership not found.")
    return {"status": "ok", "message": f"Membership revoked for {email}"}

