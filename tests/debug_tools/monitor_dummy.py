import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


async def monitor():
    # Tail the output if redirected?
    # But current process writes to stdout which I can't read directly unless I redirected it.
    # The 'run_command' output captures it.
    # I can't access it externally easily.
    pass
