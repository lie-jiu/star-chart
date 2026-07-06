"""
监控相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from datetime import datetime
from app.database import Base


class MonitorTarget(Base):
    """监控目标"""
    __tablename__ = "monitor_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    type = Column(String(20), default="http")  # http, ping, tcp, dns
    interval = Column(Integer, default=60)  # 检查间隔（秒）
    timeout = Column(Integer, default=10)  # 超时（秒）
    status = Column(String(20), default="unknown")  # up, down, unknown
    uptime = Column(Float, default=100.0)  # 可用率
    response_time = Column(Float, default=0.0)  # 响应时间ms
    last_check = Column(DateTime, default=datetime.utcnow)
    last_error = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class MonitorLog(Base):
    """监控日志"""
    __tablename__ = "monitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, index=True)
    status = Column(String(20))  # up, down
    response_time = Column(Float, default=0.0)
    status_code = Column(Integer, default=0)
    error = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
