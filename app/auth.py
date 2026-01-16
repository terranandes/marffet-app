import os
import secrets
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

    # Sanitize: If referer is google auth, fallback to front
    if "accounts.google.com" in str(target) or "googleapis.com" in str(target):
         target = FRONTEND_URL
         
    # Store in session for callback
    request.session['auth_redirect_uri'] = str(target)

    redirect_uri = request.url_for('auth_callback')
    # Force account picker to allow switching accounts
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')

# Frontend Redirect URL
FRONTEND_URL = os.getenv('FRONTEND_URL', '/')
print(f"[AUTH DEBUG] Loaded FRONTEND_URL: {FRONTEND_URL}")

@router.get("/callback", name='auth_callback')
async def auth_callback(request: Request):
    print("[AUTH] Callback triggered")
    print(f"[AUTH DEBUG] Session keys: {list(request.session.keys())}")
    print(f"[AUTH DEBUG] Request URL: {request.url}")
    try:
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
            
            # Sync user to DB and log activity
            from .portfolio_db import get_db, log_activity
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO users (id, email, name, picture) VALUES (?, ?, ?, ?)",
                    (user['sub'], user['email'], user['name'], user['picture'])
                )
            # Log login activity
            log_activity(user['sub'], 'web', 'login')
        
        # RESTORE REDIRECT
        target = request.session.pop('auth_redirect_uri', FRONTEND_URL)
        print(f"[AUTH] Redirecting to: {target}")
        return RedirectResponse(url=target)

    except Exception as e:
        print(f"[AUTH] Callback Error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    
    # Smart Logout Redirect
    # If user logout from Backend (direct API usage), go to Backend Root
    # If user logout from Frontend (app), go to Frontend Root
    referer = request.headers.get("referer", "")
    current_host = str(request.base_url)
    
    # If Referer contains Backend Host -> Stay on Backend Root
    if current_host.replace("https://", "").replace("http://", "").rstrip("/") in referer:
         return RedirectResponse(url='/')
    
    # Default: Go to Frontend
    return RedirectResponse(url=FRONTEND_URL)

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
    # Merge DB data into session data for response
    return {**user, **db_profile, "is_admin": is_admin}

