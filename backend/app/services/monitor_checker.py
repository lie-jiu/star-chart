"""
监控检查服务
"""
import httpx
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import MonitorTarget, MonitorLog


class MonitorChecker:
    """监控检查器"""

    async def check_target(self, target: MonitorTarget) -> dict:
        """检查单个目标"""
        start = datetime.utcnow()
        try:
            if target.type == "http":
                return await self._check_http(target, start)
            elif target.type == "ping":
                return await self._check_ping(target, start)
            elif target.type == "tcp":
                return await self._check_tcp(target, start)
            else:
                return await self._check_http(target, start)
        except Exception as e:
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            return {
                "status": "down",
                "response_time": round(elapsed, 2),
                "status_code": 0,
                "error": str(e)
            }

    async def _check_http(self, target: MonitorTarget, start: datetime) -> dict:
        """HTTP 检查"""
        async with httpx.AsyncClient(
            timeout=target.timeout,
            follow_redirects=True,
            verify=False
        ) as client:
            resp = await client.get(target.url)
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            status = "up" if resp.status_code < 500 else "down"
            return {
                "status": status,
                "response_time": round(elapsed, 2),
                "status_code": resp.status_code,
                "error": "" if status == "up" else f"HTTP {resp.status_code}"
            }

    async def _check_ping(self, target: MonitorTarget, start: datetime) -> dict:
        """Ping 检查"""
        import subprocess
        # 从 URL 中提取 host
        host = target.url.replace("ping://", "").replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
        try:
            result = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", str(target.timeout), host,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            await asyncio.wait_for(result.wait(), timeout=target.timeout)
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            if result.returncode == 0:
                return {"status": "up", "response_time": round(elapsed, 2), "status_code": 0, "error": ""}
            else:
                return {"status": "down", "response_time": round(elapsed, 2), "status_code": 0, "error": "Ping failed"}
        except asyncio.TimeoutError:
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            return {"status": "down", "response_time": round(elapsed, 2), "status_code": 0, "error": "Timeout"}

    async def _check_tcp(self, target: MonitorTarget, start: datetime) -> dict:
        """TCP 端口检查"""
        host_port = target.url.replace("tcp://", "").split("/")[0]
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            port = int(port)
        else:
            host = host_port
            port = 80
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=target.timeout
            )
            writer.close()
            await writer.wait_closed()
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            return {"status": "up", "response_time": round(elapsed, 2), "status_code": 0, "error": ""}
        except Exception as e:
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            return {"status": "down", "response_time": round(elapsed, 2), "status_code": 0, "error": str(e)}

    async def run_checks(self):
        """运行所有监控检查"""
        db = SessionLocal()
        try:
            targets = db.query(MonitorTarget).filter(MonitorTarget.is_active == True).all()
            for target in targets:
                result = await self.check_target(target)

                # 更新目标状态
                target.status = result["status"]
                target.response_time = result["response_time"]
                target.last_check = datetime.utcnow()
                if result["error"]:
                    target.last_error = result["error"]
                else:
                    target.last_error = ""

                # 计算可用率（最近100条日志）
                logs = db.query(MonitorLog).filter(
                    MonitorLog.target_id == target.id
                ).order_by(MonitorLog.created_at.desc()).limit(100).all()
                if logs:
                    up_count = sum(1 for l in logs if l.status == "up")
                    target.uptime = round(up_count / len(logs) * 100, 2)

                # 写入日志
                log = MonitorLog(
                    target_id=target.id,
                    status=result["status"],
                    response_time=result["response_time"],
                    status_code=result["status_code"],
                    error=result["error"]
                )
                db.add(log)

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Monitor check error: {e}")
        finally:
            db.close()
