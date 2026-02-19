from app.services.market_data_service import backfill_all_stocks
import logging

logging.basicConfig(level=logging.INFO)

print("Starting debug backfill for 1101...")
result = backfill_all_stocks(
    tickers=['1101'], 
    start_date='2000-01-01', 
    end_date='2004-12-31', 
    chunk_size=1
)
print("Result:", result)
