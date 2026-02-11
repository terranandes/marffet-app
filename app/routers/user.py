from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

from app.auth import get_current_user
from app.database import get_db
from app.repositories import user_repo

router = APIRouter()

class UserSettingsInput(BaseModel):
    settings: Dict[str, Any]
    apiKey: Optional[str] = None 

@router.get("/settings")
async def get_settings(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    with get_db() as conn:
        data = user_repo.get_user_settings(conn, user['id'])
        
    if not data:
        # Default: Return current state if possible? 
        # But if no row, means settings is null.
        return {"settings": {}, "apiKey": None}
    
    # Parse settings JSON
    settings_obj = {}
    if data.get('settings'):
        try:
            settings_obj = json.loads(data['settings'])
        except:
            settings_obj = {}
            
    return {
        "settings": settings_obj,
        "apiKey": data.get('api_key')
    }

@router.post("/settings")
async def save_settings(input: UserSettingsInput, user: dict = Depends(get_current_user)):
    """
    Save user preferences and API Key.
    - settings: JSON object (Generic preferences)
    - apiKey: Optional string. If provided, updates key. If omitted/null, leaves unchanged. If "", clears it.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    settings_json = json.dumps(input.settings)
    
    with get_db() as conn:
        # Check if row exists? update_user_login ensures users exist upon login.
        success = user_repo.update_user_settings(conn, user['id'], settings_json, input.apiKey)
        
    if not success:
        return {"status": "error", "message": "Failed to update settings"}
        
    return {"status": "ok", "settings": input.settings, "apiKey": input.apiKey}
