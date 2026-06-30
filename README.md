# Recruiting Loop Agent v3.0

An autonomous recruiting agent that continuously searches for candidates until the position is closed.

## Overview

The Recruiting Loop Agent is designed to run indefinitely, searching for candidates, deduplicating, updating databases, automatically scoring, contacting candidates, and continuing the search until a position is closed.

## Tech Stack

- Backend: FastAPI
- Agent: LangGraph
- ORM: SQLAlchemy 2.x (Async)
- Database: SQLite
- Scheduler: APScheduler + asyncio
- Frontend: React + Ant Design
- HTTP Client: httpx
- Email: smtplib
- Container: Docker + Docker Compose + Nginx

## Architecture

The system follows a four-layer architecture:
- HTTP Request
- FastAPI Router
- Service Layer
- Repository Layer
- SQLite Database

---

## Production Deployment (Docker)

### 一键部署

适用于全新服务器，脚本会自动完成环境检查、Docker 安装、代码拉取、镜像构建和服务启动：

```bash
# 方式1：直接在服务器运行
bash deploy.sh

# 方式2：curl 一键部署（推送到 GitHub 后）
curl -fsSL https://raw.githubusercontent.com/Chandler-Song/recruit-loop-agent/main/scripts/deploy.sh | bash
```

部署完成后：

| 服务 | 地址 |
|------|------|
| 前端 | `http://<服务器IP>` |
| 后端 API | `http://<服务器IP>:8000` |
| API 文档 | `http://<服务器IP>:8000/docs` |

### 手动部署

```bash
# 1. 克隆代码
git clone git@github.com:Chandler-Song/recruit-loop-agent.git
cd recruit-loop-agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 GITHUB_TOKEN、SMTP 等信息

# 3. 启动服务
docker compose up -d --build

# 4. 查看日志
docker compose logs -f
```

### 环境变量

参考 `.env.example`，关键配置项：

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./db/recruiting_agent.db` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_xxxx` |
| `SMTP_HOST` | 邮件服务器 | `smtp.gmail.com` |
| `SMTP_USER` | 邮件用户名 | `your@gmail.com` |
| `SMTP_PASSWORD` | 邮件密码/应用专用密码 | `xxxx` |
| `SMTP_PORT` | 邮件端口 | `587` |
| `EMAIL_FROM` | 发件人地址 | `your@gmail.com` |

---

## Local Development

### 后端启动

前提条件：Python 3.8+

```bash
bash scripts/start_app.sh
```

- 自动创建虚拟环境 `venv/`
- 从 `.env.example` 生成 `.env`（如不存在）
- 安装 `requirements.txt` 依赖
- 启动 FastAPI 服务于 `http://localhost:8000`（热重载）
- API 文档：`http://localhost:8000/docs`

### 前端启动

前提条件：Node.js 16+、npm

```bash
bash scripts/start_frontend.sh
```

- 自动检测 `node_modules`，不存在则安装依赖
- 设置 `REACT_APP_API_URL=http://localhost:8000/api/v1`
- 启动 React 开发服务器于 `http://localhost:3000`

### 代码推送

```bash
bash scripts/git-push.sh
```

- 自动初始化 Git 仓库（如不存在）
- 配置远程仓库 `git@github.com:Chandler-Song/recruit-loop-agent.git`
- 统一使用 `main` 分支
- 交互式输入 commit message（回车使用默认时间戳格式）
- 推送到远程仓库

---

## Scripts Reference

| 脚本 | 用途 | 环境 |
|------|------|------|
| `scripts/deploy.sh` | 远程服务器一键部署 | 生产环境 |
| `scripts/start_app.sh` | 启动后端开发服务器 | 本地开发 |
| `scripts/start_frontend.sh` | 启动前端开发服务器 | 本地开发 |
| `scripts/git-push.sh` | Git 提交并推送代码 | 通用 |

## Project Structure

```
loop-agent/
├── app/                    # 后端 FastAPI 应用
│   ├── api/               # API 路由层
│   ├── services/          # 业务逻辑层
│   ├── repositories/      # 数据访问层
│   ├── models/            # SQLAlchemy ORM 模型
│   ├── schemas/           # Pydantic 数据校验
│   ├── agents/            # LangGraph 工作流
│   ├── skills/            # GitHub 搜索技能
│   ├── core/              # 配置、异常、日志
│   ├── database/          # 数据库连接
│   └── main.py            # 应用入口
├── frontend/              # React 前端应用
│   ├── src/               # 源码
│   ├── public/            # 静态资源
│   ├── Dockerfile         # 前端生产镜像
│   └── nginx.conf         # Nginx 反向代理配置
├── scripts/               # 自动化脚本
├── docker-compose.yml     # Docker 编排
├── Dockerfile             # 后端生产镜像
├── requirements.txt       # Python 依赖
└── .env.example           # 环境变量模板
```
