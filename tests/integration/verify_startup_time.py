import time
import requests
import subprocess
import os
import signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_startup_time():
    """
    Verify startup time < 5 seconds.
    Task 10.4 in PRD.
    """
    logger.info("Starting server to measure startup time...")
    
    start = time.time()
    # Start the app using terminal
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "app.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
        preexec_fn=os.setsid
    )
    
    # Poll /api/health or / until it responds
    url = "http://localhost:8000/api/admin/market-data/stats" # New endpoint from Task 7
    success = False
    for i in range(30):
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                elapsed = time.time() - start
                logger.info(f"✅ Server started and responded in {elapsed:.2f}s")
                if elapsed < 5:
                    logger.info("✅ Startup time within criteria (< 5s).")
                else:
                    logger.warning("⚠️ Startup time exceeds 5s.")
                success = True
                break
        except:
            pass
        time.sleep(0.5)
        if i % 4 == 0:
            logger.info("  Waiting for server...")

    if not success:
        logger.error("❌ Server failed to start or respond within 15s.")

    # Cleanup
    logger.info("Stopping server...")
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    
if __name__ == "__main__":
    verify_startup_time()
