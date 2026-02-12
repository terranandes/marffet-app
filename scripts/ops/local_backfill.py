import sys
from pathlib import Path
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.market_data_service import backfill_all_stocks

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Local Universe Backfill (Fast Mode)")
    parser.add_argument("--deep", action="store_true", help="Include Deep Universe (warrants)")
    args = parser.parse_args()

    print(f"🚀 Starting Local Universe Backfill (Fast Mode, Deep={args.deep})...")
    
    # Adaptive Flow in market_data_service will detect local env and use high speed.
    # We pass args.deep if provided, otherwise default locally is True.
    result = backfill_all_stocks(period="max", overwrite=False, include_warrants=args.deep if args.deep else None)
    
    if result["status"] == "ok":
        print(f"✅ Backfill Successful! Processed {result['stocks_processed']} stocks.")
    else:
        print(f"❌ Backfill Failed: {result['message']}")

if __name__ == "__main__":
    main()
