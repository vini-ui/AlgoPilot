from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import get_db, Order, User
from app.api.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get active app for user
    active_app_id = getattr(current_user, "_active_app_id", None)
    if not active_app_id:
        return []
    
    orders = db.query(Order).filter(Order.app_id == active_app_id).order_by(Order.created_at.desc()).limit(100).all()
    return orders

