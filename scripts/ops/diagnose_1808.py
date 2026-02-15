
import asyncio
import pandas as pd
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import ROICalculator, _get_detector

async def diagnose_1808():
    stock_id = "1808"
    start_year = 2006
    
    prices_df = MarketDataProvider.get_all_daily_history_df("2006-01-01")
    df = prices_df[prices_df['stock_id'] == stock_id].copy()
    df['year'] = df['date'].dt.year
    
    divs_df = MarketDataProvider.get_all_dividends_df(2006)
    stock_divs = divs_df[divs_df['stock_id'] == stock_id]
    
    div_data = {}
    for _, row in stock_divs.iterrows():
        div_data[int(row['year'])] = {'cash': float(row['cash']), 'stock': float(row['stock'])}

    calc = ROICalculator()
    results = calc.calculate_complex_simulation(
        df, start_year, stock_code=stock_id, dividend_data=div_data, buy_logic='YEAR_START_OPEN'
    )
    
    print(f"--- 1808 Diagnosis (Start 2006, End 2025) ---")
    print(f"{'Year':<6} {'Price(E)':<10} {'Shares':<10} {'Value':<12} {'CashDiv':<10} {'StockDiv':<10}")
    
    for h in results['history']:
        y = h['year']
        d = div_data.get(y, {'cash':0, 'stock':0})
        # Note: Shares isn't in history by default, wealth / price_end
        # Need to find p_end for that year
        y_data = df[df['year'] == y]
        p_end = y_data.iloc[-1]['close'] if not y_data.empty else 0
        shares = h['value'] / p_end if p_end > 0 else 0
        
        print(f"{y:<6} {p_end:<10.2f} {int(shares):<10} {int(h['value']):<12} {d['cash']:<10.2f} {d['stock']:<10.2f}")

    print(f"\nFinal CAGR: {results.get('cagr', 0):.2f}%")

if __name__ == "__main__":
    asyncio.run(diagnose_1808())
