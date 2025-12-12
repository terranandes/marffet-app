from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
from typing import List, Optional
import asyncio
from pydantic import BaseModel

# Import Strategies
# Ensure project root is in pythonpath if running from app/ folder
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_tw.strategies.mars import MarsStrategy
from project_tw.strategies.cb import CBStrategy

app = FastAPI(title="Martian API", version="1.0.0")

# CORS Setup (Allow Frontend)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class MarsRequest(BaseModel):
    stock_codes: List[str]
    start_year: int = 2006
    end_year: int = 2025

class CBRequest(BaseModel):
    cb_price: float
    stock_price: float
    conversion_price: float

class CBResponse(BaseModel):
    premium_rate: float
    signal: str
    action: str
    detail: str
    color: str

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Martian API is ready 🚀"}

@app.post("/api/mars/analyze")
async def analyze_mars(req: MarsRequest):
    """
    Analyze a list of stocks using Mars Strategy.
    """
    start_time = time.time()
    strategy = MarsStrategy()
    print(f"--- Received Analyze Request for {len(req.stock_codes) if req.stock_codes else 0} codes (Range: {req.start_year}-{req.end_year}) ---")
    try:
        # Handling Empty Codes: Revert to Safe "Demo List" (Success Case)
        # If user wants full market, they must request 'ALL_MARKET'
        
        DEMO_STOCKS = ['2330', '2317', '2454', '2412', '0050', '2303', '2881', '2882']
        
        codes = req.stock_codes
        
        # Scenario 1: Empty or Default -> Use Demo List (Fast)
        if not codes or (len(codes) == 1 and codes[0] == ""):
            print("No specific codes provided. Using Safe Demo List.")
            codes = DEMO_STOCKS
            
        # Scenario 2: User requests "ALL_MARKET" -> Load CSV
        elif 'ALL_MARKET' in codes:
            print("Received ALL_MARKET request. Loading Full List...")
            try:
                # Load full list
                df_list = pd.read_csv("project_tw/stock_list.csv")
                
                # QUANTITY LIMIT: 
                # Scanning 1000 stocks takes too long for sync request.
                # Cap to Top 50 (or 100) for this "Expand" feature.
                codes = df_list['code'].astype(str).tolist()[:50]
                print(f"Loaded {len(codes)} stocks from Full Market (Capped).")
            except Exception as e:
                print(f"Failed to load stock list: {e}")
                codes = DEMO_STOCKS # Fallback
        
        # Run analysis (Single Call)
        raw_results = await strategy.analyze_stock_batch(
            codes, req.start_year, req.end_year
        )
        
        # Filter and Rank
        top_50 = strategy.filter_and_rank(raw_results)
        
        # Save to Excel
        output_file = f"project_tw/output/stock_list_s{req.start_year}e{req.end_year}_filtered.xlsx"
        strategy.save_to_excel(output_file)
        
        print(f"Analysis Complete. Found {len(top_50)} results. Time: {time.time() - start_time:.2f}s")
        return {"count": len(top_50), "results": top_50, "saved_to": output_file}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cb/evaluate", response_model=CBResponse)
def evaluate_cb(req: CBRequest):
    """
    Evaluate Convertible Bond Signal.
    """
    strategy = CBStrategy()
    premium = strategy.calculate_premium(req.cb_price, req.stock_price, req.conversion_price)
    advice = strategy.evaluate(premium)
    
    return {
        "premium_rate": premium,
        "signal": advice.signal.value,
        "action": advice.action_short,
        "detail": advice.action_detail,
        "color": advice.color
    }

@app.post("/api/data/race")
async def get_race_data(req: MarsRequest):
    """
    Generate Plotly Bar Chart Race JSON.
    """
    import pandas as pd
    from project_tw.crawler import TWSECrawler
    from project_tw.plot_race import generate_bar_chart_race_plotly
    from project_tw.strategies.mars import MarsStrategy
    import json

    crawler = TWSECrawler()
    combined_data = {}
    
    # 1. Fetch Data
    targets = req.stock_codes
    
    # If no specific codes requested, or special 'MARS_TOP_50' flag, use the best stocks strategies
    if not targets or 'MARS_TOP50' in targets:
        print("Identifying Top Candidates for Race...")
        
        # 0. Try to load from existing Mars Output (Fastest & Consistent)
        # Check output/stock_list_{start_year}e{end_year}_filtered.xlsx
        # Or even better, check the most recent one covering similar range
        output_file = f"project_tw/output/stock_list_s{req.start_year}e{req.end_year}_filtered.xlsx"
        
        candidates_found = False
        if os.path.exists(output_file):
             print(f"Loading candidates from {output_file}")
             try:
                 df_cached = pd.read_excel(output_file)
                 # Expecting 'id' column (legacy format) or 'stock_code'
                 if 'id' in df_cached.columns:
                     targets = df_cached['id'].astype(str).tolist()[:20] 
                     candidates_found = True
                 elif 'stock_code' in df_cached.columns:
                     targets = df_cached['stock_code'].astype(str).tolist()[:20] 
                     candidates_found = True
             except Exception as e:
                 print(f"Failed to read cache: {e}")
        
        # 1. Fallback: Run heuristic analysis if no file exists
        if not candidates_found:
            print("No cache found. Running live heuristic analysis...")
            strategy = MarsStrategy()
            # Load full list
            try:
                 df_list = pd.read_csv("project_tw/stock_list.csv")
                 all_codes = df_list['code'].astype(str).tolist()
            except:
                 all_codes = ['2330', '2317', '2454', '0050'] # Fallback
                 
            # Analyze latest 2 years only to pick candidates (Fast)
            latest_results = await strategy.analyze_stock_batch(all_codes[:200], req.end_year-1, req.end_year) # Limit to 200 for demo speed
            top_candidates = strategy.filter_and_rank(latest_results)
            targets = [t['stock_code'] for t in top_candidates[:20]] # Take Top 20 for race
        
    
    # 2. Fetch Data Parallelly
    print(f"Fetching race data for {len(targets)} targets: {targets}")
    
    async def fetch_one(code):
        try:
             raw = await crawler.fetch_history(code, req.start_year, req.end_year)
             df_stock = crawler.parse_to_dataframe(raw)
             if not df_stock.empty and len(df_stock) > 20: # Ensure minimal data
                 start_price = df_stock['close'].iloc[0]
                 if start_price > 0:
                     df_stock['roi_cum'] = ((df_stock['close'] - start_price) / start_price) * 100
                     return code, df_stock['roi_cum']
        except Exception as e:
             print(f"Error fetching {code} for race: {e}")
        return None, None

    # Using gather - fetch_history uses internal semaphore if properly implemented, or rely on internal throttling
    # Current crawler implementation has `async with self.sem:` inside it, so this is safe.
    tasks = [fetch_one(code) for code in targets]
    results = await asyncio.gather(*tasks)
    
    for code, series in results:
        if code and series is not None:
             combined_data[code] = series

    if not combined_data:
        print("Error: No valid race data found after fetch.")
        raise HTTPException(status_code=404, detail="No data found for race")
        
    # 2. Align Data
    df_rois = pd.DataFrame(combined_data)
    # Fill NaN (e.g. if one stock started later)
    df_rois = df_rois.fillna(method='ffill').fillna(0)
    
    # 3. Generate Plot
    try:
        fig = generate_bar_chart_race_plotly(df_rois, n_bars=10, title=f"Stock Race {req.start_year}-{req.end_year}")
        return json.loads(fig.to_json())
    except Exception as e:
        print(f"Error generating race plot: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
