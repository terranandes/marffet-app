import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import asyncio
from project_tw.strategies.cb import CBStrategy

async def main():
    print("Initialize CB Strategy...")
    strategy = CBStrategy()
    
    # Target: 6533 (Andes)
    targets = ['6533']
    print(f"Analyzing: {targets}")
    
    results = await strategy.analyze_list(targets)
    
    print("\n=== Analysis Results ===")
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
