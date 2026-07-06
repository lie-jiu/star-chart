"""
股票数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base


class StockWatchlist(Base):
    """股票关注列表"""
    __tablename__ = "stock_watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(100), default="")
    added_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text, default="")
    alert_high = Column(Float, default=0.0)
    alert_low = Column(Float, default=0.0)


class StockCache(Base):
    """股票数据缓存"""
    __tablename__ = "stock_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    data_type = Column(String(20))  # quote, history, news
    data = Column(Text)  # JSON string
    updated_at = Column(DateTime, default=datetime.utcnow)
