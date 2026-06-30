#!/bin/bash
# ============================================================
# start_frontend.sh - 启动 Recruiting Loop Agent 前端服务
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------- 检查 Node.js ----------
if ! command -v node &>/dev/null; then
    error "未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node -v)
info "Node.js 版本: $NODE_VERSION"

if ! command -v npm &>/dev/null; then
    error "未找到 npm，请先安装 npm"
    exit 1
fi

NPM_VERSION=$(npm -v)
info "npm 版本: $NPM_VERSION"

# ---------- 进入前端目录 ----------
if [ ! -d "$FRONTEND_DIR" ]; then
    error "前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"
info "工作目录: $FRONTEND_DIR"

# ---------- 环境变量 ----------
export PORT=3000
export REACT_APP_API_URL="http://localhost:8000/api/v1"
info "前端端口: $PORT"
info "后端 API: $REACT_APP_API_URL"

# ---------- 安装依赖 ----------
# 检查 node_modules 以及 react-scripts 是否存在本地安装
if [ ! -d "node_modules" ] || [ ! -d "node_modules/react-scripts" ]; then
    info "开始安装依赖（包括 react-scripts）..."
    npm install
    info "依赖安装完成"
else
    info "node_modules 已存在，跳过依赖安装"
fi

# ---------- 启动服务 ----------
info "=========================================="
info "  Recruiting Loop Agent 前端启动中"
info "  地址: http://localhost:3000"
info "  后端: http://localhost:8000/api/v1"
info "=========================================="

# 使用本地安装的 react-scripts（通过 npm start 调用 package.json 中的 start 脚本）
npm start
