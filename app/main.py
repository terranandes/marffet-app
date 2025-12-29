
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from project_tw.strategies.cb import CBStrategy
from project_tw.calculator import ROICalculator

app = FastAPI(title="Martian Investment System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API Endpoints ----------------

@app.get("/api/results")
def get_results():
    """Return filtered results from Excel"""
    try:
        df = pd.read_excel("project_tw/output/stock_list_s2006e2025_filtered.xlsx")
        # Replace NaN
        df = df.fillna(0)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/race-data")
def get_race_data():
    """Return year-by-year ranking data for Bar Chart Race"""
    try:
        df = pd.read_excel("project_tw/output/stock_list_s2006e2025_filtered.xlsx")
        
        race_data = []
        year_cols = [c for c in df.columns if 'bao' in c]
        
        for _, row in df.iterrows():
            for col in year_cols:
                try:
                    # Format: s2006e2007bao
                    year_str = col.split('e')[1][:4]
                    val = row[col]
                    
                    if pd.notnull(val) and val != 0:
                        race_data.append({
                            "year": int(year_str),
                            "id": str(row['id']),
                            "name": row['name'],
                            "roi": round(val, 2), # ROI %
                            "value": round(val, 2) # For chart
                        })
                except: pass
                
        return race_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cb/analyze")
async def analyze_cb(code: str):
    """Analyze CB Code on demand"""
    try:
        strategy = CBStrategy()
        results = await strategy.analyze_list([code])
        if results:
            return results[0]
        return {"action": "NOT_FOUND"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cb/portfolio")
async def analyze_portfolio_cb():
    """Analyze all CBs in user's portfolio"""
    try:
        # 1. Get all CB targets from portfolio (user_id="default")
        portfolio_data = get_all_targets_by_type()
        cb_targets = portfolio_data.get("cb", [])
        
        if not cb_targets:
            return []
            
        # Extract codes (e.g. '65331')
        cb_codes = [t['id'] for t in cb_targets]
        
        # 2. Analyze
        strategy = CBStrategy()
        results = await strategy.analyze_specific_cbs(cb_codes)
        
        return results
    except Exception as e:
        return {"error": str(e)}


# ---------------- Portfolio API ----------------
from app.portfolio_db import (
    init_db, create_group, list_groups, delete_group,
    add_target, list_targets, delete_target,
    add_transaction, list_transactions, delete_transaction,
    get_target_summary, fetch_live_prices,
    get_all_targets_by_type, get_portfolio_history, get_portfolio_race_data,
    sync_all_dividends, get_dividend_history, get_total_dividends
)
from pydantic import BaseModel
from typing import Optional

# Initialize portfolio DB on startup
init_db()

class GroupCreate(BaseModel):
    name: str

class TargetCreate(BaseModel):
    stock_id: str
    stock_name: Optional[str] = None
    asset_type: Optional[str] = "stock"  # "stock" or "etf"

class TransactionCreate(BaseModel):
    type: str  # 'buy' or 'sell'
    shares: int
    price: float
    date: str  # YYYY-MM-DD

# Groups
@app.get("/api/portfolio/groups")
def api_list_groups():
    """List all portfolio groups"""
    try:
        return list_groups()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/groups")
def api_create_group(data: GroupCreate):
    """Create a new portfolio group"""
    try:
        return create_group(data.name)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/groups/{group_id}")
def api_delete_group(group_id: str):
    """Delete a portfolio group"""
    try:
        success = delete_group(group_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Targets
@app.get("/api/portfolio/groups/{group_id}/targets")
def api_list_targets(group_id: str):
    """List targets in a group"""
    try:
        return list_targets(group_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/groups/{group_id}/targets")
def api_add_target(group_id: str, data: TargetCreate):
    """Add a target (stock/ETF) to a group"""
    try:
        return add_target(group_id, data.stock_id, data.stock_name, data.asset_type or "stock")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/targets/{target_id}")
def api_delete_target(target_id: str):
    """Delete a target"""
    try:
        success = delete_target(target_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Transactions
@app.get("/api/portfolio/targets/{target_id}/transactions")
def api_list_transactions(target_id: str):
    """List transactions for a target"""
    try:
        return list_transactions(target_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/targets/{target_id}/transactions")
def api_add_transaction(target_id: str, data: TransactionCreate):
    """Add a transaction"""
    try:
        return add_transaction(target_id, data.type, data.shares, data.price, data.date)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/transactions/{tx_id}")
def api_delete_transaction(tx_id: str):
    """Delete a transaction"""
    try:
        success = delete_transaction(tx_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Summary
@app.get("/api/portfolio/targets/{target_id}/summary")
def api_target_summary(target_id: str, current_price: Optional[float] = None):
    """Get P/L summary for a target"""
    try:
        return get_target_summary(target_id, current_price)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Live Prices
@app.get("/api/portfolio/prices")
def api_live_prices(stock_ids: str):
    """
    Fetch live prices for multiple stocks.
    stock_ids: comma-separated list (e.g., "2330,6533,2454")
    """
    try:
        ids = [s.strip() for s in stock_ids.split(",") if s.strip()]
        if not ids:
            return {}
        return fetch_live_prices(ids)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Trend Dashboard Endpoints
@app.get("/api/portfolio/trend")
def api_portfolio_trend(months: int = 12):
    """Get monthly portfolio cost history for trend chart"""
    try:
        return get_portfolio_history(months=months)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/by-type")
def api_portfolio_by_type():
    """Get all targets grouped by asset type (stock/etf)"""
    try:
        return get_all_targets_by_type()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/race-data")
def api_portfolio_race():
    """Get race data for live portfolio BCR animation"""
    try:
        return get_portfolio_race_data()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Dividend Tracking Endpoints
@app.post("/api/portfolio/sync-dividends")
def api_sync_dividends():
    """Sync dividends for all user's targets"""
    try:
        result = sync_all_dividends()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/targets/{target_id}/dividends")
def api_target_dividends(target_id: str):
    """Get dividend history for a target"""
    try:
        return get_dividend_history(target_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/cash")
def api_dividend_cash():
    """Get total dividend cash"""
    try:
        return get_total_dividends()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------------- Static Files ----------------
# Must come LAST to avoid capturing API routes
# Create dir if not exists
os.makedirs("app/static", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")
