"""
Targeted Stock Data Patcher
Downloads specific stock(s) via yfinance and patches them into existing Market_YYYY_Prices.json files.
Much faster than re-crawling the entire universe.

Usage:
    uv run python scripts/ops/patch_stock_data.py --stocks 2330 2317 2454
    uv run python scripts/ops/patch_stock_data.py --stocks 2330 --start-year 2006 --end-year 2025
"""
import argparse
import json
import math
import logging
import time
from pathlib import Path
from typing import List, Dict

import pandas as pd

try:
    import yfinance as yf
except ImportError:
    raise ImportError("yfinance not installed. Run: uv pip install yfinance")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("PatchStock")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def _is_valid(v) -> bool:
    if v is None:
        return False
    if isinstance(v, float):
        return not (math.isnan(v) or math.isinf(v))
    return True


def download_stock(code: str, start_year: int, end_year: int) -> Dict[int, dict]:
    """Download a single stock from yfinance and organize by year."""
    # Determine suffix: 4-digit codes starting with 3,4,5,6,7,8 on TPEx are .TWO
    # But for simplicity, try .TW first (TWSE), fall back to .TWO
    ticker = f"{code}.TW"
    logger.info(f"📥 Downloading {ticker} ({start_year}-{end_year})...")

    df = yf.download(
        ticker,
        start=f"{start_year}-01-01",
        end=f"{end_year + 1}-01-01",
        auto_adjust=False,
        progress=False,
        threads=False
    )

    if df.empty:
        # Try TPEx
        ticker = f"{code}.TWO"
        logger.info(f"   Trying TPEx: {ticker}...")
        df = yf.download(
            ticker,
            start=f"{start_year}-01-01",
            end=f"{end_year + 1}-01-01",
            auto_adjust=False,
            progress=False,
            threads=False
        )

    if df.empty:
        logger.error(f"❌ No data found for {code}")
        return {}

    # Flatten MultiIndex columns (yfinance quirk for single ticker)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df['year'] = df.index.year
    yearly = {}

    for year, year_df in df.groupby('year'):
        year = int(year)
        daily = []

        for idx, row in year_df.iterrows():
            o = row.get('Open', row.get('open'))
            h = row.get('High', row.get('high'))
            l = row.get('Low', row.get('low'))
            c = row.get('Close', row.get('close'))
            v = row.get('Volume', row.get('volume'))

            if not all(_is_valid(x) for x in [o, h, l, c]):
                continue

            daily.append({
                "d": idx.strftime("%Y-%m-%d"),
                "o": round(float(o), 2),
                "h": round(float(h), 2),
                "l": round(float(l), 2),
                "c": round(float(c), 2),
                "v": int(v) if _is_valid(v) else 0
            })

        if not daily:
            continue

        opens = [d["o"] for d in daily]
        highs = [d["h"] for d in daily]
        lows = [d["l"] for d in daily]
        closes = [d["c"] for d in daily]
        volumes = [d["v"] for d in daily]

        summary = {
            "id": code,
            "name": code,
            "start": opens[0],
            "end": closes[-1],
            "high": max(highs),
            "low": min(lows),
            "volume": sum(volumes),
            "first_open": opens[0]
        }

        yearly[year] = {
            "id": code,
            "summary": summary,
            "daily": daily
        }

    logger.info(f"✅ {code}: Got {len(yearly)} years of data ({min(yearly.keys()) if yearly else '?'}-{max(yearly.keys()) if yearly else '?'})")
    return yearly


def patch_market_files(code: str, yearly_data: Dict[int, dict]):
    """Patch stock data into existing Market_YYYY_Prices.json files."""
    patched = 0

    for year, stock_data in sorted(yearly_data.items()):
        file_path = DATA_DIR / f"Market_{year}_Prices.json"

        # Load existing data or create empty
        existing = {}
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing = json.load(f)

        # Patch
        before = code in existing
        existing[code] = stock_data

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, separators=(',', ':'))

        status = "UPDATED" if before else "ADDED"
        daily_count = len(stock_data.get('daily', []))
        logger.info(f"   📁 {file_path.name}: {status} {code} ({daily_count} daily points, {len(existing)} total stocks)")
        patched += 1

    return patched


def main():
    parser = argparse.ArgumentParser(description="Patch specific stock data into Market JSON files")
    parser.add_argument("--stocks", nargs="+", required=True, help="Stock codes to patch (e.g., 2330 2317)")
    parser.add_argument("--start-year", type=int, default=2000, help="Start year (default: 2000)")
    parser.add_argument("--end-year", type=int, default=None, help="End year (default: current year)")
    args = parser.parse_args()

    end_year = args.end_year or pd.Timestamp.now().year

    logger.info("=" * 50)
    logger.info("🔧 TARGETED STOCK DATA PATCHER")
    logger.info(f"   Stocks: {', '.join(args.stocks)}")
    logger.info(f"   Range: {args.start_year}-{end_year}")
    logger.info("=" * 50)

    start_time = time.time()
    total_patched = 0

    for code in args.stocks:
        logger.info(f"\n{'='*40}")
        logger.info(f"📊 Processing {code}...")
        logger.info(f"{'='*40}")

        yearly_data = download_stock(code, args.start_year, end_year)
        if yearly_data:
            count = patch_market_files(code, yearly_data)
            total_patched += count
            logger.info(f"✅ {code}: Patched {count} year files")
        else:
            logger.error(f"❌ {code}: No data to patch")

        # Small delay between stocks
        time.sleep(1.0)

    elapsed = time.time() - start_time
    logger.info(f"\n{'='*50}")
    logger.info(f"✨ PATCH COMPLETE in {elapsed:.1f}s")
    logger.info(f"   Total year-files patched: {total_patched}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    main()
