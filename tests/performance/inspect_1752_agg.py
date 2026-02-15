import asyncio
import os
import sys
import pandas as pd
from datetime import datetime

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.market_data_provider import MarketDataProvider

async def inspect_1752_agg():
    print("📊 Inspecting Aggregate Stats for 1752...")
    
    start_date = "2006-01-01"
    all_prices_df = MarketDataProvider.get_all_daily_history_df(start_date)
    df_1752 = all_prices_df[all_prices_df['stock_id'] == '1752'].copy()
    
    print(f"Total rows for 1752: {len(df_1752)}")
    
    df_1752['year'] = df_1752['date'].dt.year
    
    yearly_agg = df_1752.groupby(['stock_id', 'year']).agg(
        action_price=('open', 'first'),
        avg_price=('close', 'mean'),
        end_price=('close', 'last')
    ).reset_index()
    
    print("\nYearly Aggregated Stats:")
    print(yearly_agg.to_string())

if __name__ == "__main__":
    asyncio.run(inspect_1752_agg())
