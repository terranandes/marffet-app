import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import sys
import os

# Ensure the project root is in sys.path so tests can import project_tw
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
