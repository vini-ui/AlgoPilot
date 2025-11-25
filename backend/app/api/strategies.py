from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.models import get_db, Strategy, App, User
from app.api.auth import get_current_user

router = APIRouter()


class StrategyCreate(BaseModel):
    name: str
    type: str
    params_json: Optional[str] = "{}"
    enabled: bool = False


class StrategyResponse(BaseModel):
    id: int
    app_id: int
    name: str
    type: str
    params_json: str
    enabled: bool
    status: Optional[str] = "stopped"
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[StrategyResponse])
async def list_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get active app for user
    active_app_id = getattr(current_user, "_active_app_id", None)
    if not active_app_id:
        return []
    
    strategies = db.query(Strategy).filter(Strategy.app_id == active_app_id).all()
    return [
        {
            **strategy.__dict__,
            "status": getattr(strategy, "_runtime_status", "stopped")
        }
        for strategy in strategies
    ]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {
        **strategy.__dict__,
        "status": getattr(strategy, "_runtime_status", "stopped")
    }


@router.post("", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_app_id = getattr(current_user, "_active_app_id", None)
    if not active_app_id:
        raise HTTPException(status_code=400, detail="No active app selected")
    
    new_strategy = Strategy(
        app_id=active_app_id,
        name=strategy_data.name,
        type=strategy_data.type,
        params_json=strategy_data.params_json,
        enabled=strategy_data.enabled
    )
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    return {
        **new_strategy.__dict__,
        "status": "stopped"
    }


@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # TODO: Implement actual strategy start logic
    setattr(strategy, "_runtime_status", "running")
    
    return {"message": "Strategy started", "strategy_id": strategy_id}


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # TODO: Implement actual strategy stop logic
    setattr(strategy, "_runtime_status", "stopped")
    
    return {"message": "Strategy stopped", "strategy_id": strategy_id}


@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # TODO: Implement actual strategy pause logic
    setattr(strategy, "_runtime_status", "paused")
    
    return {"message": "Strategy paused", "strategy_id": strategy_id}


@router.post("/{strategy_id}/run-now")
async def run_strategy_now(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # TODO: Implement single execution
    return {"message": "Strategy executed", "strategy_id": strategy_id}


@router.post("/start-all")
async def start_all_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_app_id = getattr(current_user, "_active_app_id", None)
    if not active_app_id:
        raise HTTPException(status_code=400, detail="No active app selected")
    
    strategies = db.query(Strategy).filter(Strategy.app_id == active_app_id).all()
    # TODO: Start all strategies
    return {"message": f"Started {len(strategies)} strategies"}


@router.post("/stop-all")
async def stop_all_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_app_id = getattr(current_user, "_active_app_id", None)
    if not active_app_id:
        raise HTTPException(status_code=400, detail="No active app selected")
    
    strategies = db.query(Strategy).filter(Strategy.app_id == active_app_id).all()
    # TODO: Stop all strategies
    return {"message": f"Stopped {len(strategies)} strategies"}


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted successfully"}

