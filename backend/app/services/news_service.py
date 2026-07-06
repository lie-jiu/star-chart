"""
新闻数据服务 - 双数据源：60s API（每日摘要）+ RSS（实时新闻）
"""
import httpx
import json
import os
import re
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor

from app.models.news import NewsCache
from app.models.daily_news import DailyNewsCache

# 翻译线程池
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="translator")
_translator = None


def _get_translator():
    global _translator
    if _translator is None:
        from deep_translator import GoogleTranslator
        _translator = GoogleTranslator(source='auto', target='zh-CN')
    return _translator


def _translate_sync(text: str) -> str:
    if not text or len(text) < 3:
        return text
    try:
        t = _get_translator()
        return t.translate(text[:500])
    except Exception:
        return text


async def translate_async(text: str) -> str:
    if not text or len(text) < 3:
        return text
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _translate_sync, text)


class NewsService:
    """新闻聚合服务 - 60s API + RSS"""

    BASE_URL = "https://60s.liejiu.top"

    RSS_FEEDS = {
        "world": [
            ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Reuters World", "https://www.reutersagency.com/feed/"),
        ],
        "finance": [
            ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
            ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/"),
        ],
        "tech": [
            ("TechCrunch", "https://techcrunch.com/feed/"),
            ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ],
        "us_stock": [
            ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
            ("Seeking Alpha", "https://seekingalpha.com/feed.xml"),
        ],
        "crypto": [
            ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
            ("The Block", "https://www.theblock.co/rss.xml"),
        ],
    }

    def __init__(self, db: Session):
        self.db = db
        proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        client_kwargs = {
            "timeout": 15.0,
            "follow_redirects": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        }
        if proxy:
            client_kwargs["proxy"] = proxy
        self.client = httpx.AsyncClient(**client_kwargs)

    async def get_news(self, category: str = "world", limit: int = 20) -> list:
        """获取新闻（实时 + 每日摘要）"""
        # 获取实时新闻（RSS）
        realtime = self.db.query(NewsCache).filter(
            NewsCache.category == category
        ).order_by(NewsCache.id.desc()).limit(limit).all()

        # 获取每日摘要（60s）
        daily = self.db.query(DailyNewsCache).filter(
            DailyNewsCache.category == category
        ).order_by(DailyNewsCache.id.desc()).limit(limit).all()

        # 合并：每日摘要在前，实时新闻在后
        result = []

        for item in daily:
            result.append({
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "source": item.source,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "cover": item.cover or "",
                "tip": item.tip or "",
                "type": "daily",
            })

        for item in realtime:
            result.append({
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "source": item.source,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "cover": "",
                "tip": "",
                "type": "realtime",
            })

        return result[:limit]

    async def refresh_realtime(self) -> int:
        """刷新实时新闻（RSS 爬虫）"""
        total = 0
        for category, feeds in self.RSS_FEEDS.items():
            for source_name, feed_url in feeds:
                try:
                    items = await self._parse_rss(feed_url, source_name, category)
                    total += len(items)
                except Exception as e:
                    print(f"RSS parse error: {e}")
                    continue
        return total

    async def refresh_daily(self) -> int:
        """刷新每日摘要（60s API）"""
        try:
            resp = await self.client.get(f"{self.BASE_URL}/v2/60s")
            if resp.status_code != 200:
                return 0

            data = resp.json()
            if data.get("code") != 200:
                return 0

            news_data = data.get("data", {})
            news_list = news_data.get("news", [])
            date_str = news_data.get("date", "")
            tip = news_data.get("tip", "")
            cover = news_data.get("cover", "")
            link = news_data.get("link", "")

            # 清除旧缓存
            self.db.query(DailyNewsCache).filter(DailyNewsCache.category == "world").delete()

            # 写入新缓存
            for i, news_item in enumerate(news_list):
                db_item = DailyNewsCache(
                    category="world",
                    source="60s API",
                    title=news_item,
                    summary=f"{date_str} · {tip}",
                    url=link,
                    cover=cover,
                    tip=tip,
                    published_at=datetime.utcnow(),
                )
                self.db.add(db_item)

            self.db.commit()
            return len(news_list)
        except Exception as e:
            print(f"60s API error: {e}")
            self.db.rollback()
            return 0

    async def refresh_all(self) -> int:
        """刷新所有新闻"""
        daily_count = await self.refresh_daily()
        realtime_count = await self.refresh_realtime()
        return daily_count + realtime_count

    async def _parse_rss(self, url: str, source: str, category: str) -> list:
        """解析 RSS feed"""
        resp = await self.client.get(url)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.content)
        items = []

        # RSS 2.0
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "")

            desc = re.sub(r'<[^>]+>', '', desc).strip()[:300]

            published = None
            if pub_date:
                try:
                    published = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    pass

            if title and link:
                # 检查是否已存在
                existing = self.db.query(NewsCache).filter(NewsCache.url == link).first()
                if not existing:
                    title_zh = await translate_async(title)
                    desc_zh = await translate_async(desc) if desc else ""

                    db_item = NewsCache(
                        category=category,
                        source=source,
                        title=title_zh,
                        summary=desc_zh,
                        url=link,
                        published_at=published or datetime.utcnow(),
                    )
                    self.db.add(db_item)
                    items.append(db_item)

        # Atom
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//atom:entry", ns):
                title = entry.findtext("atom:title", "", ns).strip()
                link = entry.find("atom:link", ns)
                link = link.get("href", "") if link is not None else ""
                summary = entry.findtext("atom:summary", "", ns).strip()
                published_str = entry.findtext("atom:published", "", ns)

                published = None
                if published_str:
                    try:
                        published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                if title and link:
                    existing = self.db.query(NewsCache).filter(NewsCache.url == link).first()
                    if not existing:
                        title_zh = await translate_async(title)
                        summary_zh = await translate_async(summary) if summary else ""

                        db_item = NewsCache(
                            category=category,
                            source=source,
                            title=title_zh,
                            summary=summary_zh,
                            url=link,
                            published_at=published or datetime.utcnow(),
                        )
                        self.db.add(db_item)
                        items.append(db_item)

        self.db.commit()
        return items

    async def close(self):
        await self.client.aclose()
