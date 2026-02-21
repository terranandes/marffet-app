"""
Phase 17-A: Grand Correlation Analysis
Compare our DuckDB-calculated Mars CAGR vs MoneyCome reference (s2006e2026bao).
Target: >85% match rate within ±1.5% CAGR tolerance.
"""

import os
import sys
import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Project root on sys.path ──────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.project_tw.calculator import ROICalculator

# ── Constants ─────────────────────────────────────────────────────────────────
DB_PATH      = ROOT / "data/market.duckdb"
REF_EXCEL    = ROOT / "app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx"
OUTPUT_CSV   = ROOT / "tests/analysis/correlation_report_full.csv"
START_YEAR   = 2006
MATCH_TIGHT  = 1.5   # ±1.5% → "Match"
MATCH_LOOSE  = 3.0   # ±3.0% → "Close"

def calculate_cagr(start_price, end_price, num_years):
    if start_price == 0 or num_years == 0:
        return 0.0
    return ((end_price / start_price) ** (1 / num_years) - 1) * 100.0

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_reference() -> pd.DataFrame:
    """Load MoneyCome reference Excel. Returns df with columns: code, name, ref_cagr."""
    print(f"Loading reference: {REF_EXCEL}")
    df = pd.read_excel(REF_EXCEL)
    df.columns = [str(c).strip() for c in df.columns]

    # Detect code / name / cagr columns (flexible naming)
    code_col = next((c for c in df.columns if c in ("代號", "id", "ID", "code", "Code")), df.columns[0])
    name_col = next((c for c in df.columns if c in ("名稱", "name", "Name")), None)
    cagr_col = next((c for c in df.columns if "s2006e2026bao" in c.lower() or c == "s2006e2026bao"), None)

    if cagr_col is None:
        # Print all columns so we can debug
        print(f"[WARN] Could not find s2006e2026bao column. Available: {df.columns.tolist()}")
        # Try to find any column that looks like a CAGR
        cagr_col = next((c for c in df.columns if "bao" in c.lower() and "2006" in c), None)
        if cagr_col is None:
            raise ValueError(f"Cannot find CAGR column in Excel. Columns: {df.columns.tolist()}")

    print(f"  → code_col={code_col!r}, name_col={name_col!r}, cagr_col={cagr_col!r}")

    out = pd.DataFrame()
    out["code"] = df[code_col].astype(str).str.strip().str.zfill(4)
    out["name"] = df[name_col].astype(str).str.strip() if name_col else ""
    out["ref_cagr"] = pd.to_numeric(df[cagr_col], errors="coerce")

    # Keep only valid 4-digit codes with a real CAGR
    out = out[out["code"].str.match(r"^\d{4}$") & out["ref_cagr"].notna()]
    print(f"  → {len(out)} valid reference stocks loaded.")
    return out.reset_index(drop=True)


def fetch_prices(con: duckdb.DuckDBPyConnection, stock_id: str) -> pd.DataFrame:
    """Fetch daily price data from DuckDB for a stock from START_YEAR onward."""
    df = con.execute("""
        SELECT date, YEAR(date) AS year, open, high, low, close, change
        FROM daily_prices
        WHERE stock_id = ?
          AND YEAR(date) >= ?
        ORDER BY date ASC
    """, [stock_id, START_YEAR]).df()

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    return df


def fetch_dividends(con: duckdb.DuckDBPyConnection, stock_id: str) -> dict:
    """Fetch dividends from DuckDB. Returns {year: {cash, stock}}."""
    rows = con.execute("""
        SELECT year, cash, stock
        FROM dividends
        WHERE stock_id = ?
          AND year >= ?
    """, [stock_id, START_YEAR]).fetchall()

    return {int(r[0]): {"cash": float(r[1] or 0), "stock": float(r[2] or 0)} for r in rows}


def calc_mars_cagr(con: duckdb.DuckDBPyConnection, stock_id: str, ref_yrs_count: float) -> tuple[float, str, pd.DataFrame]:
    """
    Run ROICalculator.calculate_complex_simulation for a stock.
    Returns (cagr_pct, note, df_prices).
    """
    df = fetch_prices(con, stock_id)
    if df.empty:
        return 0.0, "No Data", df

    # Need at least 2 years of data
    years_available = df["year"].nunique()
    if years_available < 2:
        return 0.0, f"Insufficient Data ({years_available} yr)", df

    # Exclude 興櫃 (Emerging Market) gaps by checking length disparity
    if ref_yrs_count > years_available + 1.5:
        return 0.0, "Emerging Market (興櫃)", df

    div_dict = fetch_dividends(con, stock_id)

    calc = ROICalculator()
    result = calc.calculate_complex_simulation(
        df=df,
        start_year=START_YEAR,
        principal=1_000_000,
        annual_investment=60_000,
        dividend_data=div_dict,
        stock_code=stock_id,
        buy_logic="FIRST_CLOSE",
    )

    if not result:
        return 0.0, "Calc Failed", df

    # Find the latest available year's CAGR key (s2006eYYYYbao)
    cagr_keys = sorted([k for k in result if k.startswith(f"s{START_YEAR}e") and k.endswith("bao")])
    if not cagr_keys:
        return 0.0, "No CAGR Key", df

    # Prefer s2006e2026bao to match reference Excel column
    preferred = f"s{START_YEAR}e2026bao"
    key = preferred if preferred in result else cagr_keys[-1]
    return float(result[key]), "OK", df


# ── Main ──────────────────────────────────────────────────────────────────────

def run_correlation():
    print(f"\n{'='*50}")
    print(f"PHASE 17-A: GRAND CORRELATION ANALYSIS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 1. Load reference
    df_ref = load_reference()
    total = len(df_ref)

    # 2. Connect to DuckDB (read-only)
    if not DB_PATH.exists():
        print(f"[ERROR] DuckDB not found at {DB_PATH}")
        return
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # 3. Process each stock
    results = []
    matches_tight = 0
    matches_loose = 0
    no_data_count = 0

    print(f"Processing {total} stocks...\n")
    for i, row in df_ref.iterrows():
        stock_id  = row["code"]
        ref_cagr  = float(row["ref_cagr"])

        try:
            ref_yrs = row.get("s2006e2026yrs", 0)
            mars_cagr, note, df_prices = calc_mars_cagr(con, stock_id, float(ref_yrs)) # Modified to get df_prices
        except Exception as e:
            mars_cagr, note, df_prices = 0.0, f"Error: {e}", pd.DataFrame() # Ensure df_prices is defined

        if note == "No Data":
            no_data_count += 1

        diff     = mars_cagr - ref_cagr
        abs_diff = abs(diff)

        # Debugging prints for large discrepancies
        if note == "OK" and abs_diff > 20.0:
            # Attempt to calculate a simpler CAGR for comparison
            simple_mars_cagr = 0.0
            num_years = 0
            start_price = 0.0
            end_price = 0.0
            valid_years = 0

            if not df_prices.empty:
                first_year = df_prices.index.min().year
                last_year = df_prices.index.max().year
                valid_years = last_year - first_year + 1

                if valid_years >= 2:
                    start_price = float(df_prices.iloc[0]['close'])
                    end_price = float(df_prices.iloc[-1]['close'])
                    num_years = last_year - first_year # This is typically (end_year - start_year) for CAGR
                    if num_years > 0:
                        simple_mars_cagr = calculate_cagr(start_price, end_price, num_years)

            print(f"DEBUG {stock_id}: Large difference ({abs_diff:.2f}%)")
            print(f"  Valid Years in data: {valid_years}")
            print(f"  Prices: Start={start_price:.2f} (date={df_prices.index.min().year if not df_prices.empty else 'N/A'}), End={end_price:.2f} (date={df_prices.index.max().year if not df_prices.empty else 'N/A'})")
            print(f"  CAGR: Ref={ref_cagr:.2f}%, Mars_Complex={mars_cagr:.2f}%")
            if num_years > 0:
                print(f"  CAGR: Simple_Calc={simple_mars_cagr:.2f}% ({num_years}yrs)")
            print(f"  Note: {note}")


        if note == "OK" and abs_diff <= MATCH_TIGHT:
            status = "Match"
            matches_tight += 1
        elif note == "OK" and abs_diff <= MATCH_LOOSE:
            status = "Close"
            matches_loose += 1
        elif note == "OK":
            status = "Mismatch"
        else:
            status = note  # "No Data" / "Error" / etc.

        results.append({
            "code":      stock_id,
            "name":      row.get("name", ""),
            "ref_cagr":  round(ref_cagr, 2),
            "mars_cagr": round(mars_cagr, 2),
            "diff":      round(diff, 2),
            "status":    status,
            "note":      note,
        })

        processed = i + 1
        if processed % 200 == 0 or processed == total:
            valid_so_far = processed - no_data_count
            rate = (matches_tight / valid_so_far * 100) if valid_so_far > 0 else 0
            print(f"  [{processed:4d}/{total}] Match(±1.5%): {rate:.1f}%  NoData: {no_data_count}")

    con.close()

    # 4. Save report
    df_out = pd.DataFrame(results)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(str(OUTPUT_CSV), index=False)

    # 5. Summary
    valid_count = total - no_data_count
    if valid_count == 0:
        valid_count = 1  # avoid div/0

    match_rate_tight = matches_tight / valid_count * 100
    match_rate_loose = (matches_tight + matches_loose) / valid_count * 100
    mae = df_out[df_out["note"] == "OK"]["diff"].abs().mean()

    print(f"\n{'='*50}")
    print("GRAND CORRELATION REPORT")
    print(f"{'='*50}")
    print(f"Total Reference Stocks : {total}")
    print(f"Valid Comparisons      : {valid_count}")
    print(f"No Data (not in DB)    : {no_data_count}")
    print(f"Match Rate (±1.5%)     : {match_rate_tight:.2f}%  ← Target >85%")
    print(f"Match Rate (±3.0%)     : {match_rate_loose:.2f}%")
    print(f"Mean Absolute Error    : {mae:.4f}%")
    print(f"{'='*50}")

    # Top outliers
    ok_df = df_out[df_out["note"] == "OK"].copy()
    if not ok_df.empty:
        outliers = pd.concat([
            ok_df.nlargest(15, "diff"),
            ok_df.nsmallest(15, "diff")
        ]).drop_duplicates().sort_values("diff", key=abs, ascending=False).head(15)
        print("\nTop 15 Outliers:")
        print(outliers[["code", "name", "ref_cagr", "mars_cagr", "diff"]].to_string(index=False))

    print(f"\nFull report saved → {OUTPUT_CSV}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Return match rate for CI/pass-fail
    return match_rate_tight


if __name__ == "__main__":
    run_correlation()
