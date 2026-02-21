import logging
from typing import Dict, List, Optional, Any

# Import DB connection helper
from app.services.market_db import get_connection

logger = logging.getLogger(__name__)

class MarketDataProvider:
    """
    Single abstraction for all market data reads from DuckDB.
    Replaces MarketCache and direct JSON/SQLite queries.
    """
    
    _latest_price_cache: Dict[str, float] = {}
    _is_cache_warmed: bool = False
    _dividends_dict: Optional[Dict[str, Dict[int, Dict[str, float]]]] = None

    @classmethod
    def load_dividends_dict(cls, force_reload: bool = False) -> Dict[str, Dict[int, Dict[str, float]]]:
        """
        Load ALL dividends from DuckDB into the legacy dict format:
            {stock_id: {year: {'cash': float, 'stock': float}}}
        Cached in-memory after first load. Use force_reload=True to refresh.
        """
        if cls._dividends_dict is not None and not force_reload:
            return cls._dividends_dict

        conn = get_connection(read_only=True)
        try:
            rows = conn.execute(
                "SELECT stock_id, year, cash, stock FROM dividends ORDER BY stock_id, year"
            ).fetchall()
            result: Dict[str, Dict[int, Dict[str, float]]] = {}
            for stock_id, year, cash, stock_div in rows:
                if stock_id not in result:
                    result[stock_id] = {}
                result[stock_id][year] = {'cash': cash or 0.0, 'stock': stock_div or 0.0}
            cls._dividends_dict = result
            logger.info(f"Loaded {len(rows)} dividend records for {len(result)} stocks from DuckDB.")
            return result
        except Exception as e:
            logger.error(f"Error loading dividends dict from DuckDB: {e}")
            # Return empty dict if DuckDB is unavailable (e.g., during rebuild)
            return cls._dividends_dict or {}
        finally:
            conn.close()

    @classmethod
    def get_daily_history(cls, stock_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get full daily OHLCV for a stock. Used by Mars Strategy.
        Legacy dict-based method. Use get_daily_history_df for better performance.
        """
        conn = get_connection(read_only=True)
        try:
            query = "SELECT date, open, high, low, close, volume FROM daily_prices WHERE stock_id = ?"
            params = [stock_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date"
            
            # Execute and convert to list of dicts
            result = conn.execute(query, params).fetchall()
            return [
                {"d": r[0].strftime("%Y-%m-%d") if hasattr(r[0], 'strftime') else str(r[0]), 
                 "o": r[1], "h": r[2], "l": r[3], "c": r[4], "v": r[5]}
                for r in result
            ]
        except Exception as e:
            logger.error(f"Error fetching daily history for {stock_id}: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_daily_history_df(cls, stock_id: str, start_date: Optional[str] = None):
        """
        Fetch daily history as a Pandas DataFrame directly from DuckDB.
        """
        import pandas as pd
        conn = get_connection(read_only=True)
        try:
            query = "SELECT date, open, high, low, close, volume FROM daily_prices WHERE stock_id = ?"
            params = [stock_id]
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            query += " ORDER BY date"
            
            # Use DuckDB's .df() for high-speed conversion
            return conn.execute(query, params).df()
        except Exception as e:
            logger.error(f"Error fetching daily history DF for {stock_id}: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    @classmethod
    def get_all_daily_history_df(cls, start_date: Optional[str] = None):
        """
        Fetch ALL daily history for ALL stocks as one massive Pandas DataFrame.
        This is significantly faster for universe-wide analysis (Mars Strategy).
        """
        import pandas as pd
        conn = get_connection(read_only=True)
        try:
            query = "SELECT stock_id, date, open, high, low, close, volume FROM daily_prices"
            params = []
            if start_date:
                query += " WHERE date >= ?"
                params.append(start_date)
            query += " ORDER BY stock_id, date"
            
            return conn.execute(query, params).df()
        except Exception as e:
            logger.error(f"Error fetching ALL daily history DF: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    @classmethod
    def get_latest_price(cls, stock_id: str) -> Optional[float]:
        """
        Get latest close price for a stock.
        Checks RAM cache first, fallback to DB.
        """
        if stock_id in cls._latest_price_cache:
            return cls._latest_price_cache[stock_id]
            
        conn = get_connection(read_only=True)
        try:
            result = conn.execute(
                "SELECT close FROM daily_prices WHERE stock_id = ? ORDER BY date DESC LIMIT 1",
                [stock_id]
            ).fetchone()
            
            if result:
                price = result[0]
                cls._latest_price_cache[stock_id] = price # Update cache
                return price
            return None
        except Exception as e:
            logger.error(f"Error fetching latest price for {stock_id}: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_monthly_closes(cls, stock_ids: List[str], start_year: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get month-end closes for multiple stocks. Used by Race and Trend tabs.
        Implements monthly aggregation in SQL.
        """
        conn = get_connection(read_only=True)
        try:
            # SQL to get last trading day of each month
            # We use window function to pick the heart-of-row for each month
            query = """
                WITH MonthlyData AS (
                    SELECT 
                        stock_id, 
                        date, 
                        close,
                        ROW_NUMBER() OVER (PARTITION BY stock_id, date_trunc('month', date) ORDER BY date DESC) as row_num
                    FROM daily_prices
                    WHERE stock_id IN ({}) AND date >= ?
                )
                SELECT stock_id, date, close
                FROM MonthlyData
                WHERE row_num = 1
                ORDER BY stock_id, date
            """.format(",".join(["?"] * len(stock_ids)))
            
            start_date = f"{start_year}-01-01"
            params = stock_ids + [start_date]
            
            results = conn.execute(query, params).fetchall()
            
            # Group by stock_id
            grouped: Dict[str, List[Dict[str, Any]]] = {sid: [] for sid in stock_ids}
            for sid, date, close in results:
                grouped[sid].append({
                    "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                    "close": close
                })
            return grouped
        except Exception as e:
            logger.error(f"Error fetching monthly closes: {e}")
            return {sid: [] for sid in stock_ids}
        finally:
            conn.close()

    @classmethod
    def get_dividends(cls, stock_id: str, start_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get dividend history for a stock.
        Legacy dict-based method.
        """
        conn = get_connection(read_only=True)
        try:
            query = "SELECT year, cash, stock FROM dividends WHERE stock_id = ?"
            params = [stock_id]
            
            if start_year:
                query += " AND year >= ?"
                params.append(start_year)
                
            query += " ORDER BY year"
            
            result = conn.execute(query, params).fetchall()
            return [{"year": r[0], "cash": r[1], "stock": r[2]} for r in result]
        except Exception as e:
            logger.error(f"Error fetching dividends for {stock_id}: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_all_dividends_df(cls, start_year: Optional[int] = None):
        """
        Fetch ALL dividends for ALL stocks as a Pandas DataFrame.
        """
        import pandas as pd
        conn = get_connection(read_only=True)
        try:
            query = "SELECT stock_id, year, cash, stock FROM dividends"
            params = []
            if start_year:
                query += " WHERE year >= ?"
                params.append(start_year)
            query += " ORDER BY stock_id, year"
            
            return conn.execute(query, params).df()
        except Exception as e:
            logger.error(f"Error fetching all dividends DF: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    @classmethod
    def get_stock_list(cls) -> List[str]:
        """
        Get all known stock IDs.
        """
        conn = get_connection(read_only=True)
        try:
            result = conn.execute("SELECT stock_id FROM stocks ORDER BY stock_id").fetchall()
            return [r[0] for r in result]
        except Exception as e:
            logger.error(f"Error fetching stock list: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def warm_latest_cache(cls):
        """
        Load latest price for all stocks into tiny RAM cache (~175KB).
        Called during app startup / maintenance.
        """
        logger.info("Warming latest price cache from DuckDB...")
        conn = get_connection(read_only=True)
        try:
            # SQL to get latest price for every stock
            query = """
                SELECT stock_id, close
                FROM daily_prices
                QUALIFY ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY date DESC) = 1
            """
            results = conn.execute(query).fetchall()
            cls._latest_price_cache = {r[0]: r[1] for r in results}
            cls._is_cache_warmed = True
            logger.info(f"Buffered {len(cls._latest_price_cache)} latest prices in RAM.")
        except Exception as e:
            logger.error(f"Error warming latest cache: {e}")
        finally:
            conn.close()

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Return DuckDB row counts and descriptive stats.
        """
        conn = get_connection(read_only=True)
        try:
            price_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
            div_count = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
            stock_count = conn.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
            
            res_dates = conn.execute("SELECT MIN(date), MAX(date) FROM daily_prices").fetchone()
            distinct_stocks_prices = conn.execute("SELECT COUNT(DISTINCT stock_id) FROM daily_prices").fetchone()[0]
            
            return {
                "price_rows": price_count,
                "dividend_rows": div_count,
                "stock_rows": stock_count,
                "min_date": str(res_dates[0]) if res_dates[0] else None,
                "max_date": str(res_dates[1]) if res_dates[1] else None,
                "distinct_stocks_prices": distinct_stocks_prices,
                "cache_warmed": cls._is_cache_warmed,
                "cache_size": len(cls._latest_price_cache)
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
