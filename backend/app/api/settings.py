from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models import get_db, Setting, User
from app.api.auth import get_current_user

router = APIRouter()


class SettingsUpdate(BaseModel):
    paper_mode: Optional[bool] = None
    default_lot_size: Optional[int] = None


@router.get("")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(Setting).filter(Setting.app_id == None).all()
    result = {}
    for setting in settings:
        result[setting.key] = setting.value
    
    # Default values
    defaults = {
        "paper_mode": "false",
        "default_lot_size": "1"
    }
    
    for key, value in defaults.items():
        if key not in result:
            result[key] = value
    
    # Convert to proper types
    return {
        "paper_mode": result.get("paper_mode", "false") == "true",
        "default_lot_size": int(result.get("default_lot_size", "1"))
    }


@router.put("")
async def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if settings_data.paper_mode is not None:
        setting = db.query(Setting).filter(Setting.key == "paper_mode", Setting.app_id == None).first()
        if setting:
            setting.value = str(settings_data.paper_mode)
        else:
            setting = Setting(key="paper_mode", value=str(settings_data.paper_mode))
            db.add(setting)
    
    if settings_data.default_lot_size is not None:
        setting = db.query(Setting).filter(Setting.key == "default_lot_size", Setting.app_id == None).first()
        if setting:
            setting.value = str(settings_data.default_lot_size)
        else:
            setting = Setting(key="default_lot_size", value=str(settings_data.default_lot_size))
            db.add(setting)
    
    db.commit()
    return {"message": "Settings updated successfully"}

