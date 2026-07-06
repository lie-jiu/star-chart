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

### 🔐 安全与权限
- **Argon2id** 慢哈希（PHC 冠军，OWASP 推荐）
- JWT Token 认证，7 天有效期
- 用户名纯英文 + 强密码策略
- SQL 注入防护（SQLAlchemy 参数化查询）
- **多用户隔离**：每个用户只能看到自己的数据
- **管理员系统**：管理员可管理所有用户权限

### 📱 响应式设计
- 桌面端侧边栏导航
- 移动端汉堡菜单 + 自适应布局
- 手机端优化，无横向溢出

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
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000`

### 7. 使用 CLI 管理（可选）

```bash
# 安装 CLI
sudo cp /usr/local/bin/dashboard /usr/local/bin/dashboard
sudo chmod +x /usr/local/bin/dashboard

# 使用命令
dashboard start          # 启动服务
dashboard stop           # 停止服务
dashboard restart        # 重启服务
dashboard status         # 查看状态
dashboard logs           # 查看日志
dashboard create-admin <用户名> <密码>  # 创建管理员
dashboard backup         # 备份数据库
```

## 📡 API 文档

启动后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要端点

**认证**
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户信息 |
| PATCH | `/api/auth/me` | 修改用户名 |
| POST | `/api/auth/change-password` | 修改密码 |
| DELETE | `/api/auth/me` | 注销当前账号 |

**监控**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/monitor/targets` | 监控目标列表 |
| POST | `/api/monitor/targets` | 添加监控目标 |
| PUT | `/api/monitor/targets/{id}` | 更新监控目标 |
| DELETE | `/api/monitor/targets/{id}` | 删除监控目标 |
| GET | `/api/monitor/logs/{id}` | 监控日志 |
| GET | `/api/monitor/stats` | 监控统计 |

**股票**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stocks/watchlist` | 关注列表 |
| POST | `/api/stocks/watchlist` | 添加关注 |
| DELETE | `/api/stocks/watchlist/{id}` | 移除关注 |
| GET | `/api/stocks/quote/{symbol}` | 实时行情 |
| GET | `/api/stocks/history/{symbol}` | 历史K线 |
| GET | `/api/stocks/search` | 搜索股票 |

**新闻**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news/` | 新闻列表 |
| GET | `/api/news/categories` | 新闻分类 |
| POST | `/api/news/refresh` | 手动刷新新闻 |

**管理（仅管理员）**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/auth/users` | 列出所有用户 |
| POST | `/api/auth/set-admin/{id}` | 设置管理员 |
| POST | `/api/auth/unset-admin/{id}` | 取消管理员 |
| DELETE | `/api/auth/users/{id}` | 删除用户 |

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

### 使用 CloudFlare Tunnel

```bash
# 安装 cloudflared
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 登录并创建隧道
cloudflared tunnel login
cloudflared tunnel create star-chart

# 配置 ingress
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <your-tunnel-id>
credentials-file: ~/.cloudflared/<your-tunnel-id>.json

ingress:
  - hostname: dashboard.yourdomain.com
    service: http://127.0.0.1:8000
  - service: http_status:404
EOF

# 启动
cloudflared tunnel run star-chart
```

## 🔒 安全建议

1. **修改默认 SECRET_KEY**：编辑 `backend/app/auth.py` 中的 `SECRET_KEY`
2. **使用强密码**：密码策略要求 8 位以上，含大小写字母、数字、特殊字符
3. **启用 HTTPS**：生产环境务必使用 HTTPS（CloudFlare Tunnel 自带）
4. **定期备份**：使用 `dashboard backup` 命令定期备份数据库
5. **最小权限**：只给必要用户管理员权限

## 📄 许可证

[MIT](LICENSE) © 2026 刘宇 (lie-jiu)
