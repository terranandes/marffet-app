#!/usr/bin/env python3
"""
Universal Precision Engine Verification

Runs ROICalculator against ALL stocks and generates a comprehensive report.
Identifies outliers and potential calculation issues.

Usage:
    python scripts/verify_universal.py [--top N] [--filter PATTERN]
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import pandas as pd
import json
from datetime import datetime
from app.project_tw.calculator import ROICalculator
from app.services.market_cache import MarketCache

def load_dividends():
    """Load dividend data from main.py's DIVIDENDS_DB."""
    from app.main import DIVIDENDS_DB
    return DIVIDENDS_DB

def run_universal_verification(top_n: int = None, filter_pattern: str = None):
    """Run verification against all stocks."""
    print("=" * 70)
    print("Universal Precision Engine Verification")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Initialize
    calc = ROICalculator()
    
    # Load data
    print("\n[1/4] Loading Data...")
    dividends_db = load_dividends()
    prices_db = MarketCache.get_prices_db()
    
    # Extract unique stock IDs from all years
    all_stock_ids = set()
    for year_data in prices_db.values():
        all_stock_ids.update(year_data.keys())
    
    stock_list = [{"id": sid, "name": sid} for sid in sorted(all_stock_ids)]
    
    # Filter if requested
    if filter_pattern:
        stock_list = [s for s in stock_list if filter_pattern in str(s.get('id', ''))]
    
    if top_n:
        stock_list = stock_list[:top_n]
    
    print(f"      Stocks to verify: {len(stock_list)}")
    
    # Run simulations
    print("\n[2/4] Running Simulations...")
    results = []
    errors = []
    
    for i, stock in enumerate(stock_list):
        stock_id = str(stock.get('id', ''))
        stock_name = stock.get('name', 'Unknown')
        
        if not stock_id:
            continue
        
        try:
            # Get history
            history = MarketCache.get_stock_history_fast(stock_id)
            if not history:
                errors.append({"stock_id": stock_id, "name": stock_name, "error": "No history"})
                continue
            
            df = pd.DataFrame(history)
            div_data = dividends_db.get(stock_id, {})
            
            # Run simulation
            result = calc.calculate_complex_simulation(
                df,
                start_year=2006,
                principal=1_000_000,
                annual_investment=60_000,
                dividend_data=div_data,
                stock_code=stock_id,
                buy_logic='FIRST_OPEN'
            )
            
            # Extract metrics
            final_value = result.get('finalValue', 0)
            history_list = result.get('history', [])
            
            if history_list:
                last = history_list[-1]
                cagr = last.get('cagr', 0)
                years = len(history_list)
            else:
                cagr = 0
                years = 0
            
            # Calculate total invested
            total_invested = 1_000_000 + (years - 1) * 60_000 if years > 0 else 1_000_000
            
            # ROI
            roi = (final_value - total_invested) / total_invested * 100 if total_invested > 0 else 0
            
            results.append({
                "stock_id": stock_id,
                "name": stock_name,
                "years": years,
                "cagr": round(cagr, 2),
                "final_value": round(final_value, 0),
                "total_invested": round(total_invested, 0),
                "roi_pct": round(roi, 1),
                "profitable": bool(final_value > total_invested)  # Convert numpy.bool_ to Python bool
            })
            
            # Progress
            if (i + 1) % 100 == 0:
                print(f"      Processed {i + 1}/{len(stock_list)} stocks...")
                
        except Exception as e:
            errors.append({"stock_id": stock_id, "name": stock_name, "error": str(e)})
    
    # Analysis
    print(f"\n[3/4] Analyzing {len(results)} results...")
    
    df_results = pd.DataFrame(results)
    
    # Statistics
    stats = {
        "total_stocks": len(results),
        "profitable_stocks": len(df_results[df_results['profitable']]),
        "loss_stocks": len(df_results[~df_results['profitable']]),
        "avg_cagr": round(df_results['cagr'].mean(), 2),
        "median_cagr": round(df_results['cagr'].median(), 2),
        "max_cagr": round(df_results['cagr'].max(), 2),
        "min_cagr": round(df_results['cagr'].min(), 2),
        "std_cagr": round(df_results['cagr'].std(), 2),
    }
    
    # Top performers
    top_10 = df_results.nlargest(10, 'cagr')[['stock_id', 'name', 'cagr', 'final_value']]
    
    # Worst performers  
    bottom_10 = df_results.nsmallest(10, 'cagr')[['stock_id', 'name', 'cagr', 'final_value']]
    
    # Outliers (CAGR > 30% or < -10%)
    outliers = df_results[(df_results['cagr'] > 30) | (df_results['cagr'] < -10)]
    
    # Print report
    print("\n" + "=" * 70)
    print("[4/4] VERIFICATION REPORT")
    print("=" * 70)
    
    print("\n📊 STATISTICS")
    print(f"   Total Stocks Verified: {stats['total_stocks']}")
    print(f"   Profitable:            {stats['profitable_stocks']} ({stats['profitable_stocks']/stats['total_stocks']*100:.1f}%)")
    print(f"   Loss-Making:           {stats['loss_stocks']} ({stats['loss_stocks']/stats['total_stocks']*100:.1f}%)")
    print(f"   Average CAGR:          {stats['avg_cagr']}%")
    print(f"   Median CAGR:           {stats['median_cagr']}%")
    print(f"   CAGR Range:            {stats['min_cagr']}% to {stats['max_cagr']}%")
    print(f"   CAGR Std Dev:          {stats['std_cagr']}%")
    
    print("\n🏆 TOP 10 PERFORMERS")
    print(top_10.to_string(index=False))
    
    print("\n📉 BOTTOM 10 PERFORMERS")
    print(bottom_10.to_string(index=False))
    
    if len(outliers) > 0:
        print(f"\n⚠️  OUTLIERS ({len(outliers)} stocks with CAGR > 30% or < -10%)")
        print(outliers[['stock_id', 'name', 'cagr', 'final_value']].to_string(index=False))
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)} stocks)")
        for e in errors[:10]:
            print(f"   {e['stock_id']} ({e['name']}): {e['error']}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    
    # Save detailed results
    output_path = "output/universal_verification.json"
    os.makedirs("output", exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "top_10": top_10.to_dict(orient='records'),
        "bottom_10": bottom_10.to_dict(orient='records'),
        "outliers": outliers[['stock_id', 'name', 'cagr', 'final_value']].to_dict(orient='records') if len(outliers) > 0 else [],
        "errors": errors,
        "all_results": results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Full report saved to: {output_path}")
    
    # Sanity checks
    print("\n" + "=" * 70)
    print("SANITY CHECKS")
    print("=" * 70)
    
    issues = []
    
    # Check 1: TSMC should be ~19%
    tsmc = df_results[df_results['stock_id'] == '2330']
    if len(tsmc) > 0:
        tsmc_cagr = tsmc.iloc[0]['cagr']
        if 17 <= tsmc_cagr <= 21:
            print(f"✅ TSMC (2330): {tsmc_cagr}% CAGR - Within expected range (17-21%)")
        else:
            print(f"❌ TSMC (2330): {tsmc_cagr}% CAGR - OUT OF EXPECTED RANGE")
            issues.append("TSMC CAGR unexpected")
    
    # Check 2: No impossible CAGRs (> 50% sustained is unlikely)
    impossible = df_results[df_results['cagr'] > 50]
    if len(impossible) > 0:
        print(f"⚠️  {len(impossible)} stocks with CAGR > 50% - Needs investigation:")
        for _, row in impossible.iterrows():
            print(f"   {row['stock_id']} ({row['name']}): {row['cagr']}%")
        issues.append(f"{len(impossible)} stocks with unrealistic CAGR")
    else:
        print("✅ No impossibly high CAGRs (>50%)")
    
    # Check 3: Negative returns should exist but be limited
    very_negative = df_results[df_results['cagr'] < -15]
    if len(very_negative) > 10:
        print(f"⚠️  {len(very_negative)} stocks with CAGR < -15% - May need review")
    else:
        print(f"✅ Negative CAGR distribution looks reasonable ({len(very_negative)} stocks < -15%)")
    
    # Verdict
    print("\n" + "=" * 70)
    if len(issues) == 0:
        print("🎉 VERIFICATION PASSED - Precision Engine appears correct")
        return 0
    else:
        print(f"⚠️  VERIFICATION HAS {len(issues)} CONCERNS - Review recommended")
        for issue in issues:
            print(f"   - {issue}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Precision Engine Verification")
    parser.add_argument("--top", type=int, help="Only verify top N stocks", default=None)
    parser.add_argument("--filter", type=str, help="Filter stock IDs containing pattern", default=None)
    args = parser.parse_args()
    
    exit_code = run_universal_verification(top_n=args.top, filter_pattern=args.filter)
    sys.exit(exit_code)
