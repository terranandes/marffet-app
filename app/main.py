from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import pandas as pd
import asyncio
import os
import sys
import traceback
import numpy as np
from pathlib import Path

# Get absolute path to project root (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv()

from app.project_tw.strategies.cb import CBStrategy
from app.project_tw.calculator import ROICalculator
from app.services.notifications import NotificationEngine
from app.auth import router as auth_router, get_current_user
from app.portfolio_db import (
    get_all_targets_by_type, 
    update_user_stats, 
    get_leaderboard, 
    get_public_portfolio,
    init_db
)

# Import New Router
from app.routers.portfolio import router as portfolio_router
from app.routers.sync import router as sync_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    try:
        # 1. Initialize DB
        init_db()
        print("[Startup] Portfolio Database Initialized")
        
        # 2. Start Scheduler for Backup
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.services.backup import BackupService
        from datetime import datetime, timezone, timedelta
        
        # Explicit UTC timezone to ensure consistency on Zeabur
        scheduler = BackgroundScheduler(timezone=timezone.utc)
        
        # Schedule daily backup at 01:00 UTC (09:00 Taipei)
        # misfire_grace_time=86400 (24h): If app sleeps and wakes up, run immediately if missed.
        scheduler.add_job(BackupService.backup_db, 'cron', hour=1, minute=0, id='daily_backup', misfire_grace_time=86400)
        
        # 3. Smart Startup Check: If we missed the window due to sleep, check if backup is stale
        # We perform this check 30 seconds after startup to allow server to settle
        # We perform this check 30 seconds after startup to allow server to settle
        scheduler.add_job(
            BackupService.check_and_backup_if_needed, 
            'date', 
            run_date=datetime.now(timezone.utc) + timedelta(seconds=10),
            id='startup_backup_check'
        )
        
        # Wrapper for async prewarm function (APScheduler uses sync jobs)
        def run_annual_prewarm():
            import asyncio
            asyncio.run(BackupService.annual_prewarm_with_rebuild())
        
        # Schedule annual pre-warm refresh on Jan 1st at 02:00 UTC (10:00 Taipei)
        # This runs Cold Run first, then pushes to GitHub
        scheduler.add_job(run_annual_prewarm, 'cron', month=1, day=1, hour=2, minute=0, id='annual_prewarm', misfire_grace_time=86400)
        scheduler.start()
        app.state.scheduler = scheduler
        print("[Startup] Scheduler Started (Daily Backup + Annual Pre-warm)")
        
    except Exception as e:
        print(f"[Startup] Error initializing services: {e}")
    
    yield
    
    # Shutdown Logic
    try:
        if hasattr(app.state, 'scheduler'):
            app.state.scheduler.shutdown()
            print("[Shutdown] Scheduler Stopped")
    except: pass

app = FastAPI(title="Martian Investment System", lifespan=lifespan)

# Proxy Headers moved to bottom to enforce execution order
# (Removed from here)

# Session Middleware (Must be before CORS if using cookies, relies on correct ordering)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# Auto-detect if we're running on HTTPS based on FRONTEND_URL
FRONTEND_URL_FOR_DETECTION = os.getenv("FRONTEND_URL", "http://localhost:3000")
IS_HTTPS = FRONTEND_URL_FOR_DETECTION.startswith("https://")

# Robust HTTPS Detection for Zeabur / Production
# Robust HTTPS Detection for Zeabur / Production
IS_PRODUCTION = True 

# Auto-Example: If we see localhost in the URL, strictly disable Production mode
if "localhost" in FRONTEND_URL_FOR_DETECTION or "127.0.0.1" in FRONTEND_URL_FOR_DETECTION:
    IS_PRODUCTION = False

# OR allow explicit override
if os.getenv("dev_mode"): IS_PRODUCTION = False

# Derive Domain for Cookie
# CRITICAL: Since we are behind a Next.js Rewrite, the Host header is likely rewritten to 'martian-api'
# But the Browser is on 'martian-app'.
# We MUST explicitly set the domain to the Frontend's hostname (e.g. 'martian-app.zeabur.app')
# Otherwise, 'Domain=None' defaults to 'martian-api', and the browser ignores it.
from urllib.parse import urlparse

# Shared Simulation Cache
# Key: (start_year, principal, contribution) -> { "timestamp": float, "data": [...] }
SIM_CACHE = {}
import time

def get_domain_from_url(url):
    """Robustly extract hostname from URL, handling missing scheme."""
    if not url: return None
    try:
        if not url.startswith("http"):
            url = "https://" + url
        return urlparse(url).hostname
    except Exception as e:
        print(f"[Startup Error] Failed to parse FRONTEND_URL: {e}")
        return None

# FORCE Explicit Domain in Production
# CAUTION: For Zeabur, we have two domains: 
# 1. martian-app.zeabur.app (Next.js Frontend)
# 2. martian-api.zeabur.app (Legacy/Backend)
# If we force 'martian-app', the Legacy UI (martian-api) cannot set cookies.
# We MUST use None (Host Only) to allow both independent domains to work.
COOKIE_DOMAIN = None # get_domain_from_url(FRONTEND_URL) if IS_PRODUCTION else None

# Cookie Security Settings
# Localhost (HTTP): Secure=False, SameSite='lax' (lax allows OAuth redirects which are top-level navigations)
# Production (HTTPS): Secure=True, SameSite='none' (Required for cross-domain with Secure)
# NOTE: SameSite=none WITHOUT Secure is SILENTLY REJECTED by Chrome 80+
COOKIE_SECURE = IS_PRODUCTION
COOKIE_SAMESITE = 'none' if IS_PRODUCTION else 'lax'

print(f"[Startup] Session Config: Production={IS_PRODUCTION}, Domain={COOKIE_DOMAIN}, Secure={COOKIE_SECURE}, SameSite={COOKIE_SAMESITE}, Frontend={FRONTEND_URL_FOR_DETECTION}")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    # Revert to 'none' for maximum Cross-Site compatibility (safest with JS Redirect)
    same_site=COOKIE_SAMESITE, 
    https_only=COOKIE_SECURE, # Force Secure
    domain=COOKIE_DOMAIN, 
    max_age=60 * 60 * 24 * 7  # 7 days
)

# CORS Middleware
# In production, we MUST specify the exact frontend origin to support allow_credentials=True
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",  # Backend itself for OAuth callback
    "http://127.0.0.1:8000",
    "https://martian-app.zeabur.app",  # Hardcoded fallback for Zeabur
    "https://martian-api.zeabur.app",
    FRONTEND_URL.rstrip('/'), # e.g. https://martian-app.zeabur.app
    "https://accounts.google.com" # Sometimes needed for certain redirect flows (though usually not for CORS)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Proxy Headers (Must be added LAST to be executed FIRST/Outermost)
# Ensures Request.url.scheme is 'https' for Session and Auth
# app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"]) -> MOVED TO TOP (Line 92)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(sync_router, prefix="/api", tags=["sync"])

# ---------------- Health Check Endpoint ----------------
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "martian-backend",
        "version": "1.0.0"
    }

# ---------------- Notification Engine (Premium) ----------------
from app.engines import RuthlessManager
from app.portfolio_db import get_unread_notifications, mark_notification_read

@app.get("/api/notifications")
async def api_get_notifications(user: dict = Depends(get_current_user)):
    """
    Get unread notifications.
    Lazy Trigger: Runs RuthlessManager checks on every poll.
    """
    if not user:
        return []
    
    user_id = user['id']
    
    # 1. Lazy Trigger: Run Checks (Background logic)
    # Note: determining if we should run every time or cache?
    # RuthlessManager handles deduplication (24h cooldown), 
    # so running it often is safe but might be slightly slow if YFinance is slow.
    # Ideally should be async or stochastic (run 10% of time).
    # For now, run IT! (User wants results)
    try:
        RuthlessManager.run_checks(user_id)
    except Exception as e:
        print(f"[RuthlessManager] Error running checks: {e}")

    # 2. Return DB Notifications
    return get_unread_notifications(user_id)

@app.post("/api/notifications/{id}/read")
async def api_mark_read(id: str, user: dict = Depends(get_current_user)):
    """Mark notification as read"""
    if not user:
        return {"error": "Unauthorized"}
    user_id = user['id']
    success = mark_notification_read(id, user_id)
    return {"success": success}


# ---------------- AI Copilot ----------------

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
from google import genai

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
    # Allow empty req.apiKey if server has a default key
    has_server_key = bool(os.getenv("GEMINI_API_KEY"))
    if not req.apiKey and not has_server_key:
        return JSONResponse(status_code=400, content={"error": "Missing API Key"})
    
    try:
        from starlette.concurrency import run_in_threadpool

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

        # Helper for blocking GenAI call
        def generate_response():
            # DEBUG: Trace Key Source
            env_key = os.getenv("GEMINI_API_KEY", "")
            print(f"[DEBUG] Chat Request - Client Key Length: {len(req.apiKey) if req.apiKey else 0}")
            print(f"[DEBUG] Chat Request - Env Key Length: {len(env_key)}")
            
            # Use client key or fallback to server key
            api_key = req.apiKey or env_key
            if not api_key:
                print("[DEBUG] No API Key found in either source.")
                raise Exception("API Key required (Settings or Server Default)")
            
            print(f"[DEBUG] Using Key Source: {'CLIENT' if req.apiKey else 'SERVER'}")

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-3-flash-preview',  # Latest Gemini 3 Flash
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "model", "parts": [{"text": "Understood. I am ready to serve per my tier instructions."}]},
                    {"role": "user", "parts": [{"text": req.message}]}
                ]
            )
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
                # Fallback key logic
                api_key = req.apiKey or os.getenv("GEMINI_API_KEY")
                if not api_key: raise Exception("No API Key")

                client = genai.Client(api_key=api_key)
                for m in client.models.list():
                    methods = getattr(m, 'supported_generation_methods', []) or getattr(m, 'supported_actions', []) or []
                    if 'generateContent' in methods:
                        available_models.append(m.name)
            except Exception as e:
                print(f"List models failed: {e}")
                # If listing fails, try a hardcoded fallback list
                available_models = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']

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
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            {"role": "user", "parts": [{"text": system_prompt}]},
                            {"role": "model", "parts": [{"text": "Understood."}]},
                            {"role": "user", "parts": [{"text": req.message}]}
                        ]
                    )
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
def get_results(start_year: int = 2006, principal: float = 1_000_000, contribution: float = 60_000):
    """Return filtered results with Mars Simulation (Cached)"""
    try:
        # Check Cache
        cache_key = (start_year, principal, contribution)
        if cache_key in SIM_CACHE:
            print(f"[Mars] Serving simulation from cache for {cache_key}")
            return SIM_CACHE[cache_key]["data"]

        # Load filtered list
        SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
        df = pd.read_excel(SOURCE_FILE)
        df = df.fillna(0)
        
        # Load Prices (Optimization: Could be global, but strictly adhering to safe local load)
        PRICES_DB = {}
        import json
        current_max_year = 2026
        for year in range(start_year, current_max_year + 1):
             p_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
             if p_file.exists():
                 try:
                     with open(p_file, "r") as f: PRICES_DB[year] = json.load(f)
                 except: PRICES_DB[year] = {}
             # TPEx
             tpex_file = BASE_DIR / f"data/raw/TPEx_Market_{year}_Prices.json"
             if tpex_file.exists():
                 try:
                     with open(tpex_file, "r") as f: PRICES_DB[year].update(json.load(f))
                 except: pass

    # Run Simulation
        results = run_mars_simulation(df, PRICES_DB, DIVIDENDS_DB, start_year, principal, contribution)
        
        # Save to Cache
        SIM_CACHE[cache_key] = {
            "timestamp": time.time(),
            "data": results
        }
        
        return results
    except Exception as e:
        print(f"Error in get_results: {e}")
        return []

@app.get("/api/race-data")
def get_race_data(start_year: int = 2006, principal: float = 1_000_000, contribution: float = 60_000):
    """Return year-by-year ranking data with Generalized Share Accumulation Simulation"""
    try:
        # Check Cache first (reuse Mars Strategy result)
        cache_key = (start_year, principal, contribution)
        results = []
        
        if cache_key in SIM_CACHE:
             print(f"[Race] Reusing cached simulation for {cache_key}")
             results = SIM_CACHE[cache_key]["data"]
        else:
            # If not cached, we strictly should compute it.
            # But strictly refactoring this to call `get_results` logic is cleaner, 
            # but to minimize risk, I will duplicate the cache-miss logic but SAVE to cache.
            
            SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
            df = pd.read_excel(SOURCE_FILE)
            df = df.fillna(0) # Ensure no NaNs
            
            # Load Prices (Optimization: Could be global, but strictly adhering to safe local load)
            PRICES_DB = {}
            import json
            current_max_year = 2026
            for year in range(start_year, current_max_year + 1):
                p_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
                if p_file.exists():
                    try:
                        with open(p_file, "r") as f: PRICES_DB[year] = json.load(f)
                    except: PRICES_DB[year] = {}
                # TPEx
                tpex_file = BASE_DIR / f"data/raw/TPEx_Market_{year}_Prices.json"
                if tpex_file.exists():
                    try:
                        with open(tpex_file, "r") as f: PRICES_DB[year].update(json.load(f))
                    except: pass
    
            # Run Simulation
            results = run_mars_simulation(df, PRICES_DB, DIVIDENDS_DB, start_year, principal, contribution)
            
            # Save to Cache
            SIM_CACHE[cache_key] = {
                "timestamp": time.time(),
                "data": results
            }
        
        # Transform for Race - Flattened format for Legacy UI
        # Legacy UI expects: [{id, year, wealth, name, ...}, ...]
        flat_race_data = []
        for stock in results:
            stock_id = stock['id']
            stock_name = stock['name']
            for rec in stock['history']:
                flat_race_data.append({
                    "id": stock_id,
                    "name": stock_name,
                    "year": rec['year'],
                    "wealth": rec['value'],  # Renamed for clarity
                    "value": rec['value'],   # Also include 'value' for backward compat
                    "dividend": rec['dividend'],  # Include dividend for chart
                    "cagr": rec.get('cagr', 0),
                    "roi": 0,
                    "div_yield": 0
                })

        return flat_race_data

    except Exception as e:
        print(f"Error in get_race_data: {e}")
        traceback.print_exc()
        return []

from io import BytesIO
from fastapi.responses import StreamingResponse

@app.get("/api/export/excel")
async def api_export_excel(mode: str = "filtered", start_year: int = 2006, principal: float = 1000000, contribution: float = 60000):
    """
    Export Raw or Filtered Data as Excel (Dynamic Simulation).
    mode: 'raw' (Unfiltered) or 'filtered' (Default)
    """
    try:
        from io import BytesIO
        import pandas as pd
        import re
        
        # 1. Determine Source File (Now using 2026)
        filename_source = "stock_list_s2006e2026_unfiltered.xlsx" if mode == "raw" else "stock_list_s2006e2026_filtered.xlsx"
        source_path = BASE_DIR / "app/project_tw/references" / filename_source
        
        if not source_path.exists():
             raise HTTPException(status_code=404, detail=f"Source file not found: {filename_source}")

        df = pd.read_excel(source_path)
        df = df.fillna(0)
        
        current_max_year = 2026

        # 2. Run Simulation (to get Final Wealth / Stats aligned with UI)
        # Load Prices (Optimization: Could be global, but strictly adhering to safe local load)
        PRICES_DB = {}
        import json
        for year in range(start_year, current_max_year + 1):
             p_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
             if p_file.exists():
                 try:
                     with open(p_file, "r") as f: PRICES_DB[year] = json.load(f)
                 except: PRICES_DB[year] = {}
             # TPEx
             tpex_file = BASE_DIR / f"data/raw/TPEx_Market_{year}_Prices.json"
             if tpex_file.exists():
                 try:
                     with open(tpex_file, "r") as f: PRICES_DB[year].update(json.load(f))
                 except: pass

        race_results = run_mars_simulation(df, PRICES_DB, DIVIDENDS_DB, start_year, principal, contribution)
        
        # 3. Construct Export DataFrame
        # User wants "Aligned" data, implying the rows should show the simulation result
        # AND "Column head same with...". This implies preserving the ROI columns.
        
        # Map simulation results to a dict for easy merge
        sim_map = {}
        for r in race_results:
             sim_map[r['id']] = r
        
        # Create list for DataFrame construction
        export_rows = []
        
        # Identify relevant ROI columns for the requested range [start_year, 2026]
        # Regex to match `s2006e2007bao` style or just filter by year in name?
        # The column format matches: s<BASE>e<TARGET>bao
        # e.g. s2006e2007bao.
        # IF start_year is 2015, we might still want to show the 'bao' columns corresponding to 2015+?
        # The column name `s2006e2007bao` implies the year 2007 (or 2006-2007). 
        # Let's extract year from column name.
        
        relevant_cols = []
        for c in df.columns:
            if 'bao' in c:
                # Try extract year
                # e.g. s2006e2007bao -> 2007?
                # or just keep ALL columns if user wants "same head"?
                # "Dynamic" implies cutting off irrelevant past years.
                # Let's keep columns where year >= start_year
                try:
                    # simplistic extraction: split by 'e'
                    # s2006e2007bao -> ['s2006', '2007bao']
                    y_part = c.split('e')[1][:4] 
                    if int(y_part) >= start_year:
                        relevant_cols.append(c)
                except:
                    pass
        
        # Build rows
        for _, row in df.iterrows():
            sid = str(row['id'])
            if sid in sim_map:
                data = sim_map[sid]
                
                final_val = data.get('finalValue', 0)
                cost = data.get('totalCost', 0)
                roi = 0
                if cost > 0:
                    roi = ((final_val - cost) / cost) * 100

                # Base Info
                new_row = {
                    "id": sid,
                    "name": data['name'],
                    # summary stats
                    "Final Wealth": final_val,
                    "Total Cost": cost,
                    "Total ROI %": round(roi, 2),
                    "CAGR %": data.get('cagr_pct', 0),
                    "Yield %": 0 # Placeholder as yield is not currently tracked in top-level output
                }
                
                # Add original ROI columns (filtered by year)
                for c in relevant_cols:
                    new_row[c] = row[c]
                
                export_rows.append(new_row)
        
        df_export = pd.DataFrame(export_rows)
        
        # 4. Write to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Mars Strategy Source')
            
            # Params
            pd.DataFrame([{
                "Start Year": start_year,
                "End Year": current_max_year,
                "Principal": principal, 
                "Contribution": contribution,
                "Mode": mode
            }]).to_excel(writer, index=False, sheet_name='Parameters')
            
        output.seek(0)
        
        # Correct Filename Format: stock_list_s{start}e{end}_{mode}.xlsx
        filename = f"stock_list_s{start_year}e{current_max_year}_{mode}.xlsx"
        
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        print(f"Export Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

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
DIVIDENDS_FILE = BASE_DIR / "data/dividends_all.json"
if DIVIDENDS_FILE.exists():
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
            price_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
            start_price = 0
            end_price = 0
            
            if price_file.exists():
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


def run_mars_simulation(df, prices_db, dividends_db, start_year: int, principal: float, contribution: float):
    """
    Reusable Mars Strategy Simulation Logic.
    Returns a list of result dictionaries for each stock.
    """
    results = []
    # Identify year_cols - assuming standard format 'bao{year}e'
    # Or rely on dynamic extraction like before
    year_cols = [c for c in df.columns if 'bao' in c]
    
    for _, row in df.iterrows():
        stock_id = str(row['id'])
        
        # Simulation State for this Stock
        shares = 0
        cost = 0
        wealth = 0
        prev_wealth = 0
        wealth_trend = []
        
        # Initial Purchase at USER SELECTED Start Year
        # Try to get start price of start_year
        start_price_initial = prices_db.get(start_year, {}).get(stock_id, {}).get('start', 0)
        
        # Always initialize base wealth tracking
        cost = principal
        prev_wealth = principal
        shares = 0
        
        if start_price_initial > 0:
            shares = principal / start_price_initial
        
        # Add start_year (2006) as initial investment point in wealth_trend
        # This ensures X-axis shows 2006-2026 (21 years)
        wealth_trend.append({
            "year": start_year,
            "value": round(principal, 0),  # Initial investment value
            "dividend": 0,
            "cagr": 0
        })
        
        # To calculate CAGR/ROI properly for the final export row
        final_valid_stats = {} 

        for col in year_cols:
            try:
                year_str = col.split('e')[1][:4]
                year = int(year_str)
                
                # SKIP years before start_year
                
                # SKIP years before start_year
                if year < start_year:
                    continue
                    
                excel_roi = row[col] # Price ROI %
                
                # Fetch Price Data
                y_data = prices_db.get(year, {}).get(stock_id, {})
                start_price = y_data.get('start', 0)
                end_price = y_data.get('end', 0)
                
                if start_price > 0:
                    # If we have valid price data, use Share Accumulation Logic
                    
                    # 1. Transition from Synthetic to Real Shares if needed
                    if shares == 0:
                        shares = prev_wealth / start_price

                    # 2. Get Dividend (Cash + Stock)
                    div_info = dividends_db.get(stock_id, {}).get(str(year)) or dividends_db.get(stock_id, {}).get(year, {})
                    
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
                    
                    total_cash_in = cash_received + contribution
                    new_shares_bought = total_cash_in / avg_price
                    
                    shares += new_shares_bought
                    cost += contribution
                    
                    wealth = shares * end_price
                    
                    # 4. Calculate Effective ROI for Frontend
                    # Formula: ROI = ((Wealth_End - Contrib) / Wealth_Start) - 1
                    # Wealth_Start here is 'prev_wealth' (End of last year)
                    
                    if prev_wealth > 0:
                        effective_roi = ((wealth - contribution) / prev_wealth - 1) * 100
                    else:
                        effective_roi = excel_roi 

                    final_roi = effective_roi
                    
                    # Yield for reference
                    div_yield = (div_cash / start_price * 100)
                    
                    prev_wealth = wealth # Update for next loop

                else:
                    # Fallback to Excel Data if no detailed price JSON
                    # SYNTHETIC MODE: approximate tracking
                    final_roi = excel_roi
                    div_yield = 0
                    
                    # Apply ROI + Contribution
                    # wealth = prev * (1+r) + contrib
                    wealth = prev_wealth * (1 + final_roi/100) + contribution
                    prev_wealth = wealth
                    cost += contribution

                # Store history for frontend chart
                sim_cagr = 0
                if cost > 0 and wealth > 0:
                    years_elapsed = year - start_year + 1
                    if years_elapsed > 0:
                        sim_cagr = ((wealth / cost) ** (1 / years_elapsed) - 1) * 100

                wealth_trend.append({
                    "year": year,
                    "value": round(wealth, 0),
                    "dividend": round(div_cash * shares, 0),
                    "cagr": round(sim_cagr, 2)
                })

                if pd.notnull(final_roi) and final_roi != 0:
                    # Calculate cumulative CAGR from start_year to this year
                    years_elapsed = year - start_year + 1
                    if years_elapsed > 0:
                        cagr = ((wealth / principal) ** (1 / years_elapsed) - 1) * 100
                    else:
                        cagr = 0
                        
                    # Store stats for this year
                    stats_node = {
                        "value": round(wealth, 0),
                        "cagr": round(cagr, 2),
                    }
                    
        # End of Years Loop
        
        # Final Stats Construction
            except Exception as loop_e:
                pass

        # Final Stats Construction
        if wealth > 0:
             years_held = 2026 - start_year + 1 
             
             results.append({
                "id": stock_id,
                "name": str(row['name']),
                "finalValue": round(wealth, 0),
                "cagr_pct": round(row[f's2006e2026bao'], 2) if f's2006e2026bao' in row else 0,
                "volatility_pct": round(row['volatility'], 2) if 'volatility' in row else 0,
                "valid_years": years_held,
                "totalCost": cost,
                "history": wealth_trend
             })
    return results



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
async def analyze_portfolio_cb(user: dict = Depends(get_current_user)):
    """Analyze all CBs in user's portfolio"""
    try:
        # 1. Get all CB targets from portfolio
        user_id = user['id'] if user else "default"
        print(f"[CB DEBUG] Analyzing for User: {user_id}")
        
        portfolio_data = get_all_targets_by_type(user_id)
        cb_targets = portfolio_data.get("cb", [])
        print(f"[CB DEBUG] Found CB Targets: {len(cb_targets)} -> {[t['stock_id'] for t in cb_targets]}")
        
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
# Portfolio DB initialized in lifespan
# init_db()

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
        success = update_transaction(tx_id, data.type, data.shares, data.price, data.date)
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


# ============== ADMIN API (GM ONLY) ==============

@app.get("/api/admin/metrics")
async def get_admin_dashboard_metrics(user: dict = Depends(get_current_user)):
    """
    Get admin dashboard metrics.
    Protected: Only accessible by GM emails configured in .env
    """
    from app.auth import get_admin_user, GM_EMAILS
    from app.portfolio_db import get_admin_metrics
    
    # Check admin access
    if not user:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    
    if user.get('email') not in GM_EMAILS:
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    
    try:
        metrics = get_admin_metrics()
        return metrics
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/admin/crawl")
async def admin_trigger_crawl(
    background_tasks: BackgroundTasks, 
    key: str = Query(..., description="Access Key"),
    force: bool = Query(False, description="Force Cold Run (Clear Cache)"),
    user: dict = Depends(get_current_user)
):
    """
    Trigger Market Analysis Crawler (Background Task).
    """
    from app.auth import GM_EMAILS
    from app.services.crawler_service import CrawlerService
    
    if not user or user.get('email') not in GM_EMAILS:
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    
    # Add to background
    background_tasks.add_task(CrawlerService.run_market_analysis, force)
    
    mode = "COLD RUN (Cache Cleared)" if force else "Smart Run"
    return {"status": "accepted", "message": f"Market Analysis started in background. Mode: {mode}"}

@app.get("/api/admin/crawl/status")
async def admin_get_crawl_status(
    key: str = Query(..., description="Access Key"),
    user: dict = Depends(get_current_user)
):
    """
    Get status of the Market Analysis Crawler.
    """
    from app.auth import GM_EMAILS
    from app.services.crawler_service import CrawlerService
    
    if not user or user.get('email') not in GM_EMAILS:
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
        
    return CrawlerService.get_status()


# ---------------- User Feedback System ----------------
from app.feedback_db import (
    submit_feedback, get_all_feedback, update_feedback, 
    get_feedback_stats, get_feature_categories
)

class FeedbackSubmit(BaseModel):
    feature_category: str
    feature_name: Optional[str] = None
    feedback_type: str  # bug, suggestion, question
    message: str

@app.post("/api/feedback")
async def api_submit_feedback(data: FeedbackSubmit, user: dict = Depends(get_current_user)):
    """Submit user feedback or bug report"""
    try:
        user_id = user['id'] if user else "anonymous"
        user_email = user.get('email', '') if user else ''
        result = submit_feedback(
            user_id=user_id,
            user_email=user_email,
            category=data.feature_category,
            feature_name=data.feature_name,
            feedback_type=data.feedback_type,
            message=data.message
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/feedback")
async def api_get_feedback(status: str = None, user: dict = Depends(get_current_user)):
    """Get all feedback (GM only)"""
    if not user or not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_all_feedback(status)

@app.get("/api/feedback/stats")
async def api_feedback_stats(user: dict = Depends(get_current_user)):
    """Get feedback statistics (GM only)"""
    if not user or not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_feedback_stats()

@app.get("/api/feedback/categories")
async def api_feedback_categories():
    """Get feature categories for feedback form"""
    return get_feature_categories()

class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    agent_notes: Optional[str] = None

@app.patch("/api/feedback/{feedback_id}")
async def api_update_feedback(feedback_id: int, data: FeedbackUpdate, user: dict = Depends(get_current_user)):
    """Update feedback status (GM only)"""
    if not user or not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    return update_feedback(feedback_id, data.status, data.agent_notes)

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
# ---------------- Admin / System ----------------

@app.post("/api/admin/backup")
async def trigger_backup(user: dict = Depends(get_current_user)):
    """Trigger manual database backup to GitHub."""
    # Simple auth check - assume all logged in users can trigger for now? 
    # Or restrict to specific ID? For now, open to authenticated users as requested by PL.
    if not user: raise HTTPException(status_code=401, detail="Unauthorized")
    
    from app.services.backup import BackupService
    result = BackupService.backup_db()
    
    if result.get("status") == "success":
        return {"message": "Backup successful", "details": result}
    elif result.get("status") == "skipped":
        return {"message": "Backup skipped (missing config)", "details": result}
    else:
        raise HTTPException(status_code=500, detail=f"Backup failed: {result.get('reason')}")


@app.post("/api/admin/refresh-prewarm")
async def trigger_prewarm_refresh(background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    """Trigger pre-warm data refresh to GitHub (Background Task)."""
    from app.auth import GM_EMAILS
    
    if not user or user.get('email') not in GM_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.backup import BackupService
    
    # Run in background to prevent timeout
    async def run_bg_prewarm():
        await BackupService.annual_prewarm_with_rebuild()
        
    background_tasks.add_task(run_bg_prewarm)
    
    return {"message": "Pre-warm Rebuild & Push started in background.", "status": "accepted"}
