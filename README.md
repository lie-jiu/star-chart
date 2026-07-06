# 星图 Dashboard

> 服务监控 · 美股分析 · 全球新闻聚合

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-42b883.svg)](https://vuejs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个轻量级的自托管仪表盘，用于监控 VPS/服务状态、追踪美股行情、聚合全球新闻热点。

## ✨ 功能特性

### 🖥️ 服务监控
- HTTP / Ping / TCP 端口检测
- 实时状态、响应时间、可用率统计
- 每 60 秒自动检查，异常时记录日志
- 历史数据可视化

### 📈 美股分析
- Yahoo Finance 实时行情
- K 线图（ECharts）支持 1天~5年
- 股票搜索与关注列表
- 价格提醒（高/低点预警）

### 🌍 全球新闻
- **每日摘要**：60s API 每日早 6:30 自动抓取
- **实时新闻**：RSS 聚合（BBC/Yahoo/TechCrunch 等），每 30 分钟刷新
- **自动翻译**：英文新闻实时翻译为中文
- 5 大分类：国际/财经/科技/美股/加密货币

### 🔐 安全
- **Argon2id** 慢哈希（PHC 冠军，OWASP 推荐）
- JWT Token 认证，7 天有效期
- 用户名纯英文 + 强密码策略
- SQL 注入防护（SQLAlchemy 参数化查询）
- HTTPS 安全头部（HSTS/CSP/X-Frame-Options）

### 📱 响应式
- 桌面端侧边栏导航
- 移动端汉堡菜单 + 自适应布局

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.13 + FastAPI + SQLAlchemy |
| 前端 | Vue 3 + Vite + ECharts |
| 数据库 | PostgreSQL 17 |
| 定时任务 | APScheduler |
| 密码哈希 | Argon2id |
| 部署 | Uvicorn + Nginx/Caddy |

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 1. 克隆仓库

```bash
git clone https://github.com/lie-jiu/star-chart.git
cd star-chart
```

### 2. 配置数据库

```bash
sudo -u postgres psql -c "CREATE USER dashboard WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE dashboard OWNER dashboard;"
```

### 3. 后端配置

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 修改数据库连接
export DATABASE_URL="postgresql://dashboard:your_password@127.0.0.1:5432/dashboard"
```

### 4. 前端构建

```bash
cd frontend
npm install
npm run build
```

### 5. 创建管理员

```bash
cd backend
source venv/bin/activate
python create_admin.py <用户名> <密码>
```

### 6. 启动服务

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000`

## 📡 API 文档

启动后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户 |
| GET | `/api/monitor/targets` | 监控目标列表 |
| POST | `/api/monitor/targets` | 添加监控目标 |
| GET | `/api/stocks/quote/{symbol}` | 实时行情 |
| GET | `/api/stocks/history/{symbol}` | 历史K线 |
| GET | `/api/news/` | 新闻列表 |
| POST | `/api/news/refresh` | 手动刷新新闻 |

## 🔧 部署

### 使用 systemd

```ini
# /etc/systemd/system/star-chart.service
[Unit]
Description=Star Chart Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/dashboard/backend
Environment=DATABASE_URL=postgresql://dashboard:password@127.0.0.1:5432/dashboard
ExecStart=/root/dashboard/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable star-chart
sudo systemctl start star-chart
```

### 使用 Nginx 反代

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📄 许可证

[MIT](LICENSE) © 2026 刘宇 (lie-jiu)
