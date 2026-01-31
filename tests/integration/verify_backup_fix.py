import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import sys
import os
import asyncio
from pathlib import Path

# Add project root to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

from app.services.backup import BackupService
import logging

# Configure logger to print to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.services.backup")
logger.setLevel(logging.INFO)

print("--- Starting Backup Verification ---")
print(f"GITHUB_REPO: {os.getenv('GITHUB_REPO')}")
# We don't print the token for security

print("Running check_and_backup_if_needed()...")
try:
    BackupService.check_and_backup_if_needed()
    print("--- Execution Complete ---")
except Exception as e:
    print(f"--- Execution Failed: {e} ---")
