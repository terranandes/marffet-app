#!/usr/bin/env python3
"""
Grand Correlation: All Stocks vs MoneyCome Reference Excel

Correlates our ROICalculator BAO CAGR (2006→2026) against the unfiltered
MoneyCome reference Excel for ALL stocks.

Usage:
    uv run python tests/analysis/correlate_all_stocks.py
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
from datetime import datetime

REFERENCE_FILE = os.path.join(
    os.path.dirname(__file__), '..', '..',
    'app', 'project_tw', 'references', 'stock_list_s2006e2026_unfiltered.xlsx'
)

# Tolerance bands
CAGR_TOLERANCE_TIGHT = 1.0   # ±1.0% for "match"
CAGR_TOLERANCE_LOOSE = 3.0   # ±3.0% for "close"


def run_full_correlation():
    print("=" * 70)
    print("Grand Correlation: All Stocks vs MoneyCome Reference")
    print("=" * 70)

    # 1. Load Reference
    print("\n[1/5] Loading MoneyCome reference Excel...")
    ref_df = pd.read_excel(REFERENCE_FILE)
    ref_df['id'] = ref_df['id'].astype(str)
    # Only keep stocks with valid 2006→2026 BAO CAGR
    ref_df = ref_df[ref_df['s2006e2026bao'].notna()].copy()
    print(f"       Valid reference stocks: {len(ref_df)}")

    # 2. Run MarsStrategy bulk simulation
    print("\n[2/5] Running MarsStrategy simulation (bulk DuckDB load)...")
    from app.services.strategy_service import MarsStrategy
    import asyncio

    strategy = MarsStrategy()
    t_start = time.time()

    # Run simulation for ALL stocks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        raw_results = loop.run_until_complete(
            strategy.analyze(
                stock_ids=["ALL"],
                start_year=2006,
                principal=1_000_000,
                contribution=60_000
            )
        )
    finally:
        loop.close()

    t_elapsed = time.time() - t_start
    print(f"       Simulation completed in {t_elapsed:.1f}s")
    print(f"       Stocks simulated: {len(raw_results)}")

    # 3. Build result lookup
    print("\n[3/5] Matching results to MoneyCome reference...")
    our_results = {}
    for res in raw_results:
        code = str(res.get('stock_code', res.get('id', '')))
        # Get BAO CAGR from history
        history = res.get('history', [])
        cagr = 0.0
        if history and len(history) > 1:
            last = history[-1]
            cagr = last.get('cagr', 0.0)
        # Also check top-level keys
        if cagr == 0.0:
            cagr = res.get('cagr_pct', res.get('cagr', 0.0))
        our_results[code] = {
            'cagr': cagr,
            'final_value': res.get('finalValue', 0),
            'valid_years': res.get('valid_lasting_years', 0),
        }

    # 4. Correlate
    print("\n[4/5] Computing correlation statistics...")
    matched = 0
    close_match = 0
    total_compared = 0
    mismatches = []
    all_diffs = []

    rows_for_excel = []

    for _, ref_row in ref_df.iterrows():
        sid = str(ref_row['id'])
        mc_cagr = ref_row['s2006e2026bao']
        mc_bah = ref_row.get('s2006e2026bah', np.nan)
        mc_bal = ref_row.get('s2006e2026bal', np.nan)
        mc_yrs = ref_row.get('s2006e2026yrs', np.nan)

        our = our_results.get(sid)
        if our is None:
            rows_for_excel.append({
                'stock_id': sid,
                'name': ref_row.get('name', ''),
                'mc_bao_cagr': mc_cagr,
                'our_bao_cagr': None,
                'diff': None,
                'status': 'NOT_IN_DB'
            })
            continue

        our_cagr = our['cagr']
        diff = our_cagr - mc_cagr
        abs_diff = abs(diff)
        total_compared += 1
        all_diffs.append(abs_diff)

        if abs_diff <= CAGR_TOLERANCE_TIGHT:
            status = '✅ MATCH'
            matched += 1
        elif abs_diff <= CAGR_TOLERANCE_LOOSE:
            status = '🟡 CLOSE'
            close_match += 1
        else:
            status = '❌ MISS'
            mismatches.append((sid, ref_row.get('name', ''), mc_cagr, our_cagr, diff))

        rows_for_excel.append({
            'stock_id': sid,
            'name': ref_row.get('name', ''),
            'mc_bao_cagr': mc_cagr,
            'our_bao_cagr': round(our_cagr, 2),
            'diff': round(diff, 2),
            'abs_diff': round(abs_diff, 2),
            'mc_yrs': mc_yrs,
            'our_valid_yrs': our.get('valid_years', 0),
            'status': status
        })

    # 5. Report
    print("\n" + "=" * 70)
    print("[5/5] CORRELATION REPORT")
    print("=" * 70)

    not_in_db = len(ref_df) - total_compared
    print(f"\n  Reference stocks:      {len(ref_df)}")
    print(f"  Compared:              {total_compared}")
    print(f"  Not in DuckDB:         {not_in_db}")
    print(f"  ✅ Match (±{CAGR_TOLERANCE_TIGHT}%):    {matched}  ({matched/max(total_compared,1)*100:.1f}%)")
    print(f"  🟡 Close (±{CAGR_TOLERANCE_LOOSE}%):    {close_match}  ({close_match/max(total_compared,1)*100:.1f}%)")
    miss_count = total_compared - matched - close_match
    print(f"  ❌ Miss  (>{CAGR_TOLERANCE_LOOSE}%):     {miss_count}  ({miss_count/max(total_compared,1)*100:.1f}%)")

    if all_diffs:
        diffs_arr = np.array(all_diffs)
        print(f"\n  Mean Abs Error:        {diffs_arr.mean():.2f}%")
        print(f"  Median Abs Error:      {np.median(diffs_arr):.2f}%")
        print(f"  Std Dev:               {diffs_arr.std():.2f}%")
        print(f"  P90 Error:             {np.percentile(diffs_arr, 90):.2f}%")
        print(f"  P95 Error:             {np.percentile(diffs_arr, 95):.2f}%")

    print(f"\n  ⏱️  Simulation Time:    {t_elapsed:.1f}s")

    # Top 10 worst mismatches
    if mismatches:
        mismatches.sort(key=lambda x: abs(x[4]), reverse=True)
        print(f"\n  Top 10 Worst Mismatches:")
        print(f"  {'ID':>6}  {'Name':<10}  {'MC':>7}  {'Ours':>7}  {'Diff':>7}")
        for sid, name, mc, ours, diff in mismatches[:10]:
            print(f"  {sid:>6}  {(name or '')[:10]:<10}  {mc:>7.1f}  {ours:>7.1f}  {diff:>+7.1f}")

    # Key stocks check
    print(f"\n  Key Stock Checks:")
    for key_id, key_name in [('2330', 'TSMC'), ('2317', 'Hon Hai'), ('2454', 'MediaTek'), ('0050', '元大台灣50')]:
        mc_row = ref_df[ref_df['id'] == key_id]
        mc_val = mc_row['s2006e2026bao'].values[0] if not mc_row.empty else None
        our = our_results.get(key_id, {}).get('cagr', None)
        if mc_val is not None and our is not None:
            print(f"    {key_id} ({key_name}): MC={mc_val:.1f}%  Ours={our:.1f}%  Diff={our-mc_val:+.1f}%")
        else:
            print(f"    {key_id} ({key_name}): {'MC='+ str(mc_val) if mc_val else 'NO_REF'}  {'Ours='+str(our) if our else 'NO_SIM'}")

    # Save Excel
    output_path = os.path.join(os.path.dirname(__file__), '..', 'log', 'correlation_report.xlsx')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df = pd.DataFrame(rows_for_excel)
    result_df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"\n  📊 Report saved to: {output_path}")

    return {
        'total_ref': len(ref_df),
        'compared': total_compared,
        'matched': matched,
        'close': close_match,
        'miss': miss_count,
        'elapsed': t_elapsed,
        'mean_error': float(diffs_arr.mean()) if all_diffs else 0,
    }


if __name__ == "__main__":
    result = run_full_correlation()
    match_rate = (result['matched'] + result['close']) / max(result['compared'], 1) * 100
    print(f"\n{'='*70}")
    if match_rate >= 85:
        print(f"🎉 OVERALL: {match_rate:.1f}% within ±{CAGR_TOLERANCE_LOOSE}% — CORRELATION PASSED")
    else:
        print(f"⚠️  OVERALL: {match_rate:.1f}% within ±{CAGR_TOLERANCE_LOOSE}% — NEEDS INVESTIGATION")
    sys.exit(0 if match_rate >= 85 else 1)
