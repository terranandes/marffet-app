
import asyncio
import pandas as pd
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import ROICalculator, _get_detector
from app.services.market_db import get_connection

async def verify_tsmc():
    print("🚀 Verifying TSMC (2330) Methodology Alignment...")
    print("🎯 Target: 22.2% CAGR (2006-2025)")
    
    # 1. Fetch TSMC data
    # Standard parameters: 1,000,000 Principal, 60,000 Contribution
    start_year = 2006
    principal = 1_000_000
    contribution = 60_000
    
    prices_df = MarketDataProvider.get_all_daily_history_df("2006-01-01")
    tsmc_df = prices_df[prices_df['stock_id'] == '2330'].copy()
    tsmc_df['year'] = tsmc_df['date'].dt.year
    tsmc_df = tsmc_df[(tsmc_df['year'] >= 2006) & (tsmc_df['year'] <= 2025)]
    
    if tsmc_df.empty:
        print("❌ Error: No TSMC data found in DuckDB.")
        return

    # Dividends
    divs_df = MarketDataProvider.get_all_dividends_df(2006)
    tsmc_divs = divs_df[divs_df['stock_id'] == '2330']
    stock_divs = {}
    for _, row in tsmc_divs.iterrows():
        y = int(row['year'])
        stock_divs[y] = {
            'cash': float(row['cash']),
            'stock': float(row['stock'])
        }

    # 2. Run Simulation
    calculator = ROICalculator()
    detector = _get_detector()
    
    # Ensure detector tracks 2330 history
    detector.detect_splits("2330", tsmc_df.reset_index().to_dict('records'))
    
    # Use the same parameters as MarsStrategy analyze
    results = calculator.calculate_complex_simulation(
        tsmc_df,
        start_year=start_year,
        principal=principal,
        annual_investment=contribution,
        dividend_data=stock_divs,
        stock_code="2330",
        buy_logic='YEAR_START_OPEN'
    )
    
    final_value = results.get('finalValue', 0)
    total_cost = results.get('totalCost', 0)
    cagr = results.get('cagr', 0)
    roi = results.get('roi', 0)
    
    print(f"\n📊 Results (2006-2025):")
    print(f" - Final Wealth:   ${final_value:,.0f}")
    print(f" - Total Invested: ${total_cost:,.0f}")
    print(f" - ROI:            {roi:.2f}%")
    print(f" - CAGR:           {cagr:.2f}%")
    
    target_cagr = 22.2
    diff = abs(cagr - target_cagr)
    
    if diff <= 0.5:
        print(f"\n✅ PASS: CAGR {cagr:.2f}% is within tolerance of {target_cagr}% target.")
    else:
        print(f"\n❌ FAIL: CAGR {cagr:.2f}% diverges from {target_cagr}% target by {diff:.2f}%.")
        
    print("\n💡 Note: Reference methodology specified in docs/product/moneycome_methodology.md")

if __name__ == "__main__":
    asyncio.run(verify_tsmc())
