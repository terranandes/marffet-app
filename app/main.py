from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio

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
    start_year: int = 2019
    end_year: int = 2024

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
    strategy = MarsStrategy()
    try:
        # Run analysis (this might take time, in prod use background tasks)
        raw_results = await strategy.analyze_stock_batch(
            req.stock_codes, req.start_year, req.end_year
        )
        # Filter and Rank
        top_50 = strategy.filter_and_rank(raw_results)
        return {"count": len(top_50), "results": top_50}
    except Exception as e:
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
    import json

    crawler = TWSECrawler()
    combined_data = {}
    
    # 1. Fetch Data
    # Cap at 5 stocks for demo speed if list is too long, or use req list
    target_stocks = req.stock_codes[:10] 
    
    for code in target_stocks:
        raw = await crawler.fetch_history(code, req.start_year, req.end_year)
        df_stock = crawler.parse_to_dataframe(raw)
        
        if not df_stock.empty:
            # Calculate ROI relative to Day 1 of this period
            # Or just use Price? Let's use Cumulative Return %
            start_price = df_stock['close'].iloc[0]
            if start_price > 0:
                df_stock['roi_cum'] = ((df_stock['close'] - start_price) / start_price) * 100
                # Reindex to handle missing dates? will be handled by plot_race logic
                combined_data[code] = df_stock['roi_cum']
    
    if not combined_data:
        raise HTTPException(status_code=404, detail="No data found for race")
        
    # 2. Align Data
    df_rois = pd.DataFrame(combined_data)
    # Fill NaN (e.g. if one stock started later)
    df_rois = df_rois.fillna(0) # Or method='ffill'
    
    # 3. Generate Plot
    fig = generate_bar_chart_race_plotly(df_rois, n_bars=10, title=f"Stock Race {req.start_year}-{req.end_year}")
    
    # 4. Return JSON
    return json.loads(fig.to_json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
