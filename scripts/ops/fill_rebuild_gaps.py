"""
Phase 14: Gap-Fill Script — Ensure Zero Missing Trading Days

After rebuild_market_db.py completes, this script identifies and re-fetches
any trading days that were skipped due to transient network errors.

Strategy:
  1. Query DuckDB for all distinct dates in daily_prices.
  2. Generate the expected set of TWSE weekdays from 2004-01-01 to today.
  3. For each missing weekday, attempt to fetch from TWSE MI_INDEX.
     - If TWSE returns data → insert into DuckDB.
     - If TWSE says "no data" (holiday) → skip (not a gap).
  4. Report final count of filled gaps and remaining failures.

Usage:
    uv run python scripts/ops/fill_rebuild_gaps.py [--start-year 2004]
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.getcwd())
from app.services.market_db import get_connection
from scripts.ops.fetch_mi_index_mass import MIIndexMassFetcher

logger = logging.getLogger(__name__)


def get_existing_dates() -> set:
    """Get all distinct dates from DuckDB daily_prices."""
    conn = get_connection(read_only=True)
    try:
        rows = conn.execute(
            "SELECT DISTINCT date FROM daily_prices ORDER BY date"
        ).fetchall()
        return {str(r[0]) for r in rows}
    finally:
        conn.close()


def generate_weekdays(start_year: int = 2004) -> list:
    """Generate all weekdays from start_year-01-01 to today."""
    start = datetime(start_year, 1, 1)
    end = datetime.now()
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon-Fri
            days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return days


# Known TWSE holidays (national holidays, typhoon days, etc.)
# This is a minimal set; the script handles unknown holidays gracefully
# by checking if TWSE returns "no data" for a date.
KNOWN_HOLIDAYS = {
    # Add specific known holidays here if needed
    # Format: "YYYY-MM-DD"
}


async def fill_gaps(start_year: int = 2004, max_retries_per_date: int = 3):
    """Find and fill missing trading days."""
    print("📊 Step 1: Querying existing dates from DuckDB...")
    existing = get_existing_dates()
    print(f"   Found {len(existing)} distinct dates in daily_prices.")

    print(f"\n📅 Step 2: Generating expected weekdays from {start_year}...")
    all_weekdays = generate_weekdays(start_year)
    print(f"   Generated {len(all_weekdays)} weekdays.")

    # Find gaps (weekdays not in DB and not known holidays)
    missing = [d for d in all_weekdays if d not in existing and d not in KNOWN_HOLIDAYS]
    print(f"\n🔍 Step 3: Found {len(missing)} candidate missing dates.")

    if not missing:
        print("✅ No gaps found! Database is complete.")
        return

    # Try to fetch each missing date
    fetcher = MIIndexMassFetcher()
    filled = 0
    holidays_found = 0
    persistent_failures = []

    import httpx
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    async with httpx.AsyncClient(headers=headers) as client:
        for i, date_iso in enumerate(missing):
            date_str = date_iso.replace("-", "")  # YYYY-MM-DD -> YYYYMMDD
            pct = round((i + 1) / len(missing) * 100, 1)

            # Check cache first
            cache_file = fetcher.cache_dir / f"MI_INDEX_{date_str}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, "r") as f:
                        cached = json.load(f)
                    if cached.get("stat") == "OK":
                        # Cache hit — parse and insert
                        batch = fetcher.parse_mi_index(cached, date_str)
                        if batch:
                            written = fetcher.flush_to_db(batch)
                            if written > 0:
                                filled += 1
                                print(f"  ✅ [{pct}%] {date_iso}: {written} stocks (from cache)")
                            continue
                    elif cached.get("stat") == "EMPTY":
                        holidays_found += 1
                        continue
                except (json.JSONDecodeError, OSError):
                    pass

            # Fetch from network
            data = await fetcher.fetch_date(client, date_str)

            if data and data.get("stat") == "OK":
                batch = fetcher.parse_mi_index(data, date_str)
                if batch:
                    written = fetcher.flush_to_db(batch)
                    if written > 0:
                        filled += 1
                        print(f"  ✅ [{pct}%] {date_iso}: {written} stocks (fetched)")
                    else:
                        persistent_failures.append(date_iso)
                else:
                    holidays_found += 1
            elif data and data.get("stat") == "EMPTY":
                holidays_found += 1
            else:
                persistent_failures.append(date_iso)
                print(f"  ❌ [{pct}%] {date_iso}: Failed to fetch")

    # Final Report
    print(f"\n{'=' * 60}")
    print("🏁 Gap-Fill Complete!")
    print(f"   🔍 Candidate Missing Dates: {len(missing)}")
    print(f"   ✅ Filled:                   {filled}")
    print(f"   📅 Holidays (not real gaps): {holidays_found}")
    print(f"   ❌ Persistent Failures:      {len(persistent_failures)}")

    if persistent_failures:
        print(f"\n   ⚠️ The following dates could NOT be filled:")
        for d in persistent_failures[:20]:
            print(f"      - {d}")
        if len(persistent_failures) > 20:
            print(f"      ... and {len(persistent_failures) - 20} more")

    # Verify final count
    final_count = len(get_existing_dates())
    print(f"\n   📊 Final DB date count: {final_count}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    start_yr = 2004
    if len(sys.argv) > 1 and sys.argv[1] == "--start-year" and len(sys.argv) > 2:
        start_yr = int(sys.argv[2])

    asyncio.run(fill_gaps(start_year=start_yr))
