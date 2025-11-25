from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.models import get_db, App, User
from app.api.auth import get_current_user

router = APIRouter()


class AppCreate(BaseModel):
    name: str
    account_id: str


class AppResponse(BaseModel):
    id: int
    name: str
    account_id: str
    is_default: bool
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[AppResponse])
async def list_apps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(App).filter(App.user_id == current_user.id).all()
    return [
        {
            **app.__dict__,
            "status": "active" if app.id == getattr(current_user, "_active_app_id", None) else "inactive"
        }
        for app in apps
    ]


@router.post("", response_model=AppResponse)
async def create_app(
    app_data: AppCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_app = App(
        user_id=current_user.id,
        name=app_data.name,
        account_id=app_data.account_id
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return {
        **new_app.__dict__,
        "status": "inactive"
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
    
    app.name = app_data.name
    app.account_id = app_data.account_id
    db.commit()
    db.refresh(app)
    
    return {
        **app.__dict__,
        "status": "active" if app.id == getattr(current_user, "_active_app_id", None) else "inactive"
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


@router.post("/{app_id}/switch")
async def switch_app(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id, App.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # TODO: Implement session manager activation
    # For now, just mark as active
    setattr(current_user, "_active_app_id", app_id)
    
    return {"message": "App switched successfully", "app_id": app_id}


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

