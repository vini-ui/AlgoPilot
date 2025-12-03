from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.models import get_db, App, AppSecret, User
from app.api.auth import get_current_user
from app.services.session_manager import SessionManager

router = APIRouter()


class AppCreate(BaseModel):
    name: str
    account_id: str  # Client ID (Angel One Client Code)
    api_key: str  # SmartAPI API Key
    secret_key: str  # SmartAPI Secret Key
    mpin: str  # Angel One MPIN (Mobile Personal Identification Number)
    base_url: str = "https://apiconnect.angelbroking.com"  # SmartAPI base URL
    is_default: bool = False  # Whether this app should be set as default


class AppResponse(BaseModel):
    id: int
    name: str
    account_id: str
    is_default: bool
    status: str
    created_at: str
    base_url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[AppResponse])
async def list_apps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(App).filter(App.user_id == current_user.id).all()
    result = []
    for app in apps:
        # Get base_url from AppSecret if it exists
        secret = db.query(AppSecret).filter(AppSecret.app_id == app.id).first()
        base_url = secret.base_url if secret and secret.base_url else "https://apiconnect.angelbroking.com"
        result.append({
            "id": app.id,
            "name": app.name,
            "account_id": app.account_id,
            "is_default": app.is_default,
            "status": "active" if app.id == getattr(current_user, "_active_app_id", None) else "inactive",
            "created_at": app.created_at.isoformat() if app.created_at else "",
            "base_url": base_url
        })
    return result


@router.post("", response_model=AppResponse)
async def create_app(
    app_data: AppCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # If this is set as default, unset other defaults
    if app_data.is_default:
        db.query(App).filter(App.user_id == current_user.id).update({"is_default": False})
    
    # Create the app
    new_app = App(
        user_id=current_user.id,
        name=app_data.name,
        account_id=app_data.account_id,
        is_default=app_data.is_default
    )
    db.add(new_app)
    db.flush()  # Flush to get the app.id
    
    # TODO: Encrypt credentials using device key derived from master password
    # For now, storing as plaintext (NOT SECURE - needs encryption implementation)
    # In production, use AES-GCM encryption with PBKDF2 key derivation
    new_secret = AppSecret(
        app_id=new_app.id,
        api_key=app_data.api_key,  # Should be encrypted
        secret_key=app_data.secret_key,  # Should be encrypted
        mpin=app_data.mpin,  # Should be encrypted
        base_url=app_data.base_url
    )
    db.add(new_secret)
    db.commit()
    db.refresh(new_app)
    
    return {
        "id": new_app.id,
        "name": new_app.name,
        "account_id": new_app.account_id,
        "is_default": new_app.is_default,
        "status": "inactive",
        "created_at": new_app.created_at.isoformat() if new_app.created_at else "",
        "base_url": app_data.base_url
    }


@router.put("/{app_id}", response_model=AppResponse)
async def update_app(
    app_id: int,
    app_data: AppCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id, App.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # If this is set as default, unset other defaults
    if app_data.is_default:
        db.query(App).filter(App.user_id == current_user.id, App.id != app_id).update({"is_default": False})
    
    app.name = app_data.name
    app.account_id = app_data.account_id
    app.is_default = app_data.is_default
    
    # Update secrets if they exist
    secret = db.query(AppSecret).filter(AppSecret.app_id == app_id).first()
    if secret:
        # TODO: Encrypt credentials
        secret.api_key = app_data.api_key  # Should be encrypted
        secret.secret_key = app_data.secret_key  # Should be encrypted
        secret.mpin = app_data.mpin  # Should be encrypted
        secret.base_url = app_data.base_url
    else:
        # Create new secret if it doesn't exist
        secret = AppSecret(
            app_id=app_id,
            api_key=app_data.api_key,  # Should be encrypted
            secret_key=app_data.secret_key,  # Should be encrypted
            mpin=app_data.mpin,  # Should be encrypted
            base_url=app_data.base_url
        )
        db.add(secret)
    
    db.commit()
    db.refresh(app)
    
    # Get base_url from secret
    updated_secret = db.query(AppSecret).filter(AppSecret.app_id == app_id).first()
    base_url = updated_secret.base_url if updated_secret and updated_secret.base_url else "https://apiconnect.angelbroking.com"
    
    return {
        "id": app.id,
        "name": app.name,
        "account_id": app.account_id,
        "is_default": app.is_default,
        "status": "active" if app.id == getattr(current_user, "_active_app_id", None) else "inactive",
        "created_at": app.created_at.isoformat() if app.created_at else "",
        "base_url": base_url
    }


@router.delete("/{app_id}")
async def delete_app(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id, App.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db.delete(app)
    db.commit()
    return {"message": "App deleted successfully"}


class SwitchAppRequest(BaseModel):
    totp: Optional[str] = None  # TOTP required for first login or expired sessions


@router.post("/{app_id}/switch")
async def switch_app(
    app_id: int,
    request: Optional[SwitchAppRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id, App.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Get app secrets
    secrets = db.query(AppSecret).filter(AppSecret.app_id == app_id).first()
    if not secrets:
        raise HTTPException(status_code=400, detail="App credentials not found. Please update app with API credentials.")
    
    # Deactivate current session if any
    session_manager = SessionManager.get_instance()
    if session_manager.is_active():
        await session_manager.deactivate()
    
    # Activate new session
    totp = request.totp if request else None
    result = await session_manager.activate(app_id, app, secrets, totp)
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to activate app")
        requires_totp = result.get("requires_totp", False)
        
        # Log the error for debugging
        print(f"Session activation failed: {error_msg}")
        print(f"Result: {result}")
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": error_msg,
                "requires_totp": requires_totp,
                "raw_error": str(result) if not requires_totp else None  # Include raw error for debugging
            }
        )
    
    return {
        "message": "App switched successfully",
        "app_id": app_id,
        "session": result.get("session")
    }


@router.post("/{app_id}/set-default")
async def set_default_app(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id, App.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Unset other defaults
    db.query(App).filter(App.user_id == current_user.id).update({"is_default": False})
    
    # Set this as default
    app.is_default = True
    db.commit()
    
    return {"message": "Default app set successfully"}

