from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import pandas as pd
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())
load_dotenv()

from project_tw.strategies.cb import CBStrategy
from project_tw.calculator import ROICalculator
from app.services.notifications import NotificationEngine
from app.auth import router as auth_router, get_current_user
from app.portfolio_db import get_all_targets_by_type

app = FastAPI(title="Martian Investment System")

# Session Middleware (Must be before CORS if using cookies, relies on correct ordering)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    same_site='lax',      # Required for OAuth redirects
    https_only=False,     # Allow HTTP for localhost
    max_age=60 * 60 * 24 * 7  # 7 days
)

# ... (CORS logic remains) ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production with Auth, this should be specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

# ---------------- Notification Engine ----------------
notification_engine = NotificationEngine()

@app.get("/api/notifications/check")
async def check_notifications(user: dict = Depends(get_current_user)):
    """Trigger generic strategy alerts"""
    # If no user, default to 'default' (legacy)
    user_id = user['id'] if user else 'default'
    print(f"Checking notifications for user: {user_id}")
    
    try:
        # Get targets for specific user
        # Implementation Detail: create a specific getter in portfolio_db or update existing
        # Hack: update get_all_targets_by_type to accept user_id? 
        # Or just fetch raw here.
        # Let's assume get_all_targets_by_type has been updated (I need to update it next!)
        portfolio_data = get_all_targets_by_type(user_id=user_id) 

        targets = []
        for cat in portfolio_data.values():
            targets.extend(cat)
            
        # Get Txns to calculate shares
        # Hack: We need a way to get shares.
        # Let's assume we can fetch shares from 'portfolio_db' directly or re-use logic.
        # For this prototype: Fetch all transactions and sum them up.
        from app.portfolio_db import get_transactions
        
        enriched_targets = []
        for t in targets:
            txns = get_transactions(t['id'])
            shares = sum(tx['shares'] for tx in txns) # Simple sum (buy + sell is -shares?)
            # Wait, get_transactions returns dictionary list?
            # Standard logic: Buy is +, Sell is -
            # Let's just pass the raw targets and let Engine handle if needed,
            # BUT Engine needs live price to know value.
            # Simplified: Use a 'shares' field if available, or just mocking for now?
            # User wants "How many stocks".
            # I will implement a quick share calculator here.
            
            total_shares = 0
            for tx in txns:
                if tx['type'] == 'buy': total_shares += tx['shares']
                elif tx['type'] == 'sell': total_shares -= tx['shares']
            
            if total_shares > 0:
                t['shares'] = total_shares
                enriched_targets.append(t)
            
        alerts = await notification_engine.generate_alerts({'targets': enriched_targets})
        return alerts
    except Exception as e:
        print(f"Notification Error: {e}")
        return []

# ---------------- AI Copilot ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API Endpoints ----------------

from pydantic import BaseModel

class LogMessage(BaseModel):
    level: str
    message: str
    stack: str | None = None

@app.post("/api/log")
async def client_log(log: LogMessage):
    print(f"CLIENT_ERROR: [{log.level}] {log.message}\nStack: {log.stack}")
    return {"status": "ok"}

# ---------------- AI Copilot ----------------
import google.generativeai as genai

class ChatRequest(BaseModel):
    message: str
    context: str # Portfolio summary
    apiKey: str
    isPremium: bool = False

# System Prompts
PROMPT_FREE = (
    "You are Mars AI (Free Tier), an investment educator designed to build CONFIDENCE. "
    "Your Goal: Explain WHY the 'Mars Strategy' (Buying Top 50 Past Performers & Holding) works. "
    "Key Traits: Encouraging, Patient, Educational. "
    "Evidence to Cite: Use the 'Bar Chart Race' (BCR) and historical 'CAGR' as proof that long-term leaders win. "
    "If the user is anxious about volatility, remind them: 'History shows the Top 50 recover. Hold forever.' "
    "Restriction: Do NOT give specific rebalancing advice. Focus on the philosophy."
)

PROMPT_PREMIUM = (
    "You are Mars AI (Premium Tier), a ruthless wealth manager designed to enforce DISCIPLINE. "
    "Your Goal: Optimize returns through active REBALANCING. "
    "Key Traits: Precise, Data-Driven, Action-Oriented. "
    "Focus: Monitor 'SMA Divergence' and 'Market Cap Ratios'. "
    "If the user asks about a stock, analyze if it is still a 'Top 50' leader. "
    "If a stock is overheated (+20% vs SMA), strongly suggest selling to rebalance. "
    "Command: 'Execute the strategy. Don't fall in love with a stock.'"
)

@app.post("/api/chat")
async def chat_with_mars(req: ChatRequest):
    """Chat with Mars AI Copilot"""
    if not req.apiKey:
        return JSONResponse(status_code=400, content={"error": "Missing API Key"})
    
    try:
        genai.configure(api_key=req.apiKey)
        # Use premium model if possible/configured, but for now standard flash is fine for both with different prompts
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        base_prompt = PROMPT_PREMIUM if req.isPremium else PROMPT_FREE
        
        system_prompt = (
            f"{base_prompt}\n"
            "----------------\n"
            "USER PORTFOLIO CONTEXT:\n"
            f"{req.context}"
        )
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": system_prompt},
            {"role": "model", "parts": "Understood. I am ready to serve per my tier instructions."}
        ])
        
        response = chat.send_message(req.message)
        return {"response": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

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

# ---------------- Leaderboard & Profile ----------------

class ProfileUpdate(BaseModel):
    nickname: str

@app.post("/api/auth/profile")
async def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401, detail="Unauthorized")
    from app.portfolio_db import update_user_nickname
    
    success = update_user_nickname(user['id'], data.nickname)
    if success:
        return {"status": "ok", "nickname": data.nickname}
    return {"status": "error"}

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Calculates Live Leaderboard based on Portfolio ROI."""
    from app.portfolio_db import get_leaderboard_candidates, get_all_targets_by_type, fetch_live_prices, get_target_summary
    
    candidates = get_leaderboard_candidates()
    leaderboard = []
    
    # Pre-fetch live prices for global cache (optimization)
    # in real world, we'd batch this. For now, per user is okay or simple global fetch?
    # Let's do per user for simplicity.
    
    for cand in candidates:
        if not cand.get('nickname'): continue 
        
        targets_map = get_all_targets_by_type(cand['id'])
        all_targets = targets_map['stock'] + targets_map['etf'] + targets_map['cb']
        
        if not all_targets: continue
        
        # Calculate Total ROI
        stock_ids = list(set(t['stock_id'] for t in all_targets))
        if not stock_ids: continue
        
        prices = fetch_live_prices(stock_ids)
        
        total_market_value = 0
        total_cost = 0
        
        for t in all_targets:
            price = prices.get(t['stock_id'], {}).get('price', 0)
            shares = t['total_shares']
            if shares > 0:
                total_market_value += shares * price
                summary = get_target_summary(t['id'])
                total_cost += summary['total_cost']

        if total_cost > 0:
            roi_pct = ((total_market_value - total_cost) / total_cost) * 100
        else:
            roi_pct = 0
            
        leaderboard.append({
            "nickname": cand['nickname'],
            "roi": round(roi_pct, 2),
            "picture": cand['picture'],
            "top_stock": "㊙️"
        })
        
    leaderboard.sort(key=lambda x: x['roi'], reverse=True)
    return leaderboard[:10]

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
