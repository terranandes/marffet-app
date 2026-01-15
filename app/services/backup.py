
import os
import base64
import requests
import logging
from datetime import datetime
from app.portfolio_db import DB_PATH

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
        repo = os.getenv("GITHUB_REPO") # e.g. "terranandes/martian"
        
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
