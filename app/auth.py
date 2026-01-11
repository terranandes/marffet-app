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
    email.strip() 
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
        return user
    return None

# Dependency to require admin access (GM only)
async def get_admin_user(request: Request):
    """Require admin access. Returns user if authorized, raises 403 otherwise."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if user.get('email') not in GM_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    # Force account picker to allow switching accounts
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')

@router.get("/callback", name='auth_callback')
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            # Simple session storage
            request.session['user'] = {
                'id': user['sub'],
                'name': user['name'],
                'email': user['email'],
                'picture': user['picture']
            }
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
        return RedirectResponse(url='/')
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    if not user: return {"id": None}
    from .portfolio_db import get_user_public_profile
    # Fetch fresh DB data (e.g. nickname)
    db_profile = get_user_public_profile(user['id'])
    # Check if user is admin
    is_admin = user.get('email') in GM_EMAILS
    # Merge DB data into session data for response
    return {**user, **db_profile, "is_admin": is_admin}

