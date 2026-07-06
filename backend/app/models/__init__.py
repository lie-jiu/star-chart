"""
用户数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from datetime import datetime
from app.database import Base


class User(Base):
    """用户"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MonitorTarget(Base):
    """监控目标"""
    __tablename__ = "monitor_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    type = Column(String(20), default="http")
    interval = Column(Integer, default=60)
    timeout = Column(Integer, default=10)
    status = Column(String(20), default="unknown")
    uptime = Column(Float, default=100.0)
    response_time = Column(Float, default=0.0)
    last_check = Column(DateTime, default=datetime.utcnow)
    last_error = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class MonitorLog(Base):
    """监控日志"""
    __tablename__ = "monitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("monitor_targets.id", ondelete="CASCADE"), index=True)
    status = Column(String(20))
    response_time = Column(Float, default=0.0)
    status_code = Column(Integer, default=0)
    error = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class StockWatchlist(Base):
    """股票关注列表"""
    __tablename__ = "stock_watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symbol = Column(String(20), index=True)
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
    data_type = Column(String(20))
    data = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NewsCache(Base):
    """新闻缓存"""
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)
    source = Column(String(100))
    title = Column(Text)
    summary = Column(Text, default="")
    url = Column(String(500))
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)


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
