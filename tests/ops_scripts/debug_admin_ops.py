import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import asyncio
import sys
import os
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Mock Environment
os.environ["GITHUB_TOKEN"] = "mock_token"
os.environ["GITHUB_REPO"] = "mock_repo"

async def monitor_status():
    from app.services.crawler_service import CrawlerService
    print("[Monitor] Starting poll loop...")
    for _ in range(20):
        status = CrawlerService.get_status()
        print(f"[Monitor] Status: {status['status']} | Msg: {status['message']} | Running: {status['is_running']}")
        if status['status'] in ['success', 'error']:
            break
        await asyncio.sleep(1)

async def main():
    print("--- Debugging Admin Ops ---")
    
    from app.services.backup import BackupService
    from app.services.crawler_service import CrawlerService
    
    # 1. Check Initial Status
    print(f"Initial: {CrawlerService.get_status()}")
    
    # 2. Trigger Pre-warm (Mocking the background task)
    print("Triggering BackupService.annual_prewarm_with_rebuild()...")
    
    # Run in parallel
    task = asyncio.create_task(BackupService.annual_prewarm_with_rebuild())
    monitor = asyncio.create_task(monitor_status())
    
    await asyncio.gather(task, monitor)
    
    print(f"Final: {CrawlerService.get_status()}")

if __name__ == "__main__":
    asyncio.run(main())