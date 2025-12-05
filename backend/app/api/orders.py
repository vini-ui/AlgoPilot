from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import get_db, Order, User, App, AppSecret
from app.api.auth import get_current_user
from app.services.session_manager import SessionManager

router = APIRouter()


@router.get("")
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order book from SmartAPI."""
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
    
    # If no client, try to restore session from app
    if not smartapi_client:
        # Get app and secrets
        app = db.query(App).filter(App.id == active_app_id).first()
        if app:
            secrets = db.query(AppSecret).filter(AppSecret.app_id == active_app_id).first()
            if secrets:
                # Try to restore session (will check token validity and refresh if needed)
                restored = await session_manager.restore_session(active_app_id, app, secrets)
                if restored:
                    smartapi_client = session_manager.get_smartapi_client()
    
    if not smartapi_client:
        raise HTTPException(
            status_code=400,
            detail="No active session found. Please switch to an app to establish a session. Go to Apps page and click 'Switch to App'."
        )
    
    # Get order book from SmartAPI
    result = await smartapi_client.get_order_book()
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to fetch order book")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    return {
        "status": True,
        "message": "SUCCESS",
        "errorcode": "",
        "data": result.get("data", [])
    }


@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details by order ID from SmartAPI."""
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
    
    # If no client, try to restore session from app
    if not smartapi_client:
        # Get app and secrets
        app = db.query(App).filter(App.id == active_app_id).first()
        if app:
            secrets = db.query(AppSecret).filter(AppSecret.app_id == active_app_id).first()
            if secrets:
                # Try to restore session (will check token validity and refresh if needed)
                restored = await session_manager.restore_session(active_app_id, app, secrets)
                if restored:
                    smartapi_client = session_manager.get_smartapi_client()
    
    if not smartapi_client:
        raise HTTPException(
            status_code=400,
            detail="No active session found. Please switch to an app to establish a session. Go to Apps page and click 'Switch to App'."
        )
    
    # Get order details from SmartAPI
    result = await smartapi_client.get_order_details(order_id)
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to fetch order details")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    return {
        "status": True,
        "message": "SUCCESS",
        "errorcode": "",
        "data": result.get("data")
    }

