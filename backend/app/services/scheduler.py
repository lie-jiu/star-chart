"""
定时任务调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from app.services.monitor_checker import MonitorChecker
from app.services.news_service import NewsService
from app.database import SessionLocal

scheduler = AsyncIOScheduler()


async def monitor_check_job():
    """监控检查任务 - 每60秒"""
    checker = MonitorChecker()
    await checker.run_checks()


async def news_refresh_job():
    """新闻刷新任务 - 每30分钟"""
    db = SessionLocal()
    try:
        service = NewsService(db)
        # 刷新实时新闻
        count = await service.refresh_realtime()
        print(f"Realtime news refreshed: {count} items")
    except Exception as e:
        print(f"News refresh error: {e}")
    finally:
        db.close()


async def daily_news_refresh_job():
    """每日新闻刷新 - 每天6:30"""
    db = SessionLocal()
    try:
        service = NewsService(db)
        count = await service.refresh_daily()
        print(f"Daily news refreshed: {count} items")
    except Exception as e:
        print(f"Daily news refresh error: {e}")
    finally:
        db.close()


async def initial_news_fetch():
    """启动时预取新闻"""
    print("Fetching initial news...")
    await news_refresh_job()
    await daily_news_refresh_job()


def start_scheduler():
    """启动调度器"""
    # 监控检查 - 每60秒
    scheduler.add_job(
        monitor_check_job,
        IntervalTrigger(seconds=60),
        id="monitor_check",
        replace_existing=True
    )
    # 实时新闻刷新 - 每30分钟
    scheduler.add_job(
        news_refresh_job,
        IntervalTrigger(minutes=30),
        id="news_refresh",
        replace_existing=True
    )
    # 每日新闻刷新 - 每天6:30
    scheduler.add_job(
        daily_news_refresh_job,
        "cron",
        hour=6,
        minute=30,
        id="daily_news_refresh",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    print("Scheduler stopped")
