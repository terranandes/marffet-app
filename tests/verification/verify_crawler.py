
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add app to path
sys.path.append(os.getcwd())

from app.services.crawler_service import CrawlerService

def test_crawler_status():
    print("Testing CrawlerService.get_status()...")
    status = CrawlerService.get_status()
    print(f"Status: {status}")
    
    # Verify Timezone in last_run_time if present
    if status.get("last_run_time"):
        print(f"Last Run Time: {status['last_run_time']}")
        if "+00:00" in status['last_run_time'] or "Z" in status['last_run_time']:
            print("✅ Timezone present (UTC)")
        else:
            print("❌ Timezone MISSING")
    
    # Verify new fields
    if "progress_pct" in status and "elapsed_seconds" in status:
        print(f"✅ Progress fields present: {status['progress_pct']}%, {status['elapsed_seconds']}s")
    else:
        print("❌ Progress fields MISSING")

if __name__ == "__main__":
    test_crawler_status()
