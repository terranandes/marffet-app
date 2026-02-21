"""
Phase 14: MI_INDEX Mass Fetcher (Nominal Price Source)

Fetches daily OHLCV from TWSE MI_INDEX endpoint for the entire market.
Supports date-range restoration with:
  - WAF/rate-limit resilience (adaptive backoff)
  - Pre-2011 vs Post-2011 schema drift handling
  - Robust parsing (handles '--', empty strings, commas)
  - Periodic flush to DuckDB to keep memory low
  - File-level caching to allow resume after interruption
  - Checkpoint file for DB flush resume across restarts

Usage:
    # Full restore from 2004
    uv run python scripts/ops/fetch_mi_index_mass.py 20040101

    # Partial restore (single year)
    uv run python scripts/ops/fetch_mi_index_mass.py 20240101 20241231

    # Dry-run for a single month (no DB writes)
    uv run python scripts/ops/fetch_mi_index_mass.py 20240101 20240131 --dry-run

    # Resume from last checkpoint (auto-detected)
    uv run python scripts/ops/fetch_mi_index_mass.py 20040101 --resume
"""

import asyncio
import httpx
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

# Ensure we can import app modules
sys.path.insert(0, os.getcwd())
from app.services.market_db import get_connection

logger = logging.getLogger(__name__)

# ---------- Constants ----------

# TWSE MI_INDEX column schemas changed around 2011.
# Pre-2011: fewer columns, different ordering.
# Post-2011: standardized 9+ columns.
# We detect the schema by inspecting the 'fields' header row.

FIELD_MAPPING_POST_2011 = {
    "證券代號": "stock_id",
    "證券名稱": "name",
    "成交股數": "volume",
    "成交筆數": "trade_count",
    "成交金額": "amount",
    "開盤價": "open",
    "最高價": "high",
    "最低價": "low",
    "收盤價": "close",
}

# Pre-2011 may have the same Chinese keys but different column indices.
# We dynamically resolve by matching field names.

BATCH_FLUSH_SIZE = 10_000  # Flush to DB every N records
MAX_RETRIES = 5
BASE_DELAY_S = 3.5
RATE_LIMIT_SLEEP_S = 90.0
FORBIDDEN_SLEEP_S = 300.0
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0"
)


# ---------- Helpers ----------

def safe_parse_int(value: str) -> Optional[int]:
    """Parse a string to int, handling commas, '--', and empty strings."""
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip().replace(",", "")
    if cleaned in ("--", "-", "X", "", "N/A"):
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def safe_parse_float(value: str) -> Optional[float]:
    """Parse a string to float, handling commas, '--', '+', and empty strings."""
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip().replace(",", "").replace("+", "")
    if cleaned in ("--", "-", "X", "", "N/A"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_valid_ticker(sid: str) -> bool:
    """
    Filter to standard TWSE tickers:
    - 4-digit numeric (e.g. 2330)
    - 5-6 char numeric (e.g. 00937B, 006208)
    - ends with 'KY' (e.g. 1258KY for KY stocks listed on TWSE)
    """
    if not sid:
        return False
    sid = sid.strip()
    # Standard 4-digit tickers
    if len(sid) == 4 and sid.isdigit():
        return True
    # ETFs like 0050, 006208, 00937B
    if 4 <= len(sid) <= 6 and (sid.isdigit() or sid[:-1].isdigit()):
        return True
    # KY or foreign listings
    if sid.endswith("KY") and len(sid) <= 8:
        return True
    return False


# ---------- Core Fetcher ----------

class MIIndexMassFetcher:
    """Fetches and parses TWSE MI_INDEX data into DuckDB."""

    CHECKPOINT_FILE = "data/raw/mi_index/_checkpoint.json"

    def __init__(self, cache_dir: str = "data/raw/mi_index"):
        self.base_url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(1)

        # Stats
        self.total_records_inserted = 0
        self.total_days_processed = 0
        self.total_days_skipped = 0
        self.errors: List[str] = []

    # ---------- Checkpoint ----------

    def _load_checkpoint(self) -> Optional[str]:
        """Load last successfully flushed date from checkpoint file."""
        cp_path = Path(self.CHECKPOINT_FILE)
        if cp_path.exists():
            try:
                with open(cp_path, "r") as f:
                    cp = json.load(f)
                return cp.get("last_flushed_date")
            except (json.JSONDecodeError, OSError):
                pass
        return None

    def _save_checkpoint(self, last_date: str, records_so_far: int):
        """Save checkpoint after a successful DB flush."""
        cp_path = Path(self.CHECKPOINT_FILE)
        cp_data = {
            "last_flushed_date": last_date,
            "total_records_flushed": records_so_far,
            "updated_at": datetime.now().isoformat(),
        }
        with open(cp_path, "w") as f:
            json.dump(cp_data, f, indent=2)

    def clear_checkpoint(self):
        """Remove checkpoint file (called before a fresh start)."""
        cp_path = Path(self.CHECKPOINT_FILE)
        if cp_path.exists():
            cp_path.unlink()
            logger.info("🧹 Cleared checkpoint file.")

    # ---------- Network ----------

    async def fetch_date(
        self, client: httpx.AsyncClient, date_str: str
    ) -> Optional[dict]:
        """
        Fetch MI_INDEX JSON for a single date (YYYYMMDD).
        Returns parsed JSON or None on failure.
        Uses file-level caching to support resume.
        """
        cache_file = self.cache_dir / f"MI_INDEX_{date_str}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("stat") == "OK":
                    return data
                # Cached but empty/holiday — return as-is to skip silently
                return data
            except (json.JSONDecodeError, OSError):
                pass  # Re-fetch on corrupt cache

        params = {"response": "json", "date": date_str, "type": "ALLBUT0999"}

        async with self.semaphore:
            for attempt in range(MAX_RETRIES):
                try:
                    delay = BASE_DELAY_S + (attempt * 8.0)
                    await asyncio.sleep(delay)

                    resp = await client.get(
                        self.base_url, params=params, timeout=30.0
                    )

                    if resp.status_code == 200:
                        data = resp.json()

                        if data and data.get("stat") == "OK":
                            # Cache successful response
                            with open(cache_file, "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False)
                            return data

                        if "查詢頻率過高" in str(data):
                            logger.warning(
                                "🛑 Rate limited at %s (attempt %d). Sleeping %ds...",
                                date_str, attempt + 1, RATE_LIMIT_SLEEP_S,
                            )
                            await asyncio.sleep(RATE_LIMIT_SLEEP_S)
                            continue

                        # Likely weekend/holiday — cache empty response
                        empty = {"stat": "EMPTY", "date": date_str}
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(empty, f)
                        return empty

                    if resp.status_code == 403:
                        logger.warning(
                            "🚫 403 at %s (attempt %d). Sleeping %ds...",
                            date_str, attempt + 1, FORBIDDEN_SLEEP_S,
                        )
                        await asyncio.sleep(FORBIDDEN_SLEEP_S)
                        continue

                    logger.warning(
                        "⚠️ HTTP %d for %s", resp.status_code, date_str
                    )

                except httpx.TimeoutException:
                    logger.warning("⏱️ Timeout for %s (attempt %d)", date_str, attempt + 1)
                except Exception as e:
                    logger.error("❌ Error for %s: %s", date_str, e)

        self.errors.append(f"Failed after {MAX_RETRIES} retries: {date_str}")
        return None

    # ---------- Parsing ----------

    def _resolve_field_indices(self, fields: List[str]) -> dict:
        """
        Dynamically resolve column indices from header fields.
        Handles schema drift between pre/post-2011.
        Returns mapping: logical_name -> column_index.
        """
        idx_map = {}
        for i, field in enumerate(fields):
            field_clean = field.strip()
            if field_clean in FIELD_MAPPING_POST_2011:
                idx_map[FIELD_MAPPING_POST_2011[field_clean]] = i
        return idx_map

    def parse_mi_index(
        self, data: dict, date_str: str
    ) -> List[Tuple[str, str, float, float, float, float, int, str]]:
        """
        Parse MI_INDEX response into DuckDB-ready tuples.
        Returns list of (stock_id, date, open, high, low, close, volume, market).
        """
        if not data or data.get("stat") != "OK":
            return []

        # Find the correct table (the one with '證券代號' in fields)
        quotes_table = None
        for t in data.get("tables", []):
            fields = t.get("fields", [])
            if "證券代號" in fields:
                quotes_table = t
                break

        if not quotes_table:
            return []

        fields = quotes_table.get("fields", [])
        idx = self._resolve_field_indices(fields)

        # Minimum required fields
        required = {"stock_id", "open", "high", "low", "close"}
        if not required.issubset(idx.keys()):
            logger.warning(
                "⚠️ Schema mismatch for %s. Fields: %s, Resolved: %s",
                date_str, fields, idx,
            )
            return []

        # Format date: YYYYMMDD -> YYYY-MM-DD
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        batch = []
        for row in quotes_table.get("data", []):
            try:
                sid = row[idx["stock_id"]].strip()
                if not is_valid_ticker(sid):
                    continue

                op = safe_parse_float(row[idx["open"]])
                hi = safe_parse_float(row[idx["high"]])
                lo = safe_parse_float(row[idx["low"]])
                cl = safe_parse_float(row[idx["close"]])

                # Skip rows with missing prices (halted stocks, etc.)
                if op is None or hi is None or lo is None or cl is None:
                    continue
                if cl <= 0:
                    continue

                vol_idx = idx.get("volume")
                vol = safe_parse_int(row[vol_idx]) if vol_idx is not None else 0
                if vol is None:
                    vol = 0

                batch.append((sid, iso_date, op, hi, lo, cl, vol, "TWSE"))

            except (IndexError, TypeError) as e:
                # Log but don't crash — some rows may have unexpected format
                logger.debug("  Skipped row in %s: %s", date_str, e)
                continue

        return batch

    # ---------- DB Operations ----------

    def flush_to_db(self, batch: List[tuple], last_date_in_batch: str = "") -> int:
        """
        Upsert batch into DuckDB daily_prices.
        Saves a checkpoint after successful flush.
        Returns number of records written.
        """
        if not batch:
            return 0

        logger.info("📥 Flushing %d records to DuckDB...", len(batch))
        conn = get_connection()
        try:
            # Create temp table matching daily_prices schema
            conn.execute(
                "CREATE TEMP TABLE IF NOT EXISTS _tmp_nominal "
                "AS SELECT * FROM daily_prices LIMIT 0"
            )
            conn.executemany(
                "INSERT INTO _tmp_nominal "
                "(stock_id, date, open, high, low, close, volume, market) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                batch,
            )

            # Raw Insert Without ON CONFLICT because DB is clean and indexes are dropped for speed
            conn.execute("""
                INSERT INTO daily_prices
                SELECT * FROM _tmp_nominal
            """)
            conn.execute("DROP TABLE IF EXISTS _tmp_nominal")
            logger.info("  💾 Flushed %d records.", len(batch))

            # Save checkpoint after successful commit
            if last_date_in_batch:
                self._save_checkpoint(
                    last_date_in_batch, self.total_records_inserted + len(batch)
                )

            return len(batch)

        except Exception as e:
            logger.error("  ❌ DB flush error: %s", e)
            self.errors.append(f"DB flush error: {e}")
            return 0
        finally:
            conn.close()

    # ---------- Orchestration ----------

    async def run_restoration(
        self,
        start_date_str: str = "20040101",
        end_date_str: Optional[str] = None,
        dry_run: bool = False,
        resume: bool = False,
    ):
        """
        Main entry point: fetch and ingest MI_INDEX data for a date range.
        If resume=True, auto-skips dates before the last checkpoint.
        """
        if not end_date_str:
            end_date_str = datetime.now().strftime("%Y%m%d")

        start_dt = datetime.strptime(start_date_str, "%Y%m%d")
        end_dt = datetime.strptime(end_date_str, "%Y%m%d")

        # Resume support: skip past the checkpoint
        if resume and not dry_run:
            last_flushed = self._load_checkpoint()
            if last_flushed:
                # Resume from the day AFTER the last flushed date
                resume_dt = datetime.strptime(
                    last_flushed.replace("-", ""), "%Y%m%d"
                ) + timedelta(days=1)
                if resume_dt > start_dt:
                    print(
                        f"♻️ Resuming from checkpoint: {last_flushed} "
                        f"(skipping {(resume_dt - start_dt).days} days)",
                        flush=True,
                    )
                    start_dt = resume_dt

        total_days = (end_dt - start_dt).days + 1
        mode_label = "DRY RUN" if dry_run else ("RESUME" if resume else "LIVE")

        print(
            f"🚀 [{mode_label}] Mass Restoring Nominal Prices: "
            f"{start_dt.strftime('%Y%m%d')} → {end_date_str} ({total_days} days)",
            flush=True,
        )

        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient(headers=headers) as client:
            current_dt = start_dt
            cumulative_batch = []
            day_count = 0

            while current_dt <= end_dt:
                ds = current_dt.strftime("%Y%m%d")
                day_count += 1

                # Skip weekends (Sat=5, Sun=6)
                if current_dt.weekday() >= 5:
                    current_dt += timedelta(days=1)
                    self.total_days_skipped += 1
                    continue

                data = await self.fetch_date(client, ds)

                if data and data.get("stat") == "OK":
                    batch = self.parse_mi_index(data, ds)
                    cumulative_batch.extend(batch)
                    last_ok_date = ds  # Track for checkpoint
                    self.total_days_processed += 1

                    if day_count % 20 == 0 or len(batch) > 0:
                        pct = round(day_count / total_days * 100, 1)
                        print(
                            f"  ✅ {ds}: {len(batch)} stocks "
                            f"({pct}% | {day_count}/{total_days})",
                            flush=True,
                        )
                else:
                    self.total_days_skipped += 1

                # Periodic flush with checkpoint
                if len(cumulative_batch) >= BATCH_FLUSH_SIZE and not dry_run:
                    iso_last = f"{last_ok_date[:4]}-{last_ok_date[4:6]}-{last_ok_date[6:8]}"
                    written = self.flush_to_db(cumulative_batch, last_date_in_batch=iso_last)
                    self.total_records_inserted += written
                    cumulative_batch = []

                current_dt += timedelta(days=1)

            # Final flush
            if cumulative_batch and not dry_run:
                iso_last = f"{last_ok_date[:4]}-{last_ok_date[4:6]}-{last_ok_date[6:8]}" if 'last_ok_date' in dir() else ""
                written = self.flush_to_db(cumulative_batch, last_date_in_batch=iso_last)
                self.total_records_inserted += written

            if dry_run and cumulative_batch:
                print(
                    f"\n📋 [DRY RUN] Would insert {len(cumulative_batch)} records.",
                    flush=True,
                )
                # Show sample
                for rec in cumulative_batch[:5]:
                    print(f"   {rec}", flush=True)

        self._print_summary()

    def _print_summary(self):
        """Print final statistics."""
        print("\n" + "=" * 60, flush=True)
        print("🏁 Mass Restoration Complete", flush=True)
        print(f"   📊 Days Processed:  {self.total_days_processed}", flush=True)
        print(f"   ⏭️  Days Skipped:    {self.total_days_skipped}", flush=True)
        print(f"   💾 Records Written:  {self.total_records_inserted}", flush=True)
        if self.errors:
            print(f"   ❌ Errors ({len(self.errors)}):", flush=True)
            for e in self.errors[:10]:
                print(f"      - {e}", flush=True)
        print("=" * 60, flush=True)


# ---------- CLI ----------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    start_date = sys.argv[1] if len(sys.argv) > 1 else "20040101"
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    dry_run = "--dry-run" in sys.argv
    resume = "--resume" in sys.argv

    fetcher = MIIndexMassFetcher()
    asyncio.run(
        fetcher.run_restoration(start_date, end_date, dry_run=dry_run, resume=resume)
    )
