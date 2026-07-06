"""
股票路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import StockWatchlist, StockCache, User
from app.services.stock_service import StockService
from app.routers.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


class WatchlistCreate(BaseModel):
    symbol: str
    name: str = ""
    note: str = ""
    alert_high: float = 0.0
    alert_low: float = 0.0


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None
    alert_high: Optional[float] = None
    alert_low: Optional[float] = None


@router.get("/watchlist")
async def get_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的关注列表"""
    items = db.query(StockWatchlist).filter(
        StockWatchlist.user_id == current_user.id
    ).order_by(StockWatchlist.added_at.desc()).all()

    service = StockService()
    result = []
    for item in items:
        quote = await service.get_quote(item.symbol)
        result.append({
            "id": item.id,
            "symbol": item.symbol,
            "name": item.name or quote.get("name", ""),
            "note": item.note,
            "alert_high": item.alert_high,
            "alert_low": item.alert_low,
            "quote": quote
        })
    return result


@router.post("/watchlist")
async def add_to_watchlist(item: WatchlistCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """添加关注股票"""
    existing = db.query(StockWatchlist).filter(
        StockWatchlist.user_id == current_user.id,
        StockWatchlist.symbol == item.symbol.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in watchlist")
    db_item = StockWatchlist(
        user_id=current_user.id,
        symbol=item.symbol.upper(),
        name=item.name,
        note=item.note,
        alert_high=item.alert_high,
        alert_low=item.alert_low
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """移除关注股票"""
    item = db.query(StockWatchlist).filter(
        StockWatchlist.id == item_id,
        StockWatchlist.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"message": "removed"}


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """获取实时行情"""
    service = StockService()
    return await service.get_quote(symbol)


@router.get("/history/{symbol}")
async def get_history(symbol: str, range: str = "1mo"):
    """获取历史数据"""
    service = StockService()
    return await service.get_history(symbol, range)


@router.get("/search")
async def search_stock(q: str):
    """搜索股票"""
    service = StockService()
    return await service.search(q)
