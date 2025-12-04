from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.models import get_db, User, App, AppSecret
from app.api.auth import get_current_user
from app.services.session_manager import SessionManager
from app.services.smartapi_client import SmartAPIClient

router = APIRouter()


class SessionRestoreRequest(BaseModel):
    app_id: Optional[int] = None
    session: Optional[dict] = None


@router.post("")
async def get_user_profile_post(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    restore_request: Optional[SessionRestoreRequest] = Body(None)
):
    """Get user profile (POST version - supports session restoration)."""
    return await _get_user_profile_impl(current_user, db, restore_request)


@router.get("")
async def get_user_profile_get(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile (GET version)."""
    return await _get_user_profile_impl(current_user, db, None)


async def _get_user_profile_impl(
    current_user: User,
    db: Session,
    restore_request: Optional[SessionRestoreRequest]
):
    """
    Internal implementation for getting user profile.
    """
    # Get session manager and check for active session
    session_manager = SessionManager.get_instance()
    
    # Check if there's an active session in SessionManager
    active_app_id = session_manager.get_active_app_id()
    
    # If no active session, check if user has an active app set (for backward compatibility)
    if not active_app_id:
        active_app_id = getattr(current_user, "_active_app_id", None)
    
    # If still no active app, check if user has apps and try to use default
    if not active_app_id:
        user_apps = db.query(App).filter(App.user_id == current_user.id).all()
        if user_apps:
            # Try to find default app
            default_app = next((app for app in user_apps if app.is_default), None)
            if default_app:
                active_app_id = default_app.id
            else:
                # Use first app if no default
                active_app_id = user_apps[0].id
    
    if not active_app_id:
        raise HTTPException(
            status_code=400,
            detail="No active app selected. Please switch to an app first."
        )
    
    # Get SmartAPI client from session manager
    smartapi_client = session_manager.get_smartapi_client()
    
    # If no SmartAPI client, try to restore from request or use active_app_id
    if not smartapi_client:
        # Try to restore from request body if provided
        if restore_request and restore_request.session and restore_request.app_id:
            app = db.query(App).filter(App.id == restore_request.app_id, App.user_id == current_user.id).first()
            if app:
                secrets = db.query(AppSecret).filter(AppSecret.app_id == restore_request.app_id).first()
                if secrets:
                    restored = await session_manager.restore_session(
                        restore_request.app_id, app, secrets, restore_request.session
                    )
                    if restored:
                        smartapi_client = session_manager.get_smartapi_client()
        
        # If still no client, try to restore using active_app_id if we have session data
        if not smartapi_client and active_app_id:
            app = db.query(App).filter(App.id == active_app_id, App.user_id == current_user.id).first()
            if app:
                # Check if we can get session from somewhere (would need to be stored in DB or sent by frontend)
                raise HTTPException(
                    status_code=400,
                    detail="No active session. Please switch to this app again to establish a session."
                )
        
        if not smartapi_client:
            raise HTTPException(
                status_code=400,
                detail="No active session. Please switch to an app first."
            )
    
    # Get profile from SmartAPI
    profile_result = await smartapi_client.get_profile()
    
    if not profile_result.get("status"):
        error_msg = profile_result.get("message", "Failed to fetch profile")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    return profile_result


@router.get("/funds")
async def get_funds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get RMS funds information."""
    # Get session manager and check for active session
    session_manager = SessionManager.get_instance()
    
    # Check if there's an active session in SessionManager
    active_app_id = session_manager.get_active_app_id()
    
    # If no active session, check if user has an active app set (for backward compatibility)
    if not active_app_id:
        active_app_id = getattr(current_user, "_active_app_id", None)
    
    # If still no active app, check if user has apps and try to use default
    if not active_app_id:
        user_apps = db.query(App).filter(App.user_id == current_user.id).all()
        if user_apps:
            # Try to find default app
            default_app = next((app for app in user_apps if app.is_default), None)
            if default_app:
                active_app_id = default_app.id
            else:
                # Use first app if no default
                active_app_id = user_apps[0].id
    
    if not active_app_id:
        raise HTTPException(
            status_code=400,
            detail="No active app selected. Please switch to an app first."
        )
    
    # Get SmartAPI client from session manager
    smartapi_client = session_manager.get_smartapi_client()
    
    if not smartapi_client:
        raise HTTPException(
            status_code=400,
            detail="No active session. Please switch to an app first."
        )
    
    # Get funds from SmartAPI
    funds_result = await smartapi_client.get_funds()
    
    if not funds_result.get("status"):
        error_msg = funds_result.get("message", "Failed to fetch funds")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    return funds_result
