"""
新闻路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.news_service import NewsService
from app.routers.auth import get_current_user
from app.models import User

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_news(
    category: str = "world",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取新闻"""
    service = NewsService(db)
    return await service.get_news(category, limit)


@router.get("/categories")
async def get_categories():
    """获取新闻分类"""
    return {
        "categories": [
            {"id": "world", "name": "🌍 国际"},
            {"id": "finance", "name": "💰 财经"},
            {"id": "tech", "name": "🔬 科技"},
            {"id": "us_stock", "name": "📈 美股"},
            {"id": "crypto", "name": "₿ 加密货币"},
        ]
    }


@router.post("/refresh")
async def refresh_news(db: Session = Depends(get_db)):
    """手动刷新新闻"""
    service = NewsService(db)
    count = await service.refresh_all()
    return {"message": f"Refreshed {count} news items"}
