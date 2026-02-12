import asyncio
import os
import glob
import datetime
from app.project_tw.run_analysis import main as run_analysis_main

class CrawlerService:
    _is_running = False
    _last_run_time = None
    _last_run_status = "idle" # idle, running, success, error
    _last_message = ""
    _progress_pct = 0
    _start_time = None
    
    # Dedicated state for Backfill (Shared with Crawler UI for simplicity, or separate if requested)
    # Using shared state but with different message prefixes to keep UI logic simple.

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
            
            # Always Update Stock List Cache (O(1) Fetch)
            # This ensures we catch new IPOs even in "Smart Update" mode
            print("[CrawlerService] Updating Stock List from TWSE/TPEX...")
            try:
                from app.services.stock_info_service import StockInfoService
                from starlette.concurrency import run_in_threadpool
                
                # Run sync request in threadpool to avoid blocking status polling
                await run_in_threadpool(StockInfoService.update_cache)
            except Exception as ex:
                print(f"[CrawlerService] Failed to update stock list: {ex}")

            if force_cold_run:
                print("[CrawlerService] FORCE COLD RUN: Clearing current year cache...")
                cls._last_message = "Clearing Cache..."
                cls._progress_pct = 5
                
                # Only clear Current Year to avoid 3-min wait
                current_year = datetime.datetime.now().year
                
                # Delete data/raw/*{year}*.json (correct path)
                data_dir = "data/raw"
                if os.path.exists(data_dir):
                    patterns = [
                        f"{data_dir}/Market_{current_year}_Prices.json",
                        f"{data_dir}/TPEx_Market_{current_year}_Prices.json",
                        f"{data_dir}/TPEx_Dividends_{current_year}.json",
                        f"{data_dir}/TWSE_Dividends_{current_year}.json",
                    ]
                    
                    def clear_cache_files():
                        count = 0
                        for p in patterns:
                            for f in glob.glob(p):
                                try:
                                    os.remove(f)
                                    count += 1
                                except: pass
                        return count

                    # Run file deletion in threadpool
                    count = await run_in_threadpool(clear_cache_files)
                    print(f"[CrawlerService] Cleared {count} cache files for {current_year}")

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

    @classmethod
    async def run_universe_backfill(cls, period: str = "max", overwrite: bool = False, push_to_github: bool = False):
        """
        Run the Full Universe Backfill (2000-Present).
        """
        if cls._is_running:
            return {"status": "skipped", "message": "Another background task is already running"}
            
        cls._is_running = True
        cls._last_run_status = "running"
        cls._last_message = "Universe Backfill initiated..."
        cls._progress_pct = 1 # Start at 1%
        cls._start_time = datetime.datetime.now(datetime.timezone.utc)
        
        try:
            from app.services.market_data_service import backfill_all_stocks
            from starlette.concurrency import run_in_threadpool
            
            def progress_hook(msg, pct):
                cls._last_message = f"[Backfill] {msg}"
                cls._progress_pct = pct
                print(f"[CrawlerService Backfill] ({pct}%) {msg}")

            # Run the heavy sync operation in a threadpool
            result = await run_in_threadpool(
                backfill_all_stocks, 
                period=period, 
                overwrite=overwrite, 
                progress_callback=progress_hook
            )
            
            # Check for error from service
            if result.get("status") == "error":
                cls._last_run_status = "error"
                cls._last_message = f"Backfill Error: {result.get('message')}"
                cls._progress_pct = 0
                cls._last_run_time = datetime.datetime.now(datetime.timezone.utc)
                return result

            # Step 2: Push to GitHub if requested
            if push_to_github:
                from app.services.backup import BackupService
                cls._last_message = "Universe Backfill complete. Pushing to GitHub..."
                push_result = BackupService.refresh_prewarm_data()
                result["github_push"] = push_result
                if push_result.get("status") == "success":
                    cls._last_message = f"Universe Backfill & Push complete. Commit: {push_result.get('commit_sha')}"
                else:
                    cls._last_message = f"Universe Backfill complete, but Push failed: {push_result.get('reason')}"
            else:
                cls._last_message = "Universe Backfill completed successfully."

            cls._last_run_time = datetime.datetime.now(datetime.timezone.utc)
            cls._last_run_status = "success"
            cls._progress_pct = 100
            
            return result
            
        except Exception as e:
            cls._last_run_time = datetime.datetime.now(datetime.timezone.utc)
            cls._last_run_status = "error"
            cls._last_message = f"Backfill Error: {str(e)}"
            print(f"[CrawlerService Backfill] Error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cls._is_running = False
