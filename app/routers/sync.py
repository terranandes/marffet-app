
from fastapi import APIRouter, HTTPException
import dividend_cache

router = APIRouter()

@router.post("/sync/dividends")
async def sync_dividends(stock_ids: str = None):
    """
    Sync dividend cache for specific stocks or all if not provided.
    stock_ids: comma-separated list of stock IDs
    """
    ids_list = stock_ids.split(",") if stock_ids else None
    result = dividend_cache.sync_all_caches(ids_list)
    return result

@router.get("/sync/dividends/list")
async def list_cached_dividends():
    """List all cached stocks."""
    return dividend_cache.list_cached_stocks()
