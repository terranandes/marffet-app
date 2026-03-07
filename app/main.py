from google import genai
from urllib.parse import urlparse
import time
from fastapi.responses import StreamingResponse
from app.feedback_db import (
    submit_feedback, get_all_feedback, update_feedback, 
    get_feedback_stats, get_feature_categories
)
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks, Response
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import asyncio
import os
import sys
import traceback
from datetime import datetime
# import numpy as np # Lazy Import
from pathlib import Path

# Get absolute path to project root (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv()

from app.project_tw.strategies.cb import CBStrategy
from app.project_tw.calculator import ROICalculator
from app.services.notifications import NotificationEngine
from app.services.market_data_provider import MarketDataProvider
from app.auth import router as auth_router, get_current_user
from app.database import get_db, init_db
from app.services import portfolio_service
from app.services import market_data_service
from app.services import calculation_service
from app.services.portfolio_service import (
    get_all_targets_by_type, 
    update_user_stats, 
    get_public_portfolio,
    get_total_dividends
)
from app.repositories import user_repo

# Import New Router
from app.routers.portfolio import router as portfolio_router
from app.routers.sync import router as sync_router
from app.routers.admin import router as admin_router
from app.routers.strategy import router as strategy_router
from app.routers.user import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic

    print("[Startup] LIFESPAN EXECUTION STARTED")
    try:
        # 1. Initialize DB
        init_db()
        print("[Startup] Portfolio Database Initialized")

        from app.services.market_data_provider import MarketDataProvider
        from app.services.market_db import init_schema
        
        # 1.5.1 Init DuckDB Schema
        init_schema()
        
        # 1.5.2 Warm Latest Price Cache (fast dashboard load)
        asyncio.create_task(asyncio.to_thread(MarketDataProvider.warm_latest_cache))
        
        global _STARTUP_RAN
        _STARTUP_RAN = True
        print("[Startup] MarketDataProvider: Background warming initiated.")
        
        # 2. Start Scheduler for Backup
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.services.backup import BackupService
        from datetime import datetime, timezone, timedelta
        
        # Explicit UTC timezone to ensure consistency on Zeabur
        scheduler = BackgroundScheduler(timezone=timezone.utc)
        
        # Schedule daily backup at 01:00 UTC (09:00 Taipei)
        # misfire_grace_time=86400 (24h): If app sleeps and wakes up, run immediately if missed.
        scheduler.add_job(BackupService.backup_db, 'cron', hour=1, minute=0, id='daily_backup', misfire_grace_time=3600)
        
        # 3. Smart Startup Check: If we missed the window due to sleep, check if backup is stale
        # We perform this check 30 seconds after startup to allow server to settle
        # We perform this check 30 seconds after startup to allow server to settle
        scheduler.add_job(
            BackupService.check_and_backup_if_needed, 
            'date', 
            run_date=datetime.now(timezone.utc) + timedelta(seconds=10),
            id='startup_backup_check'
        )
        
        # NOTE: Heavy jobs (annual prewarm, quarterly sync) are now handled by
        # external cron scripts in scripts/cron/ to avoid blocking the web process.
        # See: scripts/cron/annual_prewarm.sh, scripts/cron/quarterly_dividend_sync.sh

        scheduler.start()
        app.state.scheduler = scheduler
        print("[Startup] Scheduler Started (Daily Backup only - heavy jobs use external cron)")
        
        # 1.5.3 Pre-calculate Mars Strategy default params into SIM_CACHE
        async def warm_mars_cache():
            try:
                # Wait for MarketDataProvider to finish warming prices somewhat
                await asyncio.sleep(5)
                print("[Startup] Warming Mars Strategy Cache (2006, 1M, 60k)...")
                from app.services.strategy_service import MarsStrategy
                import pandas as pd
                strategy = MarsStrategy()
                
                raw_results = await strategy.analyze(
                    stock_ids=["ALL"],
                    start_year=2006,
                    principal=1_000_000,
                    contribution=60_000
                )
                
                # Fetch Names
                SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
                name_map = {}
                if SOURCE_FILE.exists():
                    try:
                        name_df = pd.read_excel(SOURCE_FILE)
                        for _, row in name_df.iterrows():
                            name_map[str(row['id'])] = row['name']
                    except Exception:
                        pass
                
                sim_results = []
                for res in raw_results:
                    sid = str(res['stock_code'])
                    res['id'] = sid
                    res['name'] = name_map.get(sid, res.get('stock_name', sid))
                    res['valid_years'] = res.get('valid_lasting_years', 0)
                    sim_results.append(res)
                
                sim_results = sanitize_for_json(sim_results)
                
                cache_key = (2006, 1_000_000, 60_000)
                SIM_CACHE[cache_key] = {
                    "timestamp": time.time(),
                    "data": sim_results
                }
                print(f"[Startup] Mars Strategy Cache Warmed successfully ({len(sim_results)} items).")
            except Exception as e:
                print(f"[Startup Error] Failed to warm Mars cache: {e}")
                
        # To avoid OOM bootloop on Zeabur (512MB RAM limit), only pre-warm locally or on stronger instances.
        if os.getenv("ZEABUR_ENVIRONMENT_NAME") is None and os.getenv("ENVIRONMENT") != "production":
            asyncio.create_task(warm_mars_cache())
        else:
            print("[Startup] Skipping Mars Cache Warm-up defensively due to Remote Environment constraints.")
        
    except BaseException as e:
        print(f"[Startup] Error initializing services: {e}")
    
    yield
    
    # Shutdown Logic
    try:
        if hasattr(app.state, 'scheduler'):
            app.state.scheduler.shutdown()
            print("[Shutdown] Scheduler Stopped")
    except Exception:
        pass

_STARTUP_RAN = False  # Flag to track lifespan startup execution

app = FastAPI(title="Marffet Investment System", lifespan=lifespan)

# Health Check (no auth, no deps — if this responds, the app is alive)
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "startup_ran": _STARTUP_RAN}

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
if os.getenv("dev_mode"):
    IS_PRODUCTION = False

# Derive Domain for Cookie
# CRITICAL: Since we are behind a Next.js Rewrite, the Host header is likely rewritten to 'marffet-api'
# But the Browser is on 'marffet-app'.
# We MUST explicitly set the domain to the Frontend's hostname (e.g. 'marffet-app.zeabur.app')
# Otherwise, 'Domain=None' defaults to 'marffet-api', and the browser ignores it.


# Shared Simulation Cache
# Key: (start_year, principal, contribution) -> { "timestamp": float, "data": [...] }
SIM_CACHE = {}


def get_domain_from_url(url):
    """Robustly extract hostname from URL, handling missing scheme."""
    if not url:
        return None
    try:
        if not url.startswith("http"):
            url = "https://" + url
        return urlparse(url).hostname
    except Exception as e:
        print(f"[Startup Error] Failed to parse FRONTEND_URL: {e}")
        return None

# FORCE Explicit Domain in Production
# CAUTION: For Zeabur, we have two domains: 
# 1. marffet-app.zeabur.app (Next.js Frontend)
# 2. marffet-api.zeabur.app (Legacy/Backend)
# If we force 'marffet-app', the Legacy UI (marffet-api) cannot set cookies.
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
    "https://marffet-app.zeabur.app",  # Hardcoded fallback for Zeabur
    "https://marffet-api.zeabur.app",
    FRONTEND_URL.rstrip('/'), # e.g. https://marffet-app.zeabur.app
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
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(sync_router, prefix="/api", tags=["sync"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(strategy_router, prefix="/api/strategy", tags=["strategy"])
app.include_router(user_router, prefix="/api/user", tags=["user"])

# ---------------- Health Check Endpoint ----------------
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "marffet-backend",
        "version": "1.0.2"  # Build marker
    }

@app.get("/api/health/cache")
async def health_cache():
    """Check status of MarketDataProvider."""
    from app.services.market_data_provider import MarketDataProvider
    stats = MarketDataProvider.get_stats()
    
    return {
        "ready": stats.get('price_rows', 0) > 0,
        "stats": stats,
        "status": "ready" if stats.get('price_rows', 0) > 0 else "loading/empty"
    }

# ---------------- Debug Endpoint (Temporary) ----------------

@app.get("/api/debug/cache-info")
async def debug_cache_info():
    """Temporary debug endpoint to inspect DuckDB on Zeabur."""
    from app.services.market_data_provider import MarketDataProvider
    from app.services.market_db import DB_PATH
    
    return {
        "build": "1.2.0-duckdb-persistent",
        "startup_ran": _STARTUP_RAN,
        "duckdb_path": str(DB_PATH),
        "duckdb_exists": DB_PATH.exists(),
        "duckdb_size_mb": round(DB_PATH.stat().st_size / (1024*1024), 2) if DB_PATH.exists() else 0,
        "stats": MarketDataProvider.get_stats()
    }

# ---------------- Notification Engine (Premium) ----------------

# Notifications moved to app/routers/notifications.py if exists, or handled in user router.
# (Leaving these for now if they are used by frontend at these paths)
# But moving Admin/System triggers to admin router.


# ---------------- AI Copilot ----------------

# ---------------- API Endpoints ----------------


class LogMessage(BaseModel):
    level: str
    message: str
    stack: str | None = None

@app.post("/api/log")
async def client_log(log: LogMessage):
    print(f"CLIENT_ERROR: [{log.level}] {log.message}\nStack: {log.stack}")
    return {"status": "ok"}

# ---------------- AI Copilot ----------------


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
    "Your Goal: Optimize returns using the 'MoneyCome' methodology (CAGR & Volatility). "
    "Key Traits: Precise, Data-Driven, Action-Oriented. "
    "Strategy: The 'Mars Strategy' buys the Top 50 past performers. "
    "Context Usage: Analyze the provided 'USER PORTFOLIO CONTEXT' which contains 'MarketCache' verified data. "
    "Focus: "
    "1. **CAGR Truth**: Use the historical CAGR to validate long-term winners. "
    "2. **Volatility Control**: Monitor Standard Deviation (volatility_pct). "
    "3. **Rebalancing**: If a stock is overheated (+20% vs SMA) or drops out of the Top 50, strongly suggest selling. "
    "Command: 'Execute the strategy. Trust the math. Don't fall in love with a stock.'"
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
                model='gemini-2.5-flash',  # Stable model (2.0-flash deprecated for new keys)
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
                if not api_key:
                    raise Exception("No API Key")

                client = genai.Client(api_key=api_key)
                for m in client.models.list():
                    methods = getattr(m, 'supported_generation_methods', []) or getattr(m, 'supported_actions', []) or []
                    if 'generateContent' in methods:
                        available_models.append(m.name)
            except Exception as e:
                print(f"List models failed: {e}")
                # If listing fails, try a hardcoded fallback list
                available_models = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro']

            print(f"Available models for key: {available_models}")
            
            # Build Candidate List based on priorities (Pro > Flash)
            candidates = []
            priorities = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.5-flash-lite']
            
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
async def get_results(start_year: int = 2006, principal: float = 1_000_000, contribution: float = 60_000):
    """Return filtered results with Mars Simulation (Optimized & Async)"""
    if start_year < 2000:
        return JSONResponse(status_code=400, content={"error": "start_year must be >= 2000"})
    try:
        # Check Cache
        cache_key = (start_year, principal, contribution)
        if cache_key in SIM_CACHE:
            return SIM_CACHE[cache_key]["data"]

        from app.services.strategy_service import MarsStrategy
        strategy = MarsStrategy()
        
        # MarsStrategy.analyze now handles ALL or specific IDs
        # For the Mars Page, we use "ALL" (filtered by the strategy's own logic)
        raw_results = await strategy.analyze(
            stock_ids=["ALL"], 
            start_year=start_year,
            principal=principal,
            contribution=contribution
        )
        
        # Map to Legacy format for Frontend Compatibility
        # Next.js expects: id, name, finalValue, totalCost, cagr_pct, history, etc.
        results = []
        
        # Load names for enrichment if needed (Strategy might just have IDs)
        import pandas as pd
        SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
        name_map = {}
        if SOURCE_FILE.exists():
            try:
                name_df = pd.read_excel(SOURCE_FILE)
                for _, row in name_df.iterrows():
                    name_map[str(row['id'])] = row['name']
            except Exception:
                pass

        for res in raw_results:
            sid = str(res['stock_code'])
            res['id'] = sid
            res['name'] = name_map.get(sid, res.get('stock_name', sid))
            res['valid_years'] = res.get('valid_lasting_years', 0)
            results.append(res)
            
        # Sanitize and Cache
        results = sanitize_for_json(results)
        
        # Prevent memory leak by limiting cache size
        if len(SIM_CACHE) > 100:
            SIM_CACHE.clear()
            
        SIM_CACHE[cache_key] = {
            "timestamp": time.time(),
            "data": results
        }
        
        return results
    except Exception as e:
        print(f"Error in get_results: {e}")
        return []

@app.get("/api/results/detail")
def get_simulation_detail(stock_id: str, start_year: int = 2010, principal: float = 1_000_000, contribution: float = 60_000):
    """
    On-Demand Simulation Detail (BAO vs BAH vs BAL)
    Uses the Refactored ROICalculator (Clean Room Logic).
    CACHE ENABLED: Uses SIM_CACHE if available.
    """
    # Validate start_year (TWSE API only supports 2010+)
    if start_year < 2000:
        return JSONResponse(status_code=400, content={"error": "start_year must be >= 2000"})
    try:
        print(f"[Detail API] Request for {stock_id} ({start_year})")
        # Check Cache (Reuse if exact match)
        cache_key = f"DETAIL_{stock_id}_{start_year}_{principal}_{contribution}"
        if cache_key in SIM_CACHE:
            print(f"[Detail] Cache Hit for {stock_id}")
            return SIM_CACHE[cache_key]
        if cache_key in SIM_CACHE:
            print(f"[Detail] Cache Hit for {stock_id}")
            return SIM_CACHE[cache_key]
        from app.services.roi_calculator import ROICalculator
        import pandas as pd
        
        calc = ROICalculator()
        
        rows = []
        
        # Prepare Dataframe for ROICalculator
        # Prepare Dataframe for ROICalculator (Optimized via MarketDataProvider)
        from app.services.market_data_provider import MarketDataProvider
        history_raw = MarketDataProvider.get_daily_history(stock_id, start_date=f"{start_year}-01-01")
        
        # Transform for ROICalculator
        for h in history_raw:
            try:
                dt = datetime.strptime(h['d'], "%Y-%m-%d") if isinstance(h['d'], str) else h['d']
                rows.append({
                    'date': dt,
                    'year': dt.year,
                    'month': dt.month,
                    'open': h['o'],
                    'high': h['h'],
                    'low': h['l'],
                    'close': h['c'],
                    'volume': h['v']
                })
            except Exception:
                pass

        if not rows:
            return {"error": "No data found for stock"}

        df = pd.DataFrame(rows)
        # Use new DuckDB dividend format (all years for stock_id)
        div_data = MarketDataProvider.get_all_dividends_df(start_year)
        if hasattr(div_data, "groupby"):
            stock_divs = {}
            # filter for just this stock
            my_divs = div_data[div_data['stock_id'] == str(stock_id)]
            for _, r in my_divs.iterrows():
                stock_divs[int(r['year'])] = {'cash': float(r['cash']), 'stock': float(r['stock'])}
        else:
            stock_divs = {}

        # Apply dividend_patches.json
        import json
        from pathlib import Path
        try:
            patch_file = Path("data/dividend_patches.json")
            if patch_file.exists():
                with open(patch_file, 'r') as f:
                    patches = json.load(f)
                if str(stock_id) in patches:
                    for y_str, data in patches[str(stock_id)].items():
                        stock_divs[int(y_str)] = data
        except Exception as e:
            print(f"Error applying dividend patches: {e}")

        # Run 3 Simulations
        res_bao = calc.calculate_complex_simulation(
            df, start_year, principal, contribution, stock_divs, stock_id, buy_logic='YEAR_START_OPEN'
        )
        res_bah = calc.calculate_complex_simulation(
            df, start_year, principal, contribution, stock_divs, stock_id, buy_logic='YEAR_HIGH'
        )
        res_bal = calc.calculate_complex_simulation(
            df, start_year, principal, contribution, stock_divs, stock_id, buy_logic='YEAR_LOW'
        )
        
        result = {
            "BAO": sanitize_for_json(res_bao),
            "BAH": sanitize_for_json(res_bah),
            "BAL": sanitize_for_json(res_bal)
        }
        
        # Write to Cache
        SIM_CACHE[cache_key] = result
        return result

    except Exception as e:
        print(f"Error in detail sim: {e}")
        traceback.print_exc()
        return {"error": str(e)}

def sanitize_for_json(obj):
    """Recursively convert NaNs to None and Numpy types to Python types"""
    import math
    # import numpy as np # Lazy Import inside function
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    return obj

@app.get("/api/race-data")
async def get_race_data(start_year: int = 2006, principal: float = 1_000_000, contribution: float = 60_000):
    """Return year-by-year ranking data with Generalized Share Accumulation Simulation"""
    # Validate start_year (yfinance supports 2000+)
    if start_year < 2000:
        return JSONResponse(status_code=400, content={"error": "start_year must be >= 2000"})
    try:
        # Check Cache first (reuse Mars Strategy result)
        cache_key = (start_year, principal, contribution)
        results = []
        
        if cache_key in SIM_CACHE:
             print(f"[Race] Reusing cached simulation for {cache_key}")
             results = SIM_CACHE[cache_key]["data"]
        else:
            # Cache miss — run the FAST bulk MarsStrategy.analyze()
            from app.services.strategy_service import MarsStrategy
            strategy = MarsStrategy()
            
            raw_results = await strategy.analyze(
                stock_ids=["ALL"],
                start_year=start_year,
                principal=principal,
                contribution=contribution
            )
            
            # Load names for enrichment
            import pandas as pd
            SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
            name_map = {}
            if SOURCE_FILE.exists():
                try:
                    name_df = pd.read_excel(SOURCE_FILE)
                    for _, row in name_df.iterrows():
                        name_map[str(row['id'])] = row['name']
                except Exception:
                    pass
            
            results = []
            for res in raw_results:
                sid = str(res['stock_code'])
                res['id'] = sid
                res['name'] = name_map.get(sid, sid)
                results.append(res)
            
            results = sanitize_for_json(results)
            
            # Save to Cache
            if len(SIM_CACHE) > 100:
                SIM_CACHE.clear()
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

        return sanitize_for_json(flat_race_data)

    except Exception as e:
        print(f"Error in get_race_data: {e}")
        traceback.print_exc()
        return []



@app.get("/api/export/excel")
async def api_export_excel(mode: str = "unfiltered", start_year: int = 2006, principal: float = 1000000, contribution: float = 60000):
    """
    Export Mars Strategy results as Excel.
    Reuses SIM_CACHE from /api/results for instant response.
    mode: 'filtered' (all targets sorted by wealth) or 'unfiltered' (all targets raw order)
    All targets are always exported (no top-50 limit).
    """
    try:
        from io import BytesIO
        import pandas as pd
        
        current_max_year = datetime.now().year
        
        # 1. Get simulation results — reuse SIM_CACHE if available
        cache_key = (start_year, principal, contribution)
        if cache_key in SIM_CACHE:
            sim_results = SIM_CACHE[cache_key]["data"]
        else:
            # Cache miss — run the fast bulk MarsStrategy.analyze()
            from app.services.strategy_service import MarsStrategy
            strategy = MarsStrategy()
            raw_results = await strategy.analyze(
                stock_ids=["ALL"],
                start_year=start_year,
                principal=principal,
                contribution=contribution
            )
            
            # Load stock names
            SOURCE_FILE = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
            name_map = {}
            if SOURCE_FILE.exists():
                try:
                    name_df = pd.read_excel(SOURCE_FILE)
                    for _, row in name_df.iterrows():
                        name_map[str(row['id'])] = row['name']
                except Exception:
                    pass
            
            sim_results = []
            for res in raw_results:
                sid = str(res['stock_code'])
                res['id'] = sid
                res['name'] = name_map.get(sid, sid)
                sim_results.append(res)
            
            sim_results = sanitize_for_json(sim_results)
            
            # Cache for future use
            if len(SIM_CACHE) > 100:
                SIM_CACHE.clear()
            SIM_CACHE[cache_key] = {
                "timestamp": time.time(),
                "data": sim_results
            }
        
        # 2. Build export rows from cached results
        export_rows = []
        for data in sim_results:
            final_val = data.get('finalValue', 0)
            cost = data.get('totalCost', 0)
            roi = ((final_val - cost) / cost) * 100 if cost > 0 else 0
            
            new_row = {
                "id": data.get('id', ''),
                "name": data.get('name', ''),
                "Final Wealth": final_val,
                "Total Cost": cost,
                "Total ROI %": round(roi, 2),
                "CAGR %": data.get('cagr_pct', 0),
                "Volatility %": data.get('volatility_pct', 0),
                "Price": data.get('price', 0),
            }
            
            # Add per-year CAGR columns (s2006e2007bao, etc.)
            for k, v in data.items():
                if k.startswith('s') and 'bao' in k:
                    new_row[k] = v
            
            export_rows.append(new_row)
        
        # 3. Apply mode filter
        if mode == "filtered":
            # Sort by Final Wealth descending (all targets)
            export_rows.sort(key=lambda x: x.get('Final Wealth', 0), reverse=True)
        # mode == "unfiltered": keep raw order, export all
        
        df_export = pd.DataFrame(export_rows)
        
        # 4. Write to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Mars Strategy')
            
            pd.DataFrame([{
                "Start Year": start_year,
                "End Year": current_max_year,
                "Principal": principal,
                "Contribution": contribution,
                "Mode": mode,
                "Stocks": len(export_rows)
            }]).to_excel(writer, index=False, sheet_name='Parameters')
            
        output.seek(0)
        
        filename = f"stock_list_s{start_year}e{current_max_year}_{mode}.xlsx"
        
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        print(f"Export Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# Dividends are now loaded from DuckDB via MarketDataProvider.load_dividends_dict()
# Legacy DIVIDENDS_DB (hardcoded + dividends_all.json) has been retired.
# See: scripts/ops/reimport_twse_dividends.py to populate DuckDB dividends table.


@app.get("/api/stock/{stock_id}/history")
def get_stock_history(stock_id: str):
    """Return detailed yearly history for simulation (Prices + Dividends)"""
    from app.services.market_data_provider import MarketDataProvider
    history = []
    
    try:
        # Convert Stock ID to string key
        sid = str(stock_id)
        
        # Get latest stats to know timeframe? Or just iterate.
        # For simplify, we call a new provider method or reuse get_daily_history
        # This endpoint is mostly for a legacy detailed view.
        daily_history = MarketDataProvider.get_daily_history(sid)
        if not daily_history:
            return []
        
        # Group by year to get yearly summary (mimicking MarketCache behavior)
        import pandas as pd
        df = pd.DataFrame(daily_history)
        df['year'] = pd.to_datetime(df['d']).dt.year
        
        yearly = df.groupby('year').agg({'o': 'first', 'c': 'last'}).reset_index()
        
        for _, row in yearly.iterrows():
            year = int(row['year'])
            # Get Dividend using Generalized DB
            _divs = MarketDataProvider.load_dividends_dict()
            div_info = _divs.get(sid, {}).get(str(year)) or _divs.get(sid, {}).get(year, {})
            
            div_cash = 0
            stock_split = 1.0
            if isinstance(div_info, dict):
                div_cash = div_info.get('cash', 0)
                stock_split = div_info.get('stock_split', 1.0)
            elif isinstance(div_info, (int, float)):
                div_cash = div_info
            
            history.append({
                "year": year,
                "price_start": row['o'],
                "price_end": row['c'],
                "div_cash": div_cash,
                "stock_div": stock_split
            })
        
        return history
    except Exception as e:
        return {"error": str(e)}


def run_mars_simulation(df, prices_db, dividends_db, start_year: int, principal: float, contribution: float):
    """
    Reusable Mars Strategy Simulation Logic.
    Returns a list of result dictionaries for each stock.
    REFACTORED: Now uses the detailed ROICalculator for precision alignment.
    """
    import pandas as pd
    
    
    # MarketDataProvider is now a top-level import
    
    print(f"[run_mars_simulation] Starting Precision Engine for {len(df)} stocks...")
    t_start = time.time()
    
    calc = ROICalculator()
    results = []
    
    for _, row in df.iterrows():
        stock_id = str(row['id'])
        
        # 1. Fetch History using DuckDB
        history_raw = MarketDataProvider.get_daily_history(stock_id)
        if not history_raw:
            continue
            
        history_rows = []
        for h in history_raw:
            try:
                dt = datetime.strptime(h['d'], "%Y-%m-%d") if isinstance(h['d'], str) else h['d']
                history_rows.append({
                    'date': dt,
                    'year': dt.year,
                    'month': dt.month,
                    'open': h['o'],
                    'high': h['h'],
                    'low': h['l'],
                    'close': h['c'],
                    'volume': h['v']
                })
            except Exception:
                pass

        if not history_rows:
            continue
            
        stock_df = pd.DataFrame(history_rows)
            
        # 2. Run Precision Calculation (BAO - Buy At Open)
        div_data = dividends_db.get(stock_id, {})
        
        sim_res = calc.calculate_complex_simulation(
            stock_df, 
            start_year, 
            principal, 
            annual_investment=contribution, 
            dividend_data=div_data, 
            stock_code=stock_id, 
            buy_logic='FIRST_CLOSE'
        )
        
        if not sim_res:
            continue
            
        # 3. Format Output
        final_val = sim_res.get('finalValue', 0)
        total_cost = sim_res.get('totalCost', 0)
        hist_list = sim_res.get('history', [])
        
        res_entry = {
            "id": stock_id,
            "name": row['name'],
            "finalValue": final_val,
            "totalCost": total_cost,
            "cagr_pct": 0,
            "history": hist_list
        }
        
        # Copy simulated CAGR keys
        for k, v in sim_res.items():
            if k.startswith('s') and 'bao' in k:
                res_entry[k] = v
                
        # Fill global CAGR for sorting
        if hist_list:
             # Try to find last available cagr in history if present (from our modified ROICalculator)
             last = hist_list[-1]
             if 'cagr' in last:
                 res_entry['cagr_pct'] = last['cagr']
            
        results.append(res_entry)

    t_end = time.time()
    print(f"[run_mars_simulation] Completed in {t_end - t_start:.2f}s. Processed {len(results)} stocks.")
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
# NOTE: Portfolio DB refactored. Imports now from services/repositories.
# Legacy import block removed. Functions imported at top of file or inline.

# Initialize portfolio DB on startup
# Portfolio DB initialized in lifespan
# init_db()

# ---------------- Leaderboard & Profile ----------------

class ProfileUpdate(BaseModel):
    nickname: str

@app.post("/api/auth/profile")
async def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    with get_db() as conn:
        success = user_repo.update_user_nickname(conn, user['id'], data.nickname)
    if success:
        return {"status": "ok", "nickname": data.nickname}
    return {"status": "error"}

@app.get("/api/public/profile/{user_id}")
async def get_public_profile_api(user_id: str):
    """Get sanitized public profile data for any user"""
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
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    
    result = update_user_stats(user['id'])
    if not result:
        return JSONResponse(status_code=500, content={"error": "Failed to sync stats"})
    return result

@app.get("/api/leaderboard")
async def fetch_leaderboard(limit: int = 50):
    """Get public leaderboard from cached stats"""
    with get_db() as conn:
        return user_repo.get_leaderboard(conn, limit)

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
        return portfolio_service.list_groups(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/groups")
def api_create_group(data: GroupCreate, user: dict = Depends(get_current_user)):
    """Create a new portfolio group"""
    try:
        # Require login for creating groups? Or allow default?
        # User requested isolation, so we should likely require login or default to "default"
        user_id = user['id'] if user else "default"
        return portfolio_service.create_group(data.name, user_id)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/groups/{group_id}")
def api_delete_group(group_id: str, user: dict = Depends(get_current_user)):
    """Delete a portfolio group"""
    # TODO: Check ownership
    try:
        success = portfolio_service.delete_group(group_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Targets
@app.get("/api/portfolio/groups/{group_id}/targets")
def api_list_targets(group_id: str):
    """List targets in a group"""
    try:
        return portfolio_service.list_targets(group_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/groups/{group_id}/targets")
def api_add_target(group_id: str, data: TargetCreate):
    """Add a target (stock/ETF) to a group"""
    try:
        return portfolio_service.add_target(group_id, data.stock_id, data.stock_name, data.asset_type or "stock")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/targets/{target_id}")
def api_delete_target(target_id: str):
    """Delete a target"""
    try:
        success = portfolio_service.delete_target(target_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Transactions
@app.get("/api/portfolio/targets/{target_id}/transactions")
def api_list_transactions(target_id: str):
    """List transactions for a target"""
    try:
        return portfolio_service.list_transactions(target_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/portfolio/targets/{target_id}/transactions")
def api_add_transaction(target_id: str, data: TransactionCreate):
    """Add a transaction"""
    try:
        return portfolio_service.add_transaction(target_id, data.type, data.shares, data.price, data.date)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.put("/api/portfolio/transactions/{tx_id}")
def api_update_transaction(tx_id: str, data: TransactionCreate):
    """Update a transaction"""
    try:
        from app.services.portfolio_service import update_transaction
        success = update_transaction(tx_id, data.type, data.shares, data.price, data.date)
        return {"updated": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/api/portfolio/transactions/{tx_id}")
def api_delete_transaction(tx_id: str):
    """Delete a transaction"""
    try:
        success = portfolio_service.delete_transaction(tx_id)
        return {"deleted": success}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Summary
@app.get("/api/portfolio/targets/{target_id}/summary")
def api_target_summary(target_id: str, current_price: Optional[float] = None):
    """Get P/L summary for a target"""
    try:
        return calculation_service.get_target_summary(target_id, current_price)
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
        return market_data_service.fetch_live_prices(ids)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Trend Dashboard Endpoints
@app.get("/api/portfolio/trend")
def api_portfolio_trend(months: int = 12, user: dict = Depends(get_current_user)):
    """Get monthly portfolio cost history for trend chart"""
    try:
        user_id = user['id'] if user else "default"
        return calculation_service.get_portfolio_history(user_id=user_id, months=months)
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
        return calculation_service.get_portfolio_race_data(user_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



# Notifications

@app.get("/api/notifications")
async def get_notifications(user: dict = Depends(get_current_user)):
    """Get active alerts for the user's portfolio"""
    try:
        user_id = user['id'] if user else "default"
        # 1. Fetch Portfolio Data
        targets_by_type = get_all_targets_by_type(user_id)
        all_targets = []
        for type_list in targets_by_type.values():
            all_targets.extend(type_list)
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
    from app.auth import GM_EMAILS
    from app.database import get_db
    
    # Check admin access
    if not user:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    
    if user.get('email') not in GM_EMAILS:
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    
    try:
        with get_db() as conn:
            from app.auth import GM_EMAILS, PREMIUM_EMAILS, VIP_EMAILS
            metrics = user_repo.get_admin_metrics(conn, gm_emails=GM_EMAILS, premium_emails=PREMIUM_EMAILS, vip_emails=VIP_EMAILS)
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


@app.get("/")
async def root():
    return JSONResponse({"status": "ok", "service": "Marffet API", "docs": "/docs"})

# Startup event removed - Logic moved to lifespan context manager at top of file


if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to make it accessible if needed, or 127.0.0.1 for local
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
# ---------------- Admin / System Endpoints Moved to routers/admin.py ----------------
# manual_initialize, trigger_backup, trigger_prewarm_refresh are now in admin router.

