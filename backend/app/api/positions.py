from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import get_db, User, App, AppSecret
from app.api.auth import get_current_user
from app.services.session_manager import SessionManager

router = APIRouter()


@router.get("")
async def list_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get positions from SmartAPI."""
    print("=" * 80)
    print("POSITIONS API ENDPOINT CALLED")
    print(f"User ID: {current_user.id}, Username: {current_user.username}")
    
    # Get session manager and check for active session
    session_manager = SessionManager.get_instance()
    print(f"SessionManager instance: {session_manager}")
    
    # Check if there's an active session in SessionManager
    active_app_id = session_manager.get_active_app_id()
    print(f"Active app ID from SessionManager: {active_app_id}")
    
    # If no active session, check if user has an active app set (for backward compatibility)
    if not active_app_id:
        active_app_id = getattr(current_user, "_active_app_id", None)
        print(f"Active app ID from user attribute: {active_app_id}")
    
    # If still no active app, check if user has apps and try to use default
    if not active_app_id:
        user_apps = db.query(App).filter(App.user_id == current_user.id).all()
        print(f"User apps found: {len(user_apps)}")
        if user_apps:
            # Try to find default app
            default_app = next((app for app in user_apps if app.is_default), None)
            if default_app:
                active_app_id = default_app.id
                print(f"Using default app: {active_app_id}")
            else:
                # Use first app if no default
                active_app_id = user_apps[0].id
                print(f"Using first app: {active_app_id}")
    
    if not active_app_id:
        print("ERROR: No active app ID found")
        raise HTTPException(
            status_code=400,
            detail="No active app selected. Please switch to an app first."
        )
    
    # Get SmartAPI client from session manager
    smartapi_client = session_manager.get_smartapi_client()
    print(f"SmartAPI client retrieved: {smartapi_client is not None}")
    
    # If no client, try to restore session from app
    if not smartapi_client:
        print("No SmartAPI client found, attempting to restore session...")
        print(f"Active app ID: {active_app_id}")
        
        # Get app and secrets
        app = db.query(App).filter(App.id == active_app_id).first()
        if app:
            secrets = db.query(AppSecret).filter(AppSecret.app_id == active_app_id).first()
            if secrets:
                # Try to restore session (will check token validity and refresh if needed)
                restored = await session_manager.restore_session(active_app_id, app, secrets, {})
                if restored:
                    print("Session restored successfully")
                    smartapi_client = session_manager.get_smartapi_client()
                else:
                    print("Failed to restore session - session may be expired")
            else:
                print("No secrets found for app")
        else:
            print("App not found")
    
    if not smartapi_client:
        print("ERROR: No SmartAPI client found after restore attempt")
        print(f"Active app ID: {active_app_id}")
        print(f"Session manager active app ID: {session_manager.get_active_app_id()}")
        print(f"Session manager is active: {session_manager.is_active()}")
        raise HTTPException(
            status_code=400,
            detail="No active session found. Please switch to an app to establish a session. Go to Apps page and click 'Switch to App'."
        )
    
    # Check if client has valid token
    if hasattr(smartapi_client, 'access_token'):
        print(f"Access token exists: {smartapi_client.access_token is not None}")
        if smartapi_client.access_token:
            print(f"Access token (first 20 chars): {smartapi_client.access_token[:20]}...")
        if hasattr(smartapi_client, 'is_token_valid'):
            is_valid = smartapi_client.is_token_valid()
            print(f"Token is valid: {is_valid}")
    
    # Get positions from SmartAPI
    try:
        print("Calling smartapi_client.get_positions()...")
        result = await smartapi_client.get_positions()
        
        # Log result for debugging
        print(f"Positions endpoint result type: {type(result)}")
        print(f"Positions endpoint result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print(f"Positions endpoint result success: {result.get('success')}")
        print(f"Positions endpoint result error: {result.get('error')}")
        print(f"Positions endpoint result data length: {len(result.get('data', [])) if isinstance(result.get('data'), list) else 'Not a list'}")
        
        if not result.get("success"):
            error_msg = result.get("error", "Failed to fetch positions")
            print(f"ERROR: Failed to fetch positions: {error_msg}")
            print(f"Full error result: {result}")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        print(f"SUCCESS: Returning {len(result.get('data', []))} positions")
        print("=" * 80)
        
        return {
            "status": True,
            "message": "SUCCESS",
            "errorcode": "",
            "data": result.get("data", [])
        }
    except HTTPException:
        print("HTTPException raised, re-raising...")
        raise
    except Exception as e:
        print(f"EXCEPTION in list_positions endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

