"""
星图 Dashboard - 后端主入口
"""
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import monitor, stocks, news, auth
from app.services.scheduler import start_scheduler, stop_scheduler, initial_news_fetch


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_db()
    start_scheduler()
    asyncio.create_task(initial_news_fetch())
    yield
    stop_scheduler()


app = FastAPI(
    title="星图 Dashboard",
    description="服务监控 + 美股分析 + 全球新闻",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(auth, prefix="/api/auth", tags=["认证"])
app.include_router(monitor, prefix="/api/monitor", tags=["监控"])
app.include_router(stocks, prefix="/api/stocks", tags=["股票"])
app.include_router(news, prefix="/api/news", tags=["新闻"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "dashboard"}


# 静态文件（前端构建产物）
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
assets_dir = os.path.join(static_dir, "assets")


@app.get("/", response_class=FileResponse)
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    file_location = os.path.join(assets_dir, file_path)
    if os.path.exists(file_location):
        return FileResponse(file_location)
    raise HTTPException(status_code=404, detail="Asset not found")


# SPA Fallback: 所有未匹配路径返回 index.html（API 除外）
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # API 路径返回 404 JSON
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    # 检查是否是静态文件
    file_location = os.path.join(static_dir, full_path)
    if os.path.exists(file_location):
        return FileResponse(file_location)
    # 其他路径返回 index.html（让 Vue Router 处理）
    return FileResponse(os.path.join(static_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
