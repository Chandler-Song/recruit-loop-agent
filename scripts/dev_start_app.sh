#!/bin/bash
# ============================================================
# start_app.sh - 启动 Recruiting Loop Agent 后端服务
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------- 检查 Python ----------
if ! command -v python3 &>/dev/null; then
    error "未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
info "Python 版本: $PYTHON_VERSION"

# ---------- 虚拟环境 ----------
if [ ! -d "$VENV_DIR" ]; then
    info "创建虚拟环境: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
info "已激活虚拟环境: $VENV_DIR"

# ---------- 环境变量 ----------
cd "$PROJECT_DIR"

if [ -f .env ]; then
    info "加载 .env 文件"
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    warn "未找到 .env 文件，使用默认环境变量"
    warn "建议复制 .env.example 为 .env 并填写配置"
    if [ -f .env.example ]; then
        cp .env.example .env
        warn "已自动复制 .env.example -> .env，请按需修改"
    fi
fi

# ---------- 安装依赖 ----------
if [ -f requirements.txt ]; then
    info "安装 Python 依赖..."
    pip install -r requirements.txt -q
    info "依赖安装完成"
fi

# ---------- 启动服务 ----------
info "=========================================="
info "  Recruiting Loop Agent 后端启动中"
info "  地址: http://localhost:8000"
info "  文档: http://localhost:8000/docs"
info "=========================================="

uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload \
    --reload-dir app
