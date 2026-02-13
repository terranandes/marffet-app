"""
Dividend Cache Management

HYBRID APPROACH:
- Static Files: app/data/dividends/{stock_id}.json (git-versioned, pre-warm)
- DB Table: dividend_cache (runtime updates, persists on Zeabur)

Read Order: File → DB → yfinance
Write: Both file + DB
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Cache directory path
CACHE_DIR = Path(__file__).parent / "data" / "dividends"


def _get_cache_path(stock_id: str) -> Path:
    """Get cache file path for a stock."""
    # Normalize stock_id (remove .TW suffix if present)
    clean_id = stock_id.replace(".TW", "").replace(".TWO", "")
    return CACHE_DIR / f"{clean_id}.json"


def _normalize_stock_id(stock_id: str) -> str:
    """Normalize stock_id by removing .TW/.TWO suffix."""
    return stock_id.replace(".TW", "").replace(".TWO", "")


# ============ DB OPERATIONS ============

def _init_db_table():
    """Ensure dividend_cache table exists."""
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_cache (
                stock_id TEXT PRIMARY KEY,
                stock_name TEXT,
                last_synced TEXT,
                dividends_json TEXT
            )
        """)
        conn.commit()


def _get_from_db(stock_id: str) -> Optional[list[dict]]:
    """Get dividends from DB table."""
    from app.database import get_db
    clean_id = _normalize_stock_id(stock_id)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT dividends_json FROM dividend_cache WHERE stock_id = ?",
                (clean_id,)
            )
            row = cursor.fetchone()
            if row and row['dividends_json']:
                return json.loads(row['dividends_json'])
    except Exception as e:
        print(f"[DividendCache] DB read error for {clean_id}: {e}")
    return None


def _save_to_db(stock_id: str, stock_name: str, dividends: list[dict]):
    """Save dividends to DB table."""
    from app.database import get_db
    clean_id = _normalize_stock_id(stock_id)
    
    try:
        _init_db_table()  # Ensure table exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO dividend_cache (stock_id, stock_name, last_synced, dividends_json)
                VALUES (?, ?, ?, ?)
            """, (
                clean_id,
                stock_name,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(dividends, ensure_ascii=False)
            ))
            conn.commit()
    except Exception as e:
        print(f"[DividendCache] DB write error for {clean_id}: {e}")


# ============ FILE OPERATIONS ============

def _get_from_file(stock_id: str) -> Optional[list[dict]]:
    """Read dividends from cache file."""
    cache_path = _get_cache_path(stock_id)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("dividends", [])
    except (json.JSONDecodeError, IOError) as e:
        print(f"[DividendCache] File read error {cache_path}: {e}")
        return None


def _save_to_file(stock_id: str, stock_name: str, dividends: list[dict]):
    """Save dividends to cache file."""
    clean_id = _normalize_stock_id(stock_id)
    
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _get_cache_path(clean_id)
        cache_data = {
            "stock_id": clean_id,
            "stock_name": stock_name,
            "last_synced": datetime.now(timezone.utc).isoformat(),
            "source": "yfinance",
            "dividends": dividends
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DividendCache] File write error for {clean_id}: {e}")


# ============ PUBLIC API ============

def get_cached_dividends(stock_id: str) -> Optional[list[dict]]:
    """
    Get dividends using READ ORDER: File → DB → None
    
    Returns list of {"date": "YYYY-MM-DD", "amount": float} or None if not cached.
    """
    clean_id = _normalize_stock_id(stock_id)
    
    # 1st: Check Static File
    result = _get_from_file(clean_id)
    if result:
        return result
    
    # 2nd: Check DB
    result = _get_from_db(clean_id)
    if result:
        return result
    
    # 3rd: Not cached
    return None


def get_cache_info(stock_id: str) -> Optional[dict]:
    """Get cache metadata (stock_name, last_synced, etc.)"""
    cache_path = _get_cache_path(stock_id)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "stock_id": data.get("stock_id"),
                "stock_name": data.get("stock_name"),
                "last_synced": data.get("last_synced"),
                "record_count": len(data.get("dividends", []))
            }
    except (json.JSONDecodeError, IOError):
        return None


def sync_dividend_cache(stock_id: str, stock_name: str = None) -> dict:
    """
    Fetch dividends from yfinance and save to BOTH file + DB.
    
    Returns {"success": bool, "message": str, "records": int}
    """
    import yfinance as yf
    
    clean_id = _normalize_stock_id(stock_id)
    ticker_symbol = f"{clean_id}.TW"
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        div_series = ticker.dividends
        
        if div_series.empty:
            # Try .TWO for OTC stocks
            ticker_symbol = f"{clean_id}.TWO"
            ticker = yf.Ticker(ticker_symbol)
            div_series = ticker.dividends
        
        if div_series.empty:
            return {"success": False, "message": f"No dividend data found for {clean_id}", "records": 0}
        
        # Convert to list of records
        dividends = []
        for date, amount in div_series.items():
            dividends.append({
                "date": date.strftime("%Y-%m-%d"),
                "amount": round(float(amount), 6)
            })
        
        # Sort by date descending (newest first)
        dividends.sort(key=lambda x: x["date"], reverse=True)
        
        # Get stock name from yfinance if not provided
        # Get stock name from yfinance if not provided
        if not stock_name:
            # Priority 1: Check Global Cache (Official TWSE Name)
            try:
                from app.config import STOCK_NAME_CACHE
                stock_name = STOCK_NAME_CACHE.get(clean_id)
            except ImportError:
                pass

            # Priority 2: YFinance Shortname (Fallback)
            if not stock_name:
                try:
                    stock_name = ticker.info.get("shortName", clean_id)
                except:
                    stock_name = clean_id
        
        # WRITE TO BOTH: File + DB + DuckDB
        _save_to_file(clean_id, stock_name, dividends)
        _save_to_db(clean_id, stock_name, dividends)
        
        # WRITE TO DUCKDB (Task 8 Alignment)
        try:
            from app.services.market_db import get_connection
            conn = get_connection()
            # Convert yfinance records to yearly summary (DuckDB dividends table is yearly)
            # Strategy: Sum up dividends by year
            yearly_divs = {}
            for d in dividends:
                y = int(d['date'][:4])
                if y not in yearly_divs: yearly_divs[y] = 0.0
                yearly_divs[y] += d['amount']
            
            div_rows = []
            for y, amount in yearly_divs.items():
                div_rows.append((clean_id, y, float(amount), 0.0)) # stock dividend is usually 0 from simple series
            
            if div_rows:
                conn.executemany("""
                    INSERT INTO dividends (stock_id, year, cash, stock)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (stock_id, year) DO UPDATE SET
                        cash = EXCLUDED.cash, stock = EXCLUDED.stock
                """, div_rows)
            conn.close()
        except Exception as e:
            print(f"[DividendCache] DuckDB write error for {clean_id}: {e}")
        
        return {
            "success": True, 
            "message": f"Synced {len(dividends)} dividend records for {clean_id}",
            "records": len(dividends)
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error syncing {clean_id}: {str(e)}", "records": 0}


def sync_all_caches(stock_ids: list[str] = None) -> dict:
    """
    Sync dividend cache for multiple stocks.
    
    If stock_ids is None, syncs all existing cache files.
    """
    results = {}
    
    if stock_ids is None:
        # Get all existing cache files
        if CACHE_DIR.exists():
            stock_ids = [f.stem for f in CACHE_DIR.glob("*.json")]
        else:
            stock_ids = []
    
    for stock_id in stock_ids:
        result = sync_dividend_cache(stock_id)
        results[stock_id] = result
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    total_records = sum(r.get("records", 0) for r in results.values())
    
    return {
        "total_stocks": len(stock_ids),
        "success_count": success_count,
        "total_records": total_records,
        "details": results
    }


def list_cached_stocks() -> list[dict]:
    """List all stocks with cached dividend data."""
    if not CACHE_DIR.exists():
        return []
    
    cached = []
    for cache_file in CACHE_DIR.glob("*.json"):
        info = get_cache_info(cache_file.stem)
        if info:
            cached.append(info)
    
    return sorted(cached, key=lambda x: x.get("stock_id", ""))


# CLI interface for manual syncing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python dividend_cache.py --sync <stock_id> [stock_name]")
        print("  python dividend_cache.py --sync-all")
        print("  python dividend_cache.py --list")
        print("  python dividend_cache.py --prewarm")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "--sync" and len(sys.argv) >= 3:
        stock_id = sys.argv[2]
        stock_name = sys.argv[3] if len(sys.argv) > 3 else None
        result = sync_dividend_cache(stock_id, stock_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif cmd == "--sync-all":
        result = sync_all_caches()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif cmd == "--list":
        cached = list_cached_stocks()
        print(f"Cached stocks: {len(cached)}")
        for c in cached:
            print(f"  {c['stock_id']:8} | {c.get('stock_name', 'N/A'):20} | {c['record_count']} records | {c.get('last_synced', 'N/A')}")
            
    elif cmd == "--prewarm":
        # Pre-warm with common TW stocks
        PREWARM_STOCKS = [
            ("2330", "台積電"),
            ("2317", "鴻海"),
            ("2454", "聯發科"),
            ("2412", "中華電"),
            ("2308", "台達電"),
            ("0050", "元大台灣50"),
            ("0056", "元大高股息"),
            ("00878", "國泰永續高股息"),
        ]
        
        print("Pre-warming dividend cache...")
        for stock_id, stock_name in PREWARM_STOCKS:
            result = sync_dividend_cache(stock_id, stock_name)
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {stock_id} ({stock_name}): {result['message']}")
        
        print("\nDone! Run --list to see cached stocks.")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
