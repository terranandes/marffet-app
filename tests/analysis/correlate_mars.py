#!/usr/bin/env python3
"""
Phase 3: Mars Strategy Correlation Script

Verifies that the Martian ROICalculator produces CAGR values within 0.5% of MoneyCome.

Reference Values (MoneyCome Single Mode - 2006-2026):
- 2330 (TSMC): ~18.8% CAGR
- 2317 (Hon Hai): ~8.5% CAGR  
- 2454 (MediaTek): ~15.2% CAGR

Usage:
    python scripts/correlate_mars.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.project_tw.calculator import ROICalculator
from app.services.market_data_provider import MarketDataProvider

# MoneyCome Reference Data (2006-2026, BAO Strategy)
# Source: Manual verification against MoneyCome Excel
MONECOME_REFERENCE = {
    "2330": {"name": "TSMC", "cagr": 18.8, "final_value": 86_000_000},  # ~$86M
    "2317": {"name": "Hon Hai", "cagr": 8.5, "final_value": 10_000_000},  # Approx
    "2454": {"name": "MediaTek", "cagr": 15.2, "final_value": 45_000_000},  # Approx
}

# Tolerance: 0.5% absolute difference in CAGR
CAGR_TOLERANCE = 0.5
# Tolerance: 5% relative difference in final value
VALUE_TOLERANCE_PCT = 5.0

def load_dividends():
    """Load dividend data from DuckDB via MarketDataProvider."""
    from app.services.market_data_provider import MarketDataProvider
    return MarketDataProvider.load_dividends_dict()

def run_correlation():
    """Run correlation check against MoneyCome reference."""
    print("=" * 60)
    print("Mars Strategy Correlation Script - Phase 3")
    print("=" * 60)
    
    # Initialize
    calc = ROICalculator()
    dividends_db = load_dividends()
    
    # Ensure DuckDB stats
    print("\n[1/3] Checking Market Data...")
    stats = MarketDataProvider.get_stats()
    print(f"      Rows: {stats.get('price_rows', 0):,}")
    
    results = []
    all_pass = True
    
    print("\n[2/3] Running Simulations...")
    
    for stock_id, ref in MONECOME_REFERENCE.items():
        print(f"\n--- {stock_id} ({ref['name']}) ---")
        
        # Get stock history
        df = MarketDataProvider.get_daily_history_df(stock_id)
        if df.empty:
            print(f"  ERROR: No history found for {stock_id}")
            all_pass = False
            continue
        
        # Prepare DataFrame for ROICalculator (needs year, month columns)
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        # Get dividends
        div_data = dividends_db.get(stock_id, {})
        
        # Run simulation (BAO - Buy At Open, First Day)
        sim_result = calc.calculate_complex_simulation(
            df,
            start_year=2006,
            principal=1_000_000,
            annual_investment=60_000,
            dividend_data=div_data,
            stock_code=stock_id,
            buy_logic='FIRST_OPEN'
        )
        
        # Extract results
        final_value = sim_result.get('finalValue', 0)
        history_list = sim_result.get('history', [])
        
        # Calculate overall CAGR from history
        if history_list and len(history_list) > 1:
            last_point = history_list[-1]
            our_cagr = last_point.get('cagr', 0)
        else:
            our_cagr = 0
        
        # Compare
        cagr_diff = abs(our_cagr - ref['cagr'])
        value_diff_pct = abs(final_value - ref['final_value']) / ref['final_value'] * 100 if ref['final_value'] > 0 else 100
        
        cagr_pass = cagr_diff <= CAGR_TOLERANCE
        value_pass = value_diff_pct <= VALUE_TOLERANCE_PCT
        
        status = "✅ PASS" if (cagr_pass and value_pass) else "❌ FAIL"
        if not (cagr_pass and value_pass):
            all_pass = False
        
        print(f"  MoneyCome CAGR: {ref['cagr']:.1f}%")
        print(f"  Our CAGR:       {our_cagr:.1f}%")
        print(f"  CAGR Diff:      {cagr_diff:.2f}% {'✅' if cagr_pass else '❌'}")
        print(f"  Final Value:    ${final_value:,.0f}")
        print(f"  Reference:      ${ref['final_value']:,.0f}")
        print(f"  Value Diff:     {value_diff_pct:.1f}% {'✅' if value_pass else '❌'}")
        print(f"  Status:         {status}")
        
        results.append({
            "stock_id": stock_id,
            "name": ref['name'],
            "monecome_cagr": ref['cagr'],
            "our_cagr": our_cagr,
            "cagr_diff": cagr_diff,
            "cagr_pass": cagr_pass,
            "final_value": final_value,
            "ref_value": ref['final_value'],
            "value_diff_pct": value_diff_pct,
            "value_pass": value_pass
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("[3/3] CORRELATION SUMMARY")
    print("=" * 60)
    
    passes = sum(1 for r in results if r['cagr_pass'] and r['value_pass'])
    total = len(results)
    
    print(f"\nResults: {passes}/{total} stocks within tolerance")
    print(f"CAGR Tolerance: ±{CAGR_TOLERANCE}%")
    print(f"Value Tolerance: ±{VALUE_TOLERANCE_PCT}%")
    
    if all_pass:
        print("\n🎉 CORRELATION VERIFIED - All stocks match MoneyCome!")
        return 0
    else:
        print("\n⚠️  CORRELATION FAILED - Some stocks differ from MoneyCome")
        return 1

if __name__ == "__main__":
    exit_code = run_correlation()
    sys.exit(exit_code)
