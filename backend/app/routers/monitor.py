"""
监控路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models import MonitorTarget, MonitorLog, User
from app.routers.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


# ============ Schemas ============

class TargetCreate(BaseModel):
    name: str
    url: str
    type: str = "http"
    interval: int = 60
    timeout: int = 10


class TargetUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    interval: Optional[int] = None
    timeout: Optional[int] = None
    is_active: Optional[bool] = None


class TargetResponse(BaseModel):
    id: int
    name: str
    url: str
    type: str
    interval: int
    status: str
    uptime: float
    response_time: float
    last_check: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class LogResponse(BaseModel):
    id: int
    target_id: int
    status: str
    response_time: float
    status_code: int
    error: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Endpoints ============

@router.get("/targets", response_model=List[TargetResponse])
async def list_targets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的所有监控目标"""
    return db.query(MonitorTarget).filter(MonitorTarget.user_id == current_user.id).order_by(MonitorTarget.id).all()


@router.post("/targets", response_model=TargetResponse)
async def create_target(target: TargetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """添加监控目标"""
    db_target = MonitorTarget(**target.model_dump(), user_id=current_user.id)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.put("/targets/{target_id}", response_model=TargetResponse)
async def update_target(target_id: int, target: TargetUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新监控目标"""
    db_target = db.query(MonitorTarget).filter(
        MonitorTarget.id == target_id,
        MonitorTarget.user_id == current_user.id
    ).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Target not found")
    for key, value in target.model_dump(exclude_unset=True).items():
        setattr(db_target, key, value)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.delete("/targets/{target_id}")
async def delete_target(target_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除监控目标"""
    db_target = db.query(MonitorTarget).filter(
        MonitorTarget.id == target_id,
        MonitorTarget.user_id == current_user.id
    ).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(db_target)
    db.commit()
    return {"message": "deleted"}


@router.get("/logs/{target_id}", response_model=List[LogResponse])
async def get_logs(target_id: int, hours: int = 24, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户目标的监控日志"""
    # 验证目标属于当前用户
    target = db.query(MonitorTarget).filter(
        MonitorTarget.id == target_id,
        MonitorTarget.user_id == current_user.id
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    since = datetime.utcnow() - timedelta(hours=hours)
    logs = db.query(MonitorLog).filter(
        MonitorLog.target_id == target_id,
        MonitorLog.created_at >= since
    ).order_by(MonitorLog.created_at.desc()).limit(500).all()
    return logs


@router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的监控统计"""
    total = db.query(MonitorTarget).filter(MonitorTarget.user_id == current_user.id).count()
    up = db.query(MonitorTarget).filter(MonitorTarget.user_id == current_user.id, MonitorTarget.status == "up").count()
    down = db.query(MonitorTarget).filter(MonitorTarget.user_id == current_user.id, MonitorTarget.status == "down").count()
    return {
        "total": total,
        "up": up,
        "down": down,
        "availability": round(up / total * 100, 2) if total > 0 else 0
    }
