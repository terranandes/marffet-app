from fastapi import FastAPI, Depends, HTTPException
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
from app.portfolio_db import (
    get_all_targets_by_type, 
    update_user_stats, 
    get_leaderboard, 
    get_public_portfolio,
    init_db
)

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
    # If no user or user.id is None, return empty (no notifications for unauth users)
    if not user or not user.get('id'):
        return []
    user_id = user['id']
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
        from app.portfolio_db import list_transactions
        
        enriched_targets = []
        for t in targets:
            txns = list_transactions(t['id'])
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
        from starlette.concurrency import run_in_threadpool

        # Helper for blocking GenAI call
        def generate_response():
            genai.configure(api_key=req.apiKey)
            
            # Construct parameters
            base_prompt = PROMPT_PREMIUM if req.isPremium else PROMPT_FREE
            system_prompt = (
                f"{base_prompt}\n"
                "----------------\n"
                "USER PORTFOLIO CONTEXT:\n"
                f"{req.context}"
            )
            history = [
                {"role": "user", "parts": system_prompt},
                {"role": "model", "parts": "Understood. I am ready to serve per my tier instructions."}
            ]

            model = genai.GenerativeModel('gemini-1.5-pro')
            chat = model.start_chat(history=history)
            response = chat.send_message(req.message)
            return response.text

        # Run in threadpool to avoid blocking async loop
        try:
            response_text = await run_in_threadpool(generate_response)
            return {"response": response_text}
        except Exception as first_error:
            # 2. If Error (404, 429, etc.), Attempt Robust Auto-Discovery
            print(f"Default model failed ({first_error}). Attempting auto-discovery...")
            
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
            except Exception as e:
                print(f"List models failed: {e}")
                # If listing fails, try a hardcoded fallback list
                available_models = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']

            print(f"Available models for key: {available_models}")
            
            # Build Candidate List based on priorities (Pro > Flash)
            candidates = []
            priorities = ['gemini-1.5-pro', 'gemini-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
            
            # 1. Add Priority Matches
            for p in priorities:
                for avail in available_models:
                    if p in avail and avail not in candidates:
                        candidates.append(avail)
            
            # 2. Add Remaining Gemini Models
            for avail in available_models:
                if 'gemini' in avail and avail not in candidates:
                    candidates.append(avail)

            if not candidates:
                 raise Exception(f"No Gemini models found. Available: {available_models}")

            # Try Candidates One by One
            last_error = first_error
            for model_name in candidates:
                print(f"  >> Trying candidate: {model_name}...")
                try:
                    model = genai.GenerativeModel(model_name)
                    chat = model.start_chat(history=history)
                    response = chat.send_message(req.message)
                    print(f"  >> Success with {model_name}!")
                    return {"response": response.text}
                except Exception as inner_e:
                    print(f"  >> Failed {model_name}: {inner_e}")
                    last_error = inner_e
            
            # If all failed
            raise last_error

    except Exception as e:
        print(f"Gemini Error: {e}")
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

# Global Dividend Database (Cash per Share)
# Initialize with Critical Hardcoded Data (Safety Baseline)
DIVIDENDS_DB = {
    "2330": {
        2006: {'cash': 2.39}, 2007: {'cash': 2.95}, 2008: {'cash': 2.99}, 2009: {'cash': 2.98}, 2010: {'cash': 3.00},
        2011: {'cash': 3.00}, 2012: {'cash': 3.00}, 2013: {'cash': 3.00}, 2014: {'cash': 3.00}, 2015: {'cash': 4.50},
        2016: {'cash': 6.00}, 2017: {'cash': 7.00}, 2018: {'cash': 8.00}, 2019: {'cash': 12.5}, 2020: {'cash': 10.0},
        2021: {'cash': 10.5}, 2022: {'cash': 11.0}, 2023: {'cash': 11.5}, 2024: {'cash': 15.0}, 2025: {'cash': 19.0}
    },
    "5904": {
            2008: {'cash': 1.78}, 2009: {'cash': 1.80}, 2010: {'cash': 0.38}, 2011: {'cash': 2.54}, 2012: {'cash': 2.97},
            2013: {'cash': 3.79}, 2014: {'cash': 4.43}, 2015: {'cash': 6.97}, 2016: {'cash': 8.29}, 2017: {'cash': 10.29},
            2018: {'cash': 12.62}, 2019: {'cash': 15.29}, 2020: {'cash': 16.60}, 2021: {'cash': 18.16}, 2022: {'cash': 11.00},
            2023: {'cash': 24.14}, 2024: {'cash': 21.00}, 2025: {'cash': 23.00} 
    }
}

# Try to load full dataset and MERGE (Overwrite hardcoded if data exists)
import json, os
DIVIDENDS_FILE = "data/dividends_all.json"
if os.path.exists(DIVIDENDS_FILE):
    try:
        with open(DIVIDENDS_FILE, "r") as f:
            json_data = json.load(f)
            # Merge: update() adds new keys and overwrites existing ones
            DIVIDENDS_DB.update(json_data)
            # print(f"Loaded {len(json_data)} stocks from DB (Merged)")
    except Exception as e:
        print(f"Error loading dividends: {e}")


@app.get("/api/stock/{stock_id}/history")
def get_stock_history(stock_id: str):
    """Return detailed yearly history for simulation (Prices + Dividends)"""
    import json, os
    history = []
    
    try:
        # Convert Stock ID to string key
        sid = str(stock_id)
        
        for year in range(2006, 2026):
            year_str = str(year) # Keys in JSON might be strings or ints depending on saving?
            # Start/End price logic...
            price_file = f"data/raw/Market_{year}_Prices.json"
            start_price = 0
            end_price = 0
            
            if os.path.exists(price_file):
                with open(price_file, "r") as f:
                    pdata = json.load(f)
                    if sid in pdata:
                        start_price = pdata[sid].get('start', 0)
                        end_price = pdata[sid].get('end', 0)
            
            # Get Dividend using Generalized DB
            # DB Structure might be: { "2330": { "2020": { "cash": 10.0, "stock_split": 1.0 } } }
            div_info = DIVIDENDS_DB.get(sid, {}).get(year_str) or DIVIDENDS_DB.get(sid, {}).get(year, {})
            
            # Handle old structure vs new full structure
            div_cash = 0
            stock_split = 1.0
            
            if isinstance(div_info, dict):
                div_cash = div_info.get('cash', 0)
                stock_split = div_info.get('stock_split', 1.0)
            elif isinstance(div_info, (int, float)):
                div_cash = div_info # Backward compat with simple float map
            
            # Only append if we have valid price data
            if start_price > 0:
                history.append({
                    "year": year,
                    "price_start": start_price,
                    "price_end": end_price,
                    "div_cash": div_cash,
                    "stock_div": stock_split # Renamed for clarity in frontend? Or just use same?
                })
        
        return history
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/race-data")
def get_race_data(start_year: int = 2006):
    """Return year-by-year ranking data with Generalized Share Accumulation Simulation"""
    try:
        SOURCE_FILE = "project_tw/references/stock_list_s2006e2026_filtered.xlsx"
        df = pd.read_excel(SOURCE_FILE)
        df = df.fillna(0) # Ensure no NaNs
        
        # DIVIDENDS_DB is loaded globally
        
        # Pre-load ALL Price Data (Performance Optimization)
        # Structure: PRICES_DB[year][stock_id] = {'start': x, 'end': y}
        PRICES_DB = {}
        import json, os
        # Load up to current year if possible, or 2026
        for year in range(2006, 2026):
            p_file = f"data/raw/Market_{year}_Prices.json"
            if os.path.exists(p_file):
                try:
                    with open(p_file, "r") as f:
                        PRICES_DB[year] = json.load(f)
                except:
                    PRICES_DB[year] = {}
            else:
                PRICES_DB[year] = {}
                
            # Load TPEx Prices (OTC)
            tpex_file = f"data/raw/TPEx_Market_{year}_Prices.json"
            if os.path.exists(tpex_file):
                try:
                    with open(tpex_file, "r") as f:
                        tpex_data = json.load(f)
                        PRICES_DB[year].update(tpex_data)
                except:
                    pass

        race_data = []
        year_cols = [c for c in df.columns if 'bao' in c]
        
        # Filter Columns for Dynamic Start Year
        # Assumes cols are like 'bao2006e', 'bao2007e'... (Check logic below)
        # Actually logic extracts year in loop. We can just skip inside loop or pre-filter.
        
        # Simulation Parameters
        SIM_PRINCIPAL = 1_000_000
        SIM_CONTRIB = 60_000

        for _, row in df.iterrows():
            stock_id = str(row['id'])
            
            # Simulation State for this Stock
            shares = 0
            cost = 0
            wealth = 0
            prev_wealth = 0
            
            # Initial Purchase at USER SELECTED Start Year
            # Try to get start price of start_year
            start_price_initial = PRICES_DB.get(start_year, {}).get(stock_id, {}).get('start', 0)
            if start_price_initial > 0:
                shares = SIM_PRINCIPAL / start_price_initial
                cost = SIM_PRINCIPAL
                prev_wealth = SIM_PRINCIPAL
            
            for col in year_cols:
                try:
                    year_str = col.split('e')[1][:4]
                    year = int(year_str)
                    
                    # SKIP years before start_year
                    if year < start_year:
                        continue
                        
                    excel_roi = row[col] # Price ROI %
                    
                    # Fetch Price Data
                    y_data = PRICES_DB.get(year, {}).get(stock_id, {})
                    start_price = y_data.get('start', 0)
                    end_price = y_data.get('end', 0)
                    
                    if start_price > 0:
                        # If we have valid price data, use Share Accumulation Logic
                        
                        # 1. Initialize if not yet (e.g. IPO later than 2006)
                        if shares == 0 and cost == 0:
                            shares = SIM_PRINCIPAL / start_price
                            cost = SIM_PRINCIPAL
                            prev_wealth = SIM_PRINCIPAL

                        # 2. Get Dividend (Cash + Stock)
                        div_info = DIVIDENDS_DB.get(stock_id, {}).get(str(year)) or DIVIDENDS_DB.get(stock_id, {}).get(year, {})
                        
                        div_cash = 0
                        stock_split = 1.0
                        
                        if isinstance(div_info, dict):
                            div_cash = div_info.get('cash', 0)
                            stock_split = div_info.get('stock_split', 1.0)
                        elif isinstance(div_info, (int, float)):
                            div_cash = div_info

                        # 3. Process Year
                        
                        # A. Stock Dividend (Ex-Rights) - Happens usually mid-year, but we apply to held shares
                        # Shares increase by factor
                        # In TW, 1.05 means 5% stock dividend.
                        if stock_split > 1.0:
                             shares = shares * stock_split

                        # B. Cash Dividend Reinvestment
                        cash_received = shares * div_cash
                        
                        # Reinvest Dividend + Contribution at Avg Price
                        if end_price == 0:
                             end_price = start_price * (1 + excel_roi/100)
                        
                        avg_price = (start_price + end_price) / 2
                        
                        total_cash_in = cash_received + SIM_CONTRIB
                        new_shares_bought = total_cash_in / avg_price
                        
                        shares += new_shares_bought
                        cost += SIM_CONTRIB
                        
                        wealth = shares * end_price
                        
                        # 4. Calculate Effective ROI for Frontend
                        # Formula: ROI = ((Wealth_End - Contrib) / Wealth_Start) - 1
                        # Wealth_Start here is 'prev_wealth' (End of last year)
                        
                        if prev_wealth > 0:
                            effective_roi = ((wealth - SIM_CONTRIB) / prev_wealth - 1) * 100
                        else:
                            effective_roi = excel_roi 

                        final_roi = effective_roi
                        
                        # Yield for reference
                        div_yield = (div_cash / start_price * 100)
                        
                        prev_wealth = wealth # Update for next loop

                    else:
                        # Fallback to Excel Data if no detailed price JSON
                        final_roi = excel_roi
                        div_yield = 0
                        if prev_wealth > 0:
                             prev_wealth = prev_wealth * (1 + final_roi/100) + SIM_CONTRIB

                    if pd.notnull(final_roi) and final_roi != 0:
                         race_data.append({
                            "year": year,
                            "id": stock_id,
                            "name": row['name'],
                            "roi": round(final_roi, 2),
                            "value": round(wealth, 0), # Return Wealth ($) for Race/Table
                            "wealth": round(wealth, 0),
                            "div_yield": round(div_yield, 2)
                        })

                except Exception as loop_e:
                     pass
                
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
        cb_codes = [t['stock_id'] for t in cb_targets]
        
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

@app.get("/api/public/profile/{user_id}")
async def get_public_profile_api(user_id: str):
    """Get sanitized public profile data for any user"""
    from app.portfolio_db import get_public_portfolio
    try:
        data = get_public_portfolio(user_id)
        if not data:
            return JSONResponse(status_code=404, content={"error": "User not found"})
        return data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/sync-stats")
async def sync_stats(user: dict = Depends(get_current_user)):
    """Trigger update of cached wealth/ROI stats for leaderboard"""
    if not user: return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    
    from app.portfolio_db import update_user_stats
    result = update_user_stats(user['id'])
    if not result:
        return JSONResponse(status_code=500, content={"error": "Failed to sync stats"})
    return result

@app.get("/api/leaderboard")
async def fetch_leaderboard(limit: int = 50):
    """Get public leaderboard from cached stats"""
    from app.portfolio_db import get_leaderboard
    return get_leaderboard(limit)

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
def api_list_groups(user: dict = Depends(get_current_user)):
    """List all portfolio groups"""
    try:
        user_id = user['id'] if user else "default"
        return list_groups(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/groups")
def api_create_group(data: GroupCreate, user: dict = Depends(get_current_user)):
    """Create a new portfolio group"""
    try:
        # Require login for creating groups? Or allow default?
        # User requested isolation, so we should likely require login or default to "default"
        user_id = user['id'] if user else "default"
        return create_group(data.name, user_id)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/groups/{group_id}")
def api_delete_group(group_id: str, user: dict = Depends(get_current_user)):
    """Delete a portfolio group"""
    # TODO: Check ownership
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

@app.put("/api/portfolio/transactions/{tx_id}")
def api_update_transaction(tx_id: str, data: TransactionCreate):
    """Update a transaction"""
    try:
        from app.portfolio_db import update_transaction
        success = update_transaction(tx_id, data.shares, data.price, data.date)
        return {"updated": success}
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
def api_portfolio_trend(months: int = 12, user: dict = Depends(get_current_user)):
    """Get monthly portfolio cost history for trend chart"""
    try:
        user_id = user['id'] if user else "default"
        return get_portfolio_history(user_id=user_id, months=months)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/by-type")
def api_portfolio_by_type(user: dict = Depends(get_current_user)):
    """Get all targets grouped by asset type (stock/etf)"""
    try:
        user_id = user['id'] if user else "default"
        return get_all_targets_by_type(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/portfolio/race-data")
def api_portfolio_race(user: dict = Depends(get_current_user)):
    """Get race data for live portfolio BCR animation"""
    try:
        user_id = user['id'] if user else "default"
        return get_portfolio_race_data(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Dividend Tracking Endpoints
@app.post("/api/portfolio/sync-dividends")
def api_sync_dividends(user: dict = Depends(get_current_user)):
    """Sync dividends for all user's targets"""
    try:
        user_id = user['id'] if user else "default"
        result = sync_all_dividends(user_id)
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
def api_dividend_cash(user: dict = Depends(get_current_user)):
    """Get total dividend cash"""
    try:
        user_id = user['id'] if user else "default"
        return get_total_dividends(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



# Notifications

@app.get("/api/notifications")
async def get_notifications(user: dict = Depends(get_current_user)):
    """Get active alerts for the user's portfolio"""
    try:
        user_id = user['id'] if user else "default"
        # 1. Fetch Portfolio Data
        all_targets = get_all_targets_json(user_id)
        portfolio = {"targets": all_targets}
        
        # 2. Generate Alerts
        engine = NotificationEngine()
        alerts = await engine.generate_alerts(portfolio)
        
        return alerts
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

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to make it accessible if needed, or 127.0.0.1 for local
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
