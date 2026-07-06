"""
新闻数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class NewsCache(Base):
    """新闻缓存"""
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)  # world, finance, tech, etc.
    source = Column(String(100))
    title = Column(Text)
    summary = Column(Text, default="")
    url = Column(String(500))
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
