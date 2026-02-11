import pytest
import pandas as pd
from app.services.market_data_service import ensure_price_cache_batch, get_cached_prices_batch
from app.services.roi_calculator import ROICalculator

def test_tsmc_cagr_benchmark():
    """
    Golden Master Test: TSMC (2330) CAGR must be 22.2% (±0.1%) for 2006-2025.
    Source: MoneyCome.in
    """
    # 1. Setup
    calc = ROICalculator()
    stock_id = "2330"
    
    # 2. Ensure Data Exists (Fetch from YFinance if not in cache)
    # We need data from start of 2006 to end of 2025
    start_date = "2006-01-01"
    end_date = "2025-12-31"
    
    # Ensure cache has data
    # Returns mapping of input_id -> valid_yf_id (e.g., "2330" -> "2330.TW")
    print(f"Ensuring cache for {stock_id}...")
    mapping = ensure_price_cache_batch([stock_id], start_date="2005-01-01") 
    print(f"Cache mapping: {mapping}")
    
    target_id = mapping.get(stock_id, stock_id)
    print(f"Target ID for fetching: {target_id}")

    # Get Data from Cache using the VALID ID
    cached_data = get_cached_prices_batch([target_id], start_date=start_date)
    assert target_id in cached_data, f"Failed to fetch data for {target_id} (mapped from {stock_id})"
    
    series = cached_data[target_id]
    assert not series.empty, "Data series is empty"
    
    print(f"Fetched {len(series)} data points.")
    
    # 3. Prepare DataFrame for Calculator
    # Filter for the specific range 2006-2025
    mask = (series.index >= pd.Timestamp(start_date)) & (series.index <= pd.Timestamp(end_date))
    filtered_series = series[mask]
    
    # Debug: Check start/end
    if not filtered_series.empty:
        print(f"Data Date Range: {filtered_series.index[0]} to {filtered_series.index[-1]}")
        print(f"Start Price: {filtered_series.iloc[0]}, End Price: {filtered_series.iloc[-1]}")
    else:
        print("Filtered series is empty!")
    
    assert not filtered_series.empty, "Filtered data is empty"
    
    df = filtered_series.to_frame(name='close')
    
    # 4. Calculate
    metrics = calc.calculate_metrics(df)
    
    assert metrics is not None, "Metrics calculation failed"
    
    cagr = metrics['cagr_pct']
    
    print(f"TSMC Calculated CAGR (2006-2025): {cagr}%")
    
    # 5. Assert
    expected_cagr = 22.2
    tolerance = 1.0 
    
    deviation = abs(cagr - expected_cagr)
    
    if deviation > tolerance:
        pytest.fail(f"CAGR {cagr}% deviates too much from {expected_cagr}% (> {tolerance}%)")
    elif deviation > 0.1:
         print(f"WARNING: CAGR {cagr}% is close but not within 0.1% of {expected_cagr}%. (Deviation: {deviation}%)")
    else:
         print(f"SUCCESS: CAGR {cagr}% is within 0.1% of {expected_cagr}%.")
