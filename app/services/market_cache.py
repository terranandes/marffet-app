import json
import logging
from pathlib import Path
from typing import Dict, Any

# Singleton Cache
_PRICES_CACHE: Dict[int, Dict[str, Any]] = {}
_IS_LOADED: bool = False

class MarketCache:
    """
    In-Memory Cache for Market Data (Prices).
    Solves the "20 File Reads per Request" latency issue.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data/raw"
    import datetime
    START_YEAR = 2000  # yfinance supports unadjusted prices from 2000+
    END_YEAR = datetime.datetime.now().year

    @classmethod
    def get_prices_db(cls, force_reload: bool = False, incremental: bool = False) -> Dict[int, Dict[str, Any]]:
        """
        Returns the Prices Database: { Year: { StockID: {Start, End, High, Low...} } }
        Lazy loads heavily on first call.
        
        Args:
            force_reload: Re-read all files even if cache is loaded.
            incremental: If True, sleep between years to avoid spiking memory/CPU (Cloud safety).
        """
        global _PRICES_CACHE, _IS_LOADED
        import os
        import time

        if _IS_LOADED and not force_reload:
            return _PRICES_CACHE
        
        IS_CLOUD = os.getenv("ZEABUR") or os.getenv("RAILWAY") or os.getenv("RENDER")

        logging.info(f"[MarketCache] Warming up... Loading price data. (Cloud={IS_CLOUD}, Incremental={incremental})")
        
        # Don't overwrite the global cache until we are finished to avoid partial state during web requests
        # UNLESS it's a force_reload or first load, in which case we populate _PRICES_CACHE directly
        # but for background warmup, we can build it incrementally.
        
        loaded_count = 0
        skipped_count = 0

        try:
            # We iterate year by year. If incremental, we sleep 2 seconds between years to give GC time.
            for year in range(cls.END_YEAR, cls.START_YEAR - 1, -1): # Start from newest year (most relevant)
                if year in _PRICES_CACHE and not force_reload:
                    continue
                    
                year_data = {}
                
                # 1. Main Market
                p_file = cls.DATA_DIR / f"Market_{year}_Prices.json"
                if p_file.exists():
                    try:
                        with open(p_file, "r") as f:
                            year_data.update(json.load(f))
                        loaded_count += 1
                    except Exception as e:
                        logging.error(f"[MarketCache] Error loading {p_file}: {type(e).__name__}: {e}")
                        skipped_count += 1
                        # Robustness: Move corrupted file aside so it doesn't crash us again
                        try:
                            corrupt_path = p_file.with_suffix(".json.corrupted")
                            os.replace(p_file, corrupt_path)
                            logging.warning(f"[MarketCache] Moved corrupted {p_file.name} to {corrupt_path.name}")
                        except: pass

                # 2. TPEx Market (OTC)
                tpex_file = cls.DATA_DIR / f"TPEx_Market_{year}_Prices.json"
                if tpex_file.exists():
                    try:
                        with open(tpex_file, "r") as f:
                            year_data.update(json.load(f))
                        loaded_count += 1
                    except Exception as e:
                        logging.error(f"[MarketCache] Error loading {tpex_file}: {type(e).__name__}: {e}")
                        skipped_count += 1
                        # Robustness: Move corrupted file aside
                        try:
                            corrupt_path = tpex_file.with_suffix(".json.corrupted")
                            os.replace(tpex_file, corrupt_path)
                            logging.warning(f"[MarketCache] Moved corrupted {tpex_file.name} to {corrupt_path.name}")
                        except: pass
                
                if year_data:
                    _PRICES_CACHE[year] = year_data
                
                # Cloud Safety: Stun the load to avoid 512MB RAM ceiling
                if incremental and IS_CLOUD:
                    time.sleep(1.0) # 1 sec gap between years for GC
                    import gc
                    gc.collect()

            _IS_LOADED = True
            logging.info(f"[MarketCache] Done. Loaded {loaded_count} files, skipped {skipped_count}. Total Years: {len(_PRICES_CACHE)}")
            
        except BaseException as e:
            logging.error(f"[MarketCache] Fatal error during cache load: {type(e).__name__}: {e}")
        
        return _PRICES_CACHE

    @classmethod
    def get_stock_history_fast(cls, stock_id: str) -> list:
        """
        Optimized history fetch using memory cache.
        Returns list of daily dictionaries if available (Schema V2),
        or yearly summaries if not (Schema V1).
        """
        db = cls.get_prices_db()
        history = []
        
        for year in sorted(db.keys()):
            yd = db[year]
            if stock_id in yd:
                node = yd[stock_id]
                
                # CHECK SCHEMA V2 (Daily Data)
                if "daily" in node and node["daily"]:
                    # Transform V2 Daily (d,o,h,l,c,v) -> App Format
                    # App Format: {year, date, open, high, low, close, volume}
                    for day in node["daily"]:
                        history.append({
                            "year": int(year),
                            "date": day["d"],
                            "open": day["o"],
                            "high": day["h"],
                            "low": day["l"],
                            "close": day["c"],
                            "volume": day["v"]
                        })
                
                # FALLBACK SCHEMA V1 (Yearly Summary)
                elif "summary" in node:
                    # V2 Summary
                    s = node["summary"]
                    history.append({
                        "year": int(year),
                        "open": s.get('start'),
                        "close": s.get('end'),
                        "high": s.get('high'),
                        "low": s.get('low')
                    })
                else:
                    # V1 Legacy
                    history.append({
                        "year": int(year),
                        "open": node.get('first_open', node.get('start', 0)),
                        "close": node.get('end', 0),
                        "high": node.get('high', 0),
                        "low": node.get('low', 0)
                    })
        return history
