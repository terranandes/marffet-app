import os
import secrets
from datetime import datetime
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

# Configuration (Load from Env or default for dev)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))

# GM Admin Whitelist (Comma-separated emails from .env)
GM_EMAILS = set(
    email.strip().lower() 
    for email in os.getenv('GM_EMAILS', '').split(',') 
    if email.strip()
)


router = APIRouter()
oauth = OAuth(Config(environ=os.environ))

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
else:
    print("WARNING: Google Client ID/Secret not found. Auth will not work.")

# Dependency to get current user
async def get_current_user(request: Request):
    user = request.session.get('user')
    if user:
        # Add is_admin flag for API endpoint checks
        user['is_admin'] = user.get('email', '').strip().lower() in GM_EMAILS
        return user
    return None

# Dependency to require admin access (GM only)
async def get_admin_user(request: Request):
    """Require admin access. Returns user if authorized, raises 403 otherwise."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if user.get('email', '').strip().lower() not in GM_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/login")
async def login(request: Request):
    # SMART REDIRECT: Determine where to send user after login
    # 1. 'next' query param
    # 2. 'Referer' header
    # 3. Default: FRONTEND_URL
    target = request.query_params.get("next") or request.headers.get("referer") or FRONTEND_URL
    
    # DEBUG: Inspect Headers and Session
    print(f"[AUTH DEBUG] Login Request Headers: {dict(request.headers)}")
    print(f"[AUTH DEBUG] Login Request Cookies: {request.cookies}")
    print(f"[AUTH DEBUG] Current Session BEFORE: {dict(request.session)}")

    # Sanitize: If referer is google auth, fallback to front
    if "accounts.google.com" in str(target) or "googleapis.com" in str(target):
         target = FRONTEND_URL
         
    # Store in session for callback
    request.session['auth_redirect_uri'] = str(target)

    # Force Redirect URI to match Frontend URL
    base_url = str(FRONTEND_URL).rstrip('/')
    if base_url.startswith('http'):
        redirect_uri = f"{base_url}/auth/callback"
    else:
        redirect_uri = request.url_for('auth_callback')
    
    print(f"[AUTH] Login Redirect URI: {redirect_uri}")
    
    # Generate the OAuth Redirect Logic (populates request.session state)
    redirect_obj = await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')
    google_url = redirect_obj.headers.get("location")
    
    # ITP Workaround: Instead of returning 302 directly (which Safari might strip cookies on),
    # return a 200 OK page that saves the cookie, then JS redirects.
    from fastapi.responses import HTMLResponse
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Redirecting...</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #000; color: #fff; }}
                .loader {{ border: 4px solid #333; border-top: 4px solid #fff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }}
                @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            </style>
        </head>
        <body>
            <div style="text-align:center">
                <div class="loader" style="margin:0 auto 20px"></div>
                <p>Connecting to Google...</p>
                <div id="debug" style="display:none">{google_url}</div>
            </div>
            <script>
                // Short timeout to ensure cookie is processed
                setTimeout(function() {{
                    window.location.href = "{google_url}";
                }}, 100);
            </script>
        </body>
    </html>
    """
    response = HTMLResponse(content=html_content)
    # Set a debug cookie to test persistence explicitly
    response.set_cookie(
        key="debug_persist", 
        value=f"set_at_{datetime.now().timestamp()}", 
        max_age=300, 
        secure=True, 
        samesite='none',
        domain=None # Try Host-Only for this one to compare
    )
    return response

# Frontend Redirect URL
FRONTEND_URL = os.getenv('FRONTEND_URL', '/')
print(f"[AUTH DEBUG] Loaded FRONTEND_URL: {FRONTEND_URL}")

# Debug Endpoint
@router.get("/debug")
async def auth_debug(request: Request):
    """Dump config and session info for debugging"""
    from .main import IS_PRODUCTION, COOKIE_DOMAIN, IS_HTTPS
    return {
        "session": dict(request.session),
        "cookies": request.cookies,
        "headers": dict(request.headers),
        "config": {
            "IS_PRODUCTION": IS_PRODUCTION,
            "IS_HTTPS": IS_HTTPS,
            "COOKIE_DOMAIN": COOKIE_DOMAIN,
            "FRONTEND_URL": FRONTEND_URL
        },
        "url_for_callback": str(request.url_for('auth_callback'))
    }

# --- COOKIE STICKINESS TEST ---
@router.get("/test-cookie-set")
async def test_cookie_set(request: Request):
    """Sets a test session variable and redirects."""
    request.session['test_val'] = f"hello_mobile_{datetime.now().timestamp()}"
    print(f"[COOKIE TEST] Setting session: {request.session['test_val']}")
    return RedirectResponse(url="/auth/test-cookie-check")

@router.get("/test-cookie-check")
async def test_cookie_check(request: Request):
    """Checks if the session variable survived the redirect."""
    val = request.session.get('test_val')
    print(f"[COOKIE TEST] Read session: {val}")
    if val:
        return JSONResponse({"status": "PASS", "message": "Cookie Persisted!", "value": val, "cookies": request.cookies})
    else:
        return JSONResponse({"status": "FAIL", "message": "Cookie LOST during redirect.", "cookies": request.cookies}, status_code=400)

@router.get("/callback", name='auth_callback')
async def auth_callback(request: Request):

    print("[AUTH] Callback triggered")
    print(f"[AUTH DEBUG] Callback Headers: {dict(request.headers)}")
    print(f"[AUTH DEBUG] Callback Cookies: {request.cookies}")
    print(f"[AUTH DEBUG] Session content: {dict(request.session)}")
    
    # Force Redirect URI to match Frontend URL (Critical for Zeabur+Next.js Rewrite)
    # The request.url_for might return the internal Backend URL (martian-api)
    # But Google expects the public Frontend URL (martian-app)
    base_url = str(FRONTEND_URL).rstrip('/')
    if base_url.startswith('http'):
        redirect_uri = f"{base_url}/auth/callback"
    else:
        redirect_uri = str(request.url_for('auth_callback'))
        
    print(f"[AUTH] Using Redirect URI: {redirect_uri}")

    try:
        # Pass redirect_uri explicitly to authorize_access_token (required by some providers/versions)
        token = await oauth.google.authorize_access_token(request, redirect_uri=redirect_uri)
        user = token.get('userinfo')
        print(f"[AUTH] Google User: {user.get('email')}")
        if user:
            # Simple session storage
            request.session['user'] = {
                'id': user['sub'],
                'name': user['name'],
                'email': user['email'],
                'picture': user['picture']
            }
            print("[AUTH] Session 'user' set.")
            
            # Sync user to DB using new helper
            from .portfolio_db import update_user_login
            update_user_login(user['sub'], user['email'], user['name'], user['picture'])

            # Log login activity
            from .portfolio_db import log_activity
            log_activity(user['sub'], 'web', 'login')
        
        # RESTORE REDIRECT
        target = request.session.pop('auth_redirect_uri', FRONTEND_URL)
        print(f"[AUTH] Redirecting to: {target}")
        return RedirectResponse(url=target)

    except Exception as e:
        print(f"[AUTH] Callback Error: {e}")
        # DEBUG: return session keys to identifying if cookie was lost or just mismatched
        debug_info = {
            "error": str(e), 
            "session_keys": list(request.session.keys()),
            "cookie_present": bool(request.cookies.get("session")),
            "debug_cookie": request.cookies.get("debug_persist")
        }
        return JSONResponse(status_code=400, content=debug_info)


@router.get("/logout")
async def logout(request: Request):
    # CRITICAL: Use clear() instead of pop() to ensure session is fully cleared
    request.session.clear()
    
    # "Nuclear Option": Explicitly expire the cookie on multiple plausible domains 
    # to clean up any "Zombie Cookies" (Host-Only vs Explicit Domain)
    
    # helper to add delete headers
    def nuke_cookies(resp):
        if COOKIE_DOMAIN:
            resp.delete_cookie("session", domain=COOKIE_DOMAIN)
        resp.delete_cookie("session", domain=None)
        resp.delete_cookie("session")
        return resp

    # Detect if this is an API call (fetch) or direct browser navigation
    # API calls will have Accept: application/json or similar
    accept_header = request.headers.get("accept", "")
    is_api_call = "application/json" in accept_header or "fetch" in request.headers.get("sec-fetch-mode", "")
    
    if is_api_call:
        # Return JSON for API calls (from frontend fetch)
        response = JSONResponse({"status": "ok", "message": "Logged out successfully"})
        return nuke_cookies(response)
    
    # Smart Logout Redirect for direct browser access
    response = RedirectResponse(url=FRONTEND_URL)
    return nuke_cookies(response)

@router.get("/me")
async def get_me(request: Request): 
    # Checking raw session first for debug
    if 'user' in request.session:
        print(f"[AUTH] /me Check: User found in session: {request.session['user'].get('email')}")
    else:
        print("[AUTH] /me Check: No user in session.")

    user = request.session.get('user')
    if not user: return {"id": None}
    
    from .portfolio_db import get_user_public_profile
    # Fetch fresh DB data (e.g. nickname)
    db_profile = get_user_public_profile(user['id'])
    # Check if user is admin
    is_admin = user.get('email') in GM_EMAILS
    
    # GEMINI CHECK
    gemini_key = os.getenv('GEMINI_API_KEY')
    has_gemini_key = bool(gemini_key and len(gemini_key) > 5) # Basic validation
    print(f"[AUTH] Gemini Key Check: Loaded? {bool(gemini_key)}. Valid? {has_gemini_key}")
    
    # Merge DB data into session data for response
    return {**user, **db_profile, "is_admin": is_admin, "has_gemini_key": has_gemini_key}


@router.post("/guest")
async def guest_login(request: Request):
    """Create a guest session for users who don't want to sign in."""
    request.session['user'] = {
        'id': 'guest',
        'name': 'Guest',
        'email': 'guest@local',
        'picture': None,
        'is_guest': True
    }
    print("[AUTH] Guest mode activated")
    return {"status": "ok", "message": "Guest mode activated"}
