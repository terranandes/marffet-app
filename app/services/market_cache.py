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
    START_YEAR = 2000  # yfinance supports unadjusted prices from 2000+
    END_YEAR = 2026

    @classmethod
    def get_prices_db(cls, force_reload: bool = False) -> Dict[int, Dict[str, Any]]:
        """
        Returns the Prices Database: { Year: { StockID: {Start, End, High, Low...} } }
        Lazy loads heavily on first call.
        """
        global _PRICES_CACHE, _IS_LOADED

        if _IS_LOADED and not force_reload:
            return _PRICES_CACHE

        logging.info("[MarketCache] Warming up... Loading 20 years of price data into memory.")
        new_cache = {}

        for year in range(cls.START_YEAR, cls.END_YEAR + 1):
            year_data = {}
            
            # 1. Main Market
            p_file = cls.DATA_DIR / f"Market_{year}_Prices.json"
            if p_file.exists():
                try:
                    with open(p_file, "r") as f:
                        year_data.update(json.load(f))
                except Exception as e:
                    logging.error(f"[MarketCache] Error loading {p_file}: {e}")

            # 2. TPEx Market (OTC)
            tpex_file = cls.DATA_DIR / f"TPEx_Market_{year}_Prices.json"
            if tpex_file.exists():
                try:
                    with open(tpex_file, "r") as f:
                        year_data.update(json.load(f))
                except Exception as e:
                    logging.error(f"[MarketCache] Error loading {tpex_file}: {e}")
            
            new_cache[year] = year_data
        
        logging.info(f"[MarketCache] Loaded {len(new_cache)} years. (RAM Usage: ~100MB)")
        _PRICES_CACHE = new_cache
        _IS_LOADED = True
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
