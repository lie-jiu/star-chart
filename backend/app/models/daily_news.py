"""
每日新闻数据模型（60s API）
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class DailyNewsCache(Base):
    """每日新闻缓存（60s API）"""
    __tablename__ = "daily_news_cache"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)
    source = Column(String(100))
    title = Column(Text)
    summary = Column(Text, default="")
    url = Column(String(500))
    cover = Column(String(500), default="")
    tip = Column(Text, default="")
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
