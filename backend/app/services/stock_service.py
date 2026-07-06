"""
股票数据服务 - 使用 Yahoo Finance API
"""
import httpx
import json
from datetime import datetime, timedelta


class StockService:
    """股票数据服务"""

    BASE_URL = "https://query1.finance.yahoo.com"
    SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    async def get_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        try:
            url = f"{self.BASE_URL}/v8/finance/chart/{symbol}"
            params = {
                "interval": "1d",
                "range": "1d"
            }
            resp = await self.client.get(url, params=params)
            data = resp.json()

            if data.get("chart", {}).get("error"):
                return {"error": data["chart"]["error"]["description"]}

            result = data["chart"]["result"][0]
            meta = result["meta"]
            return {
                "symbol": symbol.upper(),
                "name": meta.get("shortName", meta.get("symbol", symbol)),
                "price": meta.get("regularMarketPrice", 0),
                "previous_close": meta.get("chartPreviousClose", meta.get("previousClose", 0)),
                "change": round(meta.get("regularMarketPrice", 0) - meta.get("chartPreviousClose", meta.get("previousClose", 0)), 2),
                "change_percent": round(
                    (meta.get("regularMarketPrice", 0) - meta.get("chartPreviousClose", meta.get("previousClose", 0)))
                    / meta.get("chartPreviousClose", meta.get("previousClose", 1)) * 100, 2
                ),
                "currency": meta.get("currency", "USD"),
                "exchange": meta.get("exchangeName", ""),
                "market_state": meta.get("marketState", ""),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_history(self, symbol: str, range: str = "1mo") -> dict:
        """获取历史K线数据"""
        try:
            range_map = {
                "1d": ("1d", "1m"),
                "5d": ("5d", "15m"),
                "1mo": ("1mo", "1d"),
                "3mo": ("3mo", "1d"),
                "6mo": ("6mo", "1d"),
                "1y": ("1y", "1d"),
                "5y": ("5y", "1wk"),
            }
            period, interval = range_map.get(range, ("1mo", "1d"))

            url = f"{self.BASE_URL}/v8/finance/chart/{symbol}"
            params = {
                "interval": interval,
                "range": period,
                "includePrePost": False
            }
            resp = await self.client.get(url, params=params)
            data = resp.json()

            if data.get("chart", {}).get("error"):
                return {"error": data["chart"]["error"]["description"]}

            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [{}])[0]
            adjclose = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])

            candles = []
            for i, ts in enumerate(timestamps):
                candles.append({
                    "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                    "open": indicators.get("open", [None]*len(timestamps))[i],
                    "high": indicators.get("high", [None]*len(timestamps))[i],
                    "low": indicators.get("low", [None]*len(timestamps))[i],
                    "close": indicators.get("close", [None]*len(timestamps))[i],
                    "volume": indicators.get("volume", [None]*len(timestamps))[i],
                    "adjclose": adjclose[i] if i < len(adjclose) else None,
                })

            return {
                "symbol": symbol.upper(),
                "range": range,
                "candles": candles
            }
        except Exception as e:
            return {"error": str(e)}

    async def search(self, query: str) -> list:
        """搜索股票"""
        try:
            params = {
                "q": query,
                "quotesCount": 10,
                "newsCount": 0
            }
            resp = await self.client.get(self.SEARCH_URL, params=params)
            data = resp.json()

            results = []
            for item in data.get("quotes", []):
                results.append({
                    "symbol": item.get("symbol", ""),
                    "name": item.get("shortname", item.get("longname", "")),
                    "exchange": item.get("exchange", ""),
                    "type": item.get("quoteType", "")
                })
            return results
        except Exception as e:
            return []

    async def close(self):
        await self.client.aclose()
