import asyncio
import os
import glob
from project_tw.run_analysis import main as run_analysis_main

class CrawlerService:
    _is_running = False
    _last_run_time = None
    _last_run_status = "idle" # idle, running, success, error
    _last_message = ""

    @classmethod
    def get_status(cls):
        return {
            "is_running": cls._is_running,
            "last_run_time": cls._last_run_time.isoformat() if cls._last_run_time else None,
            "status": cls._last_run_status,
            "message": cls._last_message
        }

    @classmethod
    async def run_market_analysis(cls, force_cold_run: bool = False):
        """
        Run the full Mars Strategy Analysis (Crawler + Calc).
        """
        if cls._is_running:
            return {"status": "skipped", "message": "Analysis already running"}
            
            cls._is_running = True
            cls._last_run_status = "running"
            cls._last_message = "Analysis in progress..."
            
            # ... (execution) ...
        try:
            print("[CrawlerService] Starting Market Analysis...")
            
            if force_cold_run:
                print("[CrawlerService] FORCE COLD RUN: Clearing current year cache...")
                # Only clear Current Year to avoid 3-min wait
                import datetime
                current_year = datetime.datetime.now().year
                
                # Delete project_tw/data/raw/*{year}*.json
                # Pattern: Market_2026_Prices.json, 2330_20261201.json
                # Be careful not to delete history.
                # Actually, with Smart Caching implemented, we don't strictly need to delete files 
                # if we rely on the 24h expiry.
                # BUT user explicitly asked for "Cold Run" to force update NOW.
                # So we should touch/delete current year files.
                
                data_dir = "project_tw/data/raw"
                if os.path.exists(data_dir):
                    patterns = [
                        f"{data_dir}/Market_{current_year}_Prices.json",
                        f"{data_dir}/TPEx_Market_{current_year}_Prices.json",
                        f"{data_dir}/TPEx_Dividends_{current_year}.json",
                        f"{data_dir}/*_{current_year}*.json" # individual stock months
                    ]
                    
                    count = 0
                    for p in patterns:
                        for f in glob.glob(p):
                            try:
                                os.remove(f)
                                count += 1
                            except: pass
                    print(f"[CrawlerService] Cleared {count} cache files for {current_year}")

            # Run Analysis
            await run_analysis_main()
            import datetime
            cls._last_run_time = datetime.datetime.now()
            cls._last_run_status = "success"
            cls._last_message = "Analysis completed successfully."
            
            print("[CrawlerService] Market Analysis Complete.")
            return {"status": "success", "message": "Analysis completed"}
            
        except Exception as e:
            import datetime
            cls._last_run_time = datetime.datetime.now()
            cls._last_run_status = "error"
            cls._last_message = str(e)
            print(f"[CrawlerService] Error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cls._is_running = False
