
import os
import base64
import requests
import logging
from datetime import datetime
from app.database import get_db, DB_PATH
from app.repositories import target_repo

logger = logging.getLogger(__name__)

class BackupService:
    @staticmethod
    def backup_db():
        """
        Backup portfolio.db to GitHub repository.
        Requires GITHUB_TOKEN and GITHUB_REPO env vars.
        TARGET PATH: /app/portfolio.db in the repo.
        """
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO") # e.g. "terranandes/marffet-app"
        
        if not token or not repo:
            logger.warning("[Backup] GITHUB_TOKEN or GITHUB_REPO not set. Skipping backup.")
            return {"status": "skipped", "reason": "missing_env_vars"}
            
        if not DB_PATH.exists():
            logger.error(f"[Backup] Database file not found at {DB_PATH}")
            return {"status": "error", "reason": "db_not_found"}

        try:
            # 1. Read DB file
            with open(DB_PATH, "rb") as f:
                content = f.read()
            
            encoded_content = base64.b64encode(content).decode("utf-8")
            
            # 2. Check if file exists (to get SHA)
            target_path = "app/portfolio.db"
            url = f"https://api.github.com/repos/{repo}/contents/{target_path}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            
            sha = None
            resp_get = requests.get(url, headers=headers)
            if resp_get.status_code == 200:
                sha = resp_get.json().get("sha")
            
            # 3. Upload / Update
            payload = {
                "message": f"Backup portfolio.db {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": encoded_content,
                "branch": "master" # Default branch
            }
            if sha:
                payload["sha"] = sha
                
            resp_put = requests.put(url, headers=headers, json=payload)
            
            if resp_put.status_code in (200, 201):
                logger.info(f"[Backup] Successfully backed up to {repo}/{target_path}")
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                logger.error(f"[Backup] GitHub API Error: {resp_put.text}")
                return {"status": "error", "reason": "github_api_error", "details": resp_put.text}
                
        except Exception as e:
            logger.exception(f"[Backup] Failed: {e}")
            return {"status": "error", "reason": str(e)}

    @staticmethod
    def check_and_backup_if_needed():
        """
        Check if the last backup on GitHub is older than 20 hours.
        If so, trigger a backup immediately.
        Used on Startup to handle Ephemeral Container restarts (Zeabur) which might miss cron windows.
        """
        from datetime import timezone, timedelta
        
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        
        if not token or not repo:
            return
            
        try:
            target_path = "app/portfolio.db"
            url = f"https://api.github.com/repos/{repo}/commits?path={target_path}&per_page=1"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                commits = resp.json()
                if commits and len(commits) > 0:
                    last_date_str = commits[0]["commit"]["committer"]["date"]
                    # Format: 2024-01-25T15:00:00Z
                    last_backup_time = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
                    
                    now = datetime.now(timezone.utc)
                    age = now - last_backup_time
                    
                    logger.info(f"[BackupCheck] Last backup was {age} ago ({last_backup_time})")
                    
                    if age > timedelta(hours=20):
                        logger.info("[BackupCheck] Backup is stale (>20h). Triggering immediate backup...")
                        BackupService.backup_db()
                    else:
                        logger.info("[BackupCheck] Backup is fresh. Skipping.")
                        
                else:
                     # File likely doesn't exist or no commits, try backup
                     logger.info("[BackupCheck] No history found. Triggering backup.")
                     BackupService.backup_db()
            else:
                 logger.warning(f"[BackupCheck] Failed to check history: {resp.status_code}")
                 
        except Exception as e:
            logger.error(f"[BackupCheck] Error verifying backup status: {e}")
            
    @staticmethod
    async def annual_prewarm_with_rebuild():
        """
        Annual scheduled job: Rebuild cache data, then push to GitHub.
        Called on Jan 1st via APScheduler or manually from Admin Dashboard.
        """
        from app.services.crawler_service import CrawlerService
        
        logger.info("[Annual Pre-warm] Starting Rebuild + Push...")
        
        try:
            # Step 1: Run Cold Run to regenerate data (async)
            result = await CrawlerService.run_market_analysis(force_cold_run=True)
            
            if result.get("status") != "success":
                logger.error(f"[Annual Pre-warm] Rebuild failed: {result}")
                return {"status": "error", "reason": "rebuild_failed", "details": result}
            
            logger.info("[Annual Pre-warm] Rebuild complete. Now pushing to GitHub...")
            
            # Step 2: Push refreshed files to GitHub
            push_result = BackupService.refresh_prewarm_data()
            
            logger.info(f"[Annual Pre-warm] Complete: {push_result}")
            return {
                "status": "success",
                "rebuild": result,
                "push": push_result
            }
            
        except Exception as e:
            logger.exception(f"[Annual Pre-warm] Failed: {e}")
            return {"status": "error", "reason": str(e)}

    @staticmethod
    def refresh_prewarm_data():
        """
        Backup pre-warm cache files (data/raw/*.json) to GitHub repository.
        Uses Git Trees API to create a SINGLE commit for all files.
        """
        from pathlib import Path
        
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        
        if not token or not repo:
            logger.warning("[PreWarm] GITHUB_TOKEN or GITHUB_REPO not set.")
            return {"status": "skipped", "reason": "missing_env_vars"}
        
        # Target files: Market prices, TPEx prices, Dividends, ListingDates
        data_dir = Path("data/raw")
        if not data_dir.exists():
            return {"status": "error", "reason": "data/raw not found"}
        
        # Filter patterns (exclude CB_Issuance - too large and changes daily)
        patterns = [
            "Market_*_Prices.json",
            "TPEx_Market_*_Prices.json",
            "TPEx_Dividends_*.json",
            "ListingDates.json"
        ]
        
        files_to_upload = []
        for pattern in patterns:
            files_to_upload.extend(data_dir.glob(pattern))
            
        # Also include DuckDB Parquet schemas
        backup_dir = Path("data/backup")
        if backup_dir.exists():
            files_to_upload.extend(backup_dir.glob("*.parquet"))
        
        if not files_to_upload:
            return {"status": "error", "reason": "no_files_found"}
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            # Step 1: Get the current commit SHA of master branch
            ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/master"
            ref_resp = requests.get(ref_url, headers=headers)
            if ref_resp.status_code != 200:
                return {"status": "error", "reason": f"Failed to get ref: {ref_resp.text}"}
            
            current_commit_sha = ref_resp.json()["object"]["sha"]
            
            # Step 2: Get the tree SHA of the current commit
            commit_url = f"https://api.github.com/repos/{repo}/git/commits/{current_commit_sha}"
            commit_resp = requests.get(commit_url, headers=headers)
            base_tree_sha = commit_resp.json()["tree"]["sha"]
            
            # Step 3: Create blobs for each file and build tree entries
            tree_entries = []
            for file_path in files_to_upload:
                with open(file_path, "rb") as f:
                    content = f.read()
                
                # Create blob
                blob_url = f"https://api.github.com/repos/{repo}/git/blobs"
                blob_resp = requests.post(blob_url, headers=headers, json={
                    "content": base64.b64encode(content).decode("utf-8"),
                    "encoding": "base64"
                })
                
                if blob_resp.status_code != 201:
                    logger.error(f"Failed to create blob for {file_path.name}")
                    continue
                
                blob_sha = blob_resp.json()["sha"]
                tree_entries.append({
                    "path": str(file_path),
                    "mode": "100644",  # Regular file
                    "type": "blob",
                    "sha": blob_sha
                })
            
            if not tree_entries:
                return {"status": "error", "reason": "no_blobs_created"}
            
            # Step 4: Create new tree
            tree_url = f"https://api.github.com/repos/{repo}/git/trees"
            tree_resp = requests.post(tree_url, headers=headers, json={
                "base_tree": base_tree_sha,
                "tree": tree_entries
            })
            
            if tree_resp.status_code != 201:
                return {"status": "error", "reason": f"Failed to create tree: {tree_resp.text}"}
            
            new_tree_sha = tree_resp.json()["sha"]
            
            # Step 5: Create commit with all files
            commit_create_url = f"https://api.github.com/repos/{repo}/git/commits"
            commit_msg = f"Pre-warm: {len(tree_entries)} cache files @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            commit_create_resp = requests.post(commit_create_url, headers=headers, json={
                "message": commit_msg,
                "tree": new_tree_sha,
                "parents": [current_commit_sha]
            })
            
            if commit_create_resp.status_code != 201:
                return {"status": "error", "reason": f"Failed to create commit: {commit_create_resp.text}"}
            
            new_commit_sha = commit_create_resp.json()["sha"]
            
            # Step 6: Update ref to point to new commit
            update_ref_resp = requests.patch(ref_url, headers=headers, json={
                "sha": new_commit_sha
            })
            
            if update_ref_resp.status_code != 200:
                return {"status": "error", "reason": f"Failed to update ref: {update_ref_resp.text}"}
            
            logger.info(f"[PreWarm] Single commit created: {new_commit_sha[:7]} ({len(tree_entries)} files)")
            
            return {
                "status": "success",
                "uploaded": len(tree_entries),
                "commit_sha": new_commit_sha[:7],
                "message": commit_msg,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"[PreWarm] Failed: {e}")
            return {"status": "error", "reason": str(e)}

    @staticmethod
    def backup_dividend_cache():
        """
        Backup dividend cache files (app/data/dividends/*.json) to GitHub repository.
        Called by Admin "Sync All Dividends" to persist cache across deploys.
        Uses Git Trees API to create a SINGLE commit for all files.
        """
        from pathlib import Path
        
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        
        if not token or not repo:
            logger.warning("[DividendBackup] GITHUB_TOKEN or GITHUB_REPO not set.")
            return {"status": "skipped", "reason": "missing_env_vars"}
        
        # Target directory for dividend cache
        data_dir = Path(__file__).parent.parent / "data" / "dividends"
        if not data_dir.exists():
            return {"status": "error", "reason": "app/data/dividends not found"}
        
        # Get all JSON files
        files_to_upload = list(data_dir.glob("*.json"))
        
        if not files_to_upload:
            return {"status": "error", "reason": "no_dividend_cache_files"}
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            # Step 1: Get the current commit SHA of master branch
            ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/master"
            ref_resp = requests.get(ref_url, headers=headers)
            if ref_resp.status_code != 200:
                return {"status": "error", "reason": f"Failed to get ref: {ref_resp.text}"}
            
            current_commit_sha = ref_resp.json()["object"]["sha"]
            
            # Step 2: Get the tree SHA of the current commit
            commit_url = f"https://api.github.com/repos/{repo}/git/commits/{current_commit_sha}"
            commit_resp = requests.get(commit_url, headers=headers)
            base_tree_sha = commit_resp.json()["tree"]["sha"]
            
            # Step 3: Create blobs for each file and build tree entries
            tree_entries = []
            for file_path in files_to_upload:
                with open(file_path, "rb") as f:
                    content = f.read()
                
                # Create blob
                blob_url = f"https://api.github.com/repos/{repo}/git/blobs"
                blob_resp = requests.post(blob_url, headers=headers, json={
                    "content": base64.b64encode(content).decode("utf-8"),
                    "encoding": "base64"
                })
                
                if blob_resp.status_code != 201:
                    logger.error(f"[DividendBackup] Failed to create blob for {file_path.name}")
                    continue
                
                blob_sha = blob_resp.json()["sha"]
                tree_entries.append({
                    "path": f"app/data/dividends/{file_path.name}",
                    "mode": "100644",  # Regular file
                    "type": "blob",
                    "sha": blob_sha
                })
            
            if not tree_entries:
                return {"status": "error", "reason": "no_blobs_created"}
            
            # Step 4: Create new tree
            tree_url = f"https://api.github.com/repos/{repo}/git/trees"
            tree_resp = requests.post(tree_url, headers=headers, json={
                "base_tree": base_tree_sha,
                "tree": tree_entries
            })
            
            if tree_resp.status_code != 201:
                return {"status": "error", "reason": f"Failed to create tree: {tree_resp.text}"}
            
            new_tree_sha = tree_resp.json()["sha"]
            
            # Step 5: Create commit with all files
            commit_create_url = f"https://api.github.com/repos/{repo}/git/commits"
            commit_msg = f"Dividend cache: {len(tree_entries)} stocks @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            commit_create_resp = requests.post(commit_create_url, headers=headers, json={
                "message": commit_msg,
                "tree": new_tree_sha,
                "parents": [current_commit_sha]
            })
            
            if commit_create_resp.status_code != 201:
                return {"status": "error", "reason": f"Failed to create commit: {commit_create_resp.text}"}
            
            new_commit_sha = commit_create_resp.json()["sha"]
            
            # Step 6: Update ref to point to new commit
            update_ref_resp = requests.patch(ref_url, headers=headers, json={
                "sha": new_commit_sha
            })
            
            if update_ref_resp.status_code != 200:
                return {"status": "error", "reason": f"Failed to update ref: {update_ref_resp.text}"}
            
            logger.info(f"[DividendBackup] Commit created: {new_commit_sha[:7]} ({len(tree_entries)} files)")
            
            return {
                "status": "success",
                "uploaded": len(tree_entries),
                "commit_sha": new_commit_sha[:7],
                "message": commit_msg,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"[DividendBackup] Failed: {e}")
            return {"status": "error", "reason": str(e)}


    @staticmethod
    async def run_quarterly_dividend_sync():
        """
        Quarterly scheduled job: Sync ALL dividend data for all stocks in the universe, then backup to GitHub.
        Scheduled for Jan/Apr/Jul/Oct 1st at 03:00 UTC.
        """
        from app import dividend_cache
        import pandas as pd
        from pathlib import Path
        
        logger.info("[Quarterly Sync] Starting Global Dividend Sync (Universe)...")
        
        try:
            # 1. Load All Stocks (Universe)
            stock_list_path = Path("app/project_tw/stock_list.csv")
            if stock_list_path.exists():
                df_stocks = pd.read_csv(stock_list_path)
                stock_ids = df_stocks['code'].astype(str).tolist()
                logger.info(f"[Quarterly Sync] Loaded {len(stock_ids)} symbols from stock_list.csv")
            else:
                # Fallback to user targets if file missing
                with get_db() as conn:
                    stock_ids = target_repo.get_all_unique_stock_ids(conn)
                logger.warning("[Quarterly Sync] stock_list.csv missing. Falling back to active targets.")
                
            if not stock_ids:
                logger.info("[Quarterly Sync] No stocks to sync.")
                return {"status": "skipped", "message": "No stocks found"}
            
            # 2. Sync All (Updates DB + files)
            # This operations updates the local JSON files in data/raw/TWSE_Dividends_*.json
            result = dividend_cache.sync_all_caches(stock_ids)
            logger.info(f"[Quarterly Sync] Local Sync Result: {result}")
            
            # 3. Backup to GitHub
            backup_result = BackupService.refresh_prewarm_data()
            
            logger.info(f"[Quarterly Sync] Complete. Backup Status: {backup_result.get('status')}")
            return {
                "status": "success",
                "sync_result": result,
                "backup_result": backup_result
            }
            
        except Exception as e:
            logger.exception(f"[Quarterly Sync] Failed: {e}")
            return {"status": "error", "reason": str(e)}
