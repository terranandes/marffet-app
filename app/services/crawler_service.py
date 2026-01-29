import asyncio
import os
import glob
from app.project_tw.run_analysis import main as run_analysis_main

class CrawlerService:
    _is_running = False
    _last_run_time = None
    _last_run_status = "idle" # idle, running, success, error
    _last_message = ""
    _progress_pct = 0
    _start_time = None

    @classmethod
    def get_status(cls):
        import datetime
        elapsed = 0
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if cls._start_time:
            if cls._is_running:
                elapsed = (now - cls._start_time).total_seconds()
            elif cls._last_run_time:
                # If finished, calculate total duration
                elapsed = (cls._last_run_time - cls._start_time).total_seconds()

        return {
            "is_running": cls._is_running,
            "last_run_time": cls._last_run_time.isoformat() if cls._last_run_time else None,
            "status": cls._last_run_status,
            "message": cls._last_message,
            "progress_pct": cls._progress_pct,
            "elapsed_seconds": int(elapsed)
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
        cls._progress_pct = 0
        import datetime
        cls._start_time = datetime.datetime.now(datetime.timezone.utc)
            
            # ... (execution) ...
        try:
            print("[CrawlerService] Starting Market Analysis...")
            
            if force_cold_run:
                print("[CrawlerService] FORCE COLD RUN: Clearing current year cache...")
                cls._last_message = "Clearing Cache..."
                cls._progress_pct = 5
                
                # FORCE COLD RUN: Clear ALL cache for full rebuild (User Request)
                # This ensures we recover missing historic data (e.g. 6238 in 2015)
                # Delete data/raw/*.json matching patterns
                data_dir = "data/raw"
                if os.path.exists(data_dir):
                    patterns = [
                        f"{data_dir}/Market_*_Prices.json",
                        f"{data_dir}/TPEx_Market_*_Prices.json",
                        f"{data_dir}/TPEx_Dividends_*.json",
                        f"{data_dir}/TWSE_Dividends_*.json",
                        f"{data_dir}/TWT49U_*.json" # Also clear TWT49U raw cache
                    ]
                    
                    count = 0
                    for p in patterns:
                        for f in glob.glob(p):
                            try:
                                os.remove(f)
                                count += 1
                            except: pass
                    print(f"[CrawlerService] Cleared {count} cache files (Full Rebuild)")

            # Run Analysis
            # Run Analysis
            cls._progress_pct = 10
            def update_status(msg, pct=None):
                cls._last_message = msg
                if pct is not None:
                    cls._progress_pct = pct
                else:
                    # Fallback Heuristic
                    if "Analyzing" in msg: cls._progress_pct = 20
                    elif "Processing" in msg: cls._progress_pct = 80
                    elif "Saving" in msg: cls._progress_pct = 90
                print(f"[CrawlerService Status] ({cls._progress_pct}%) {msg}")

            await run_analysis_main(status_callback=update_status)
            import datetime
            cls._last_run_time = datetime.datetime.now(datetime.timezone.utc)
            cls._last_run_status = "success"
            cls._last_message = "Analysis completed successfully."
            cls._progress_pct = 100
            
            print("[CrawlerService] Market Analysis Complete.")
            return {"status": "success", "message": "Analysis completed"}
            
        except Exception as e:
            import datetime
            cls._last_run_time = datetime.datetime.now(datetime.timezone.utc)
            cls._last_run_status = "error"
            cls._last_message = str(e)
            print(f"[CrawlerService] Error: {e}")
            return {"status": "error", "message": str(e)}
            print(f"[CrawlerService] Error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cls._is_running = False
