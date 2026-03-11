import os
import secrets
from datetime import datetime
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse

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

# Premium Privileged Users (Comma-separated emails from .env)
# These users get premium features without admin powers
PREMIUM_EMAILS = set(
    email.strip().lower()
    for email in os.getenv('PREMIUM_EMAILS', '').split(',')
    if email.strip()
)

# VIP Users (Comma-separated emails from .env)
VIP_EMAILS = set(
    email.strip().lower()
    for email in os.getenv('VIP_EMAILS', '').split(',')
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
    # 1. Check for API Key (Cron/System)
    api_key = request.headers.get('X-API-KEY')
    cron_secret = os.getenv('CRON_SECRET', 'change_me_in_prod_please')
    if api_key and api_key == cron_secret:
         return {"email": "cron@system", "is_admin": True}

    # 2. Check for User Session
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
    
    # Import config check
    from .main import COOKIE_DOMAIN
    
    # Sanitize: If referer is google auth, fallback to front
    if "accounts.google.com" in str(target) or "googleapis.com" in str(target):
         target = FRONTEND_URL
         
    # Store in session for callback
    request.session['auth_redirect_uri'] = str(target)

    # Force Redirect URI to match the Origin (Frontend vs Backend)
    # This is critical for Zeabur where we have two potential domains.
    # We decide based on where the user came from (Referer).
    
    # 1. Get potential Frontend Base URL
    frontend_base = str(FRONTEND_URL).rstrip('/')
    
    # 2. Get Referer Base URL
    referer = request.headers.get("referer", "")
    referer_base = "/".join(referer.split("/")[:3]) if referer else ""
    
    # Decision Logic
    # Always match the logic used in /auth/callback to prevent OAuth redirect_uri_mismatch errors
    # during the token exchange phase if Referer was missing or mismatched (e.g. 127.0.0.1 vs localhost).
    if frontend_base.startswith('http'):
        redirect_uri = f"{frontend_base}/auth/callback"
        print(f"[AUTH] Using Frontend URL for OAuth Redirect URI: {redirect_uri}")
    else:
        redirect_uri = str(request.url_for('auth_callback'))
        if "127.0.0.1" in redirect_uri:
            redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")
        from .main import IS_PRODUCTION
        if IS_PRODUCTION and redirect_uri.startswith("http://"):
             redirect_uri = redirect_uri.replace("http://", "https://")
        print(f"[AUTH] Using Standard Request Origin: {redirect_uri}")
    
    print(f"[AUTH] Login Redirect URI: {redirect_uri}")
    
    # Generate the OAuth Redirect Logic (populates request.session state)
    redirect_obj = await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')
    google_url = redirect_obj.headers.get("location")
    
    # DEBUG: Inspect Headers and Session
    print(f"[AUTH DEBUG] Login Request Headers: {dict(request.headers)}")
    print(f"[AUTH DEBUG] Login Request Host: {request.headers.get('host')}")
    print(f"[AUTH DEBUG] Login Request Scheme: {request.url.scheme}")

    # Set a debug cookie to test persistence explicitly
    # Use dynamic config from main.py to match SessionMiddleware settings
    from .main import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN
    redirect_obj.set_cookie(
        key="debug_persist", 
        value=f"set_at_{datetime.now().timestamp()}", 
        max_age=300, 
        secure=COOKIE_SECURE, 
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN # Match the session cookie domain
    )
    return redirect_obj

# Frontend Redirect URL
FRONTEND_URL = os.getenv('FRONTEND_URL', '/')
print(f"[AUTH DEBUG] Loaded FRONTEND_URL: {FRONTEND_URL}")

# Debug Endpoint
@router.get("/debug")
async def auth_debug(request: Request):
    """Dump config and session info for debugging"""
    from .main import IS_PRODUCTION, COOKIE_DOMAIN, IS_HTTPS
    
    # Check what the server sees
    debug_data = {
        "session": dict(request.session),
        "cookies": request.cookies,
        "headers": {
            "host": request.headers.get("host"),
            "x-forwarded-host": request.headers.get("x-forwarded-host"),
            "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
            "user-agent": request.headers.get("user-agent"),
        },
        "request_url": str(request.url),
        "config": {
            "IS_PRODUCTION": IS_PRODUCTION,
            "IS_HTTPS": IS_HTTPS,
            "COOKIE_DOMAIN": COOKIE_DOMAIN,
            "FRONTEND_URL": FRONTEND_URL
        },
        "url_for_callback": str(request.url_for('auth_callback'))
    }
    
    # Try setting a test cookie available to JS
    response = JSONResponse(debug_data)
    response.set_cookie("debug_probe", "active", domain=COOKIE_DOMAIN, samesite='lax')
    return response

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
    # The request.url_for might return the internal Backend URL (marffet-api)
    # But Google expects the public Frontend URL (marffet-app)
    base_url = str(FRONTEND_URL).rstrip('/')
    if base_url.startswith('http'):
        redirect_uri = f"{base_url}/auth/callback"
    else:
        redirect_uri = str(request.url_for('auth_callback'))
        
    print(f"[AUTH] Using Redirect URI: {redirect_uri}")

    try:
        # Pass redirect_uri explicitly to authorize_access_token (required by some providers/versions)
        # UPDATE: Authlib 1.6+ retrieves this from session state automatically if authorize_redirect had it.
        # Passing it explicitly caused "multiple values" TypeError.
        token = await oauth.google.authorize_access_token(request)
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
            from app.database import get_db
            from app.repositories import user_repo
            with get_db() as conn:
                user_repo.update_user_login(conn, user['sub'], user['email'], user['name'], user['picture'])
                # Log login activity
                user_repo.log_activity(conn, user['sub'], 'web', 'login')
        
        # RESTORE REDIRECT
        target = request.session.pop('auth_redirect_uri', FRONTEND_URL)
        print(f"[AUTH] Redirecting to: {target}")
        return RedirectResponse(url=target)
    except Exception as e:
        print(f"[AUTH] Callback Error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url=f"{FRONTEND_URL}?error=auth_failed")

def get_user_tier_by_email(conn, email: str) -> str:
    """Helper clearly evaluating precedence: GM > VIP > PREMIUM > FREE/Injected."""
    # 1. Fetch Injected DB membership
    cursor = conn.cursor()
    cursor.execute("SELECT tier, valid_until FROM user_memberships WHERE email = ?", (email,))
    membership_record = cursor.fetchone()

    is_injected_premium = False
    injected_tier = None
    if membership_record:
        try:
            from datetime import datetime
            valid_until = datetime.fromisoformat(membership_record['valid_until'])
            if valid_until > datetime.now():
                is_injected_premium = True
                injected_tier = membership_record['tier']
        except Exception as e:
            print(f"[AUTH] Error parsing membership valid_until: {e}")

    # 2. Check Static File-based Overrides
    email_clean = email.strip().lower()
    is_admin = email_clean in GM_EMAILS
    is_env_vip = email_clean in VIP_EMAILS
    is_env_premium = email_clean in PREMIUM_EMAILS

    # Calculate effective tier based on highest precedence: GM > VIP > PREMIUM > FREE
    tier_levels = {'FREE': 0, 'PREMIUM': 1, 'VIP': 2, 'GM': 3}

    # Static config tier
    static_tier = 'FREE'
    if is_admin:
        static_tier = 'GM'
    elif is_env_vip:
        static_tier = 'VIP'
    elif is_env_premium:
        static_tier = 'PREMIUM'

    # Injected config tier
    db_tier = injected_tier if is_injected_premium and injected_tier else 'FREE'

    # The effective tier is the highest of the two
    tier = static_tier if tier_levels.get(static_tier, 0) >= tier_levels.get(db_tier, 0) else db_tier
    return tier


@router.get("/me")
async def get_me(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # Checking raw session first for debug
    if 'user' in request.session:
        print(f"[AUTH] /me Check: User found in session: {request.session['user'].get('email')}")
    else:
        print("[AUTH] /me Check: No user in session.")

    user = request.session.get('user')
    if not user:
        return {"id": None}
    
    # Fetch fresh DB data (e.g. nickname)
    from app.database import get_db
    from app.repositories import user_repo
    with get_db() as conn:
        db_profile = user_repo.get_user_public_profile(conn, user['id'])
        # Use helper
        tier = get_user_tier_by_email(conn, user.get('email', ''))
        
    # Check if user is admin explicitly
    is_admin = tier == 'GM'
    
    # GM and VIP are treated as premium-capable tiers (all premium features unlocked)
    # PREMIUM tier gets a subset of premium features (defined by frontend gating)
    is_premium = tier in ['PREMIUM', 'VIP', 'GM']

    
    # GEMINI CHECK
    gemini_key = os.getenv('GEMINI_API_KEY')
    has_gemini_key = bool(gemini_key and len(gemini_key) > 5) # Basic validation
    print(f"[AUTH] Gemini Key Check: Loaded? {bool(gemini_key)}. Valid? {has_gemini_key}")
    
    # Merge DB data into session data for response
    # Handle None profile
    if not db_profile:
        db_profile = {}
    return {**user, **db_profile, "is_admin": is_admin, "is_premium": is_premium, "tier": tier, "has_gemini_key": has_gemini_key}


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
    print("[AUTH] Guest session activated")
    return {"status": "ok", "message": "Guest session activated"}


@router.get("/logout")
async def logout(request: Request, response: Response):
    """Clear the user session and redirect to the frontend."""
    user_email = request.session.get('user', {}).get('email', 'unknown')
    request.session.clear()
    print(f"[AUTH] Logged out: {user_email}")
    res = RedirectResponse(url=FRONTEND_URL)
    res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return res
