"""
Phase 14: Rebuild Market DB (Nominal Foundation)

Orchestrator script that wipes adjusted data from daily_prices
and rehydrates from MI_INDEX (Nominal source).

Checkpoint/Resume Logic:
  - Each DB flush saves a checkpoint to `data/raw/mi_index/_checkpoint.json`
  - On crash/restart, `--resume` auto-skips already-flushed dates
  - The per-day JSON cache in `data/raw/mi_index/` also avoids re-fetching

Usage:
    # Preview what will happen (no destructive writes)
    uv run python scripts/ops/rebuild_market_db.py --preview

    # Full rebuild (wipe + restore from scratch)
    uv run python scripts/ops/rebuild_market_db.py --confirm

    # Resume after crash/interruption (auto-detects checkpoint)
    uv run python scripts/ops/rebuild_market_db.py --resume

    # Upsert only (no wipe, overlay nominal data on existing)
    uv run python scripts/ops/rebuild_market_db.py --upsert-only
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.getcwd())
from app.services.market_db import get_connection, DB_PATH
from scripts.ops.fetch_mi_index_mass import MIIndexMassFetcher

logger = logging.getLogger(__name__)


def get_db_stats() -> dict:
    """Get current DuckDB statistics."""
    conn = get_connection(read_only=True)
    try:
        row_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
        stock_count = conn.execute(
            "SELECT COUNT(DISTINCT stock_id) FROM daily_prices"
        ).fetchone()[0]
        date_range = conn.execute(
            "SELECT MIN(date), MAX(date) FROM daily_prices"
        ).fetchone()
        market_breakdown = conn.execute(
            "SELECT market, COUNT(*) FROM daily_prices GROUP BY market"
        ).fetchall()

        return {
            "total_rows": row_count,
            "unique_stocks": stock_count,
            "date_min": str(date_range[0]) if date_range[0] else "N/A",
            "date_max": str(date_range[1]) if date_range[1] else "N/A",
            "market_breakdown": {m: c for m, c in market_breakdown},
            "db_size_mb": round(DB_PATH.stat().st_size / (1024 * 1024), 2)
            if DB_PATH.exists()
            else 0,
        }
    finally:
        conn.close()


def wipe_daily_prices():
    """Delete all rows from daily_prices table."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM daily_prices")
        conn.execute("CHECKPOINT")
        logger.info("🗑️ Wiped all daily_prices data.")
    finally:
        conn.close()


def preview():
    """Show current DB state without making changes."""
    stats = get_db_stats()
    print("\n📊 Current DuckDB State:")
    print(f"   DB Path:      {DB_PATH}")
    print(f"   DB Size:      {stats['db_size_mb']} MB")
    print(f"   Total Rows:   {stats['total_rows']:,}")
    print(f"   Unique Stocks: {stats['unique_stocks']}")
    print(f"   Date Range:   {stats['date_min']} → {stats['date_max']}")
    print(f"   Market Tags:  {stats['market_breakdown']}")
    print()
    print("⚠️ A full rebuild will:")
    print("   1. DELETE all rows from daily_prices")
    print("   2. Re-fetch 2004-2025 from TWSE MI_INDEX (NOMINAL)")
    print("   3. Insert ~5-7M rows of pure nominal data")
    print()
    print("Run with --confirm to proceed.")


async def rebuild(wipe: bool = True, start_year: int = 2004, resume: bool = False):
    """Full rebuild: wipe + restore, or resume from checkpoint."""
    stats_before = get_db_stats()
    print(f"\n📊 Before: {stats_before['total_rows']:,} rows")

    fetcher = MIIndexMassFetcher()

    if wipe and not resume:
        print("\n🗑️ Wiping daily_prices...")
        wipe_daily_prices()
        fetcher.clear_checkpoint()

    print(f"\n🚀 Starting MI_INDEX restoration from {start_year}...")
    end_date = datetime.now().strftime("%Y%m%d")
    await fetcher.run_restoration(
        f"{start_year}0101", end_date, resume=resume
    )

    stats_after = get_db_stats()
    print(f"\n📊 After: {stats_after['total_rows']:,} rows")
    print(f"   Unique Stocks: {stats_after['unique_stocks']}")
    print(f"   Date Range:   {stats_after['date_min']} → {stats_after['date_max']}")


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild market.duckdb with Nominal data from TWSE MI_INDEX"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--preview", action="store_true", help="Show current DB state (no changes)"
    )
    group.add_argument(
        "--confirm",
        action="store_true",
        help="Full rebuild: wipe daily_prices + restore from MI_INDEX",
    )
    group.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previous --confirm run from the last checkpoint",
    )
    group.add_argument(
        "--upsert-only",
        action="store_true",
        help="Restore without wiping (upsert over existing data)",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2004,
        help="Start year for restoration (default: 2004)",
    )

    args = parser.parse_args()

    if args.preview:
        preview()
    elif args.confirm:
        asyncio.run(rebuild(wipe=True, start_year=args.start_year))
    elif args.resume:
        asyncio.run(rebuild(wipe=False, start_year=args.start_year, resume=True))
    elif args.upsert_only:
        asyncio.run(rebuild(wipe=False, start_year=args.start_year))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    main()
