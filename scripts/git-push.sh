#!/bin/bash
# ============================================================
# git-push.sh - 将项目代码推送到远程 Git 仓库
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

REMOTE_URL="git@github.com:Chandler-Song/recruit-loop-agent.git"

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------- 1. Git 环境检查 ----------
if ! command -v git &>/dev/null; then
    error "未找到 git，请先安装 Git"
    exit 1
fi
info "Git 版本: $(git --version)"

cd "$PROJECT_DIR"
info "项目目录: $PROJECT_DIR"

# ---------- 2. 仓库初始化 ----------
if [ ! -d ".git" ]; then
    info "初始化 Git 仓库..."
    git init
    if [ $? -ne 0 ]; then
        error "git init 失败"
        exit 1
    fi
    info "Git 仓库初始化完成"
else
    info "Git 仓库已存在"
fi

# ---------- 3. 远程仓库配置 ----------
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$CURRENT_REMOTE" ]; then
    info "添加远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
    if [ $? -ne 0 ]; then
        error "git remote add origin 失败"
        exit 1
    fi
    info "远程仓库配置完成"
elif [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
    warn "当前远程地址: $CURRENT_REMOTE"
    warn "目标远程地址: $REMOTE_URL"
    read -p "是否更新远程地址？(y/N) " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        git remote set-url origin "$REMOTE_URL"
        if [ $? -ne 0 ]; then
            error "git remote set-url 失败"
            exit 1
        fi
        info "远程地址已更新"
    else
        info "保持当前远程地址: $CURRENT_REMOTE"
    fi
else
    info "远程仓库已配置: $REMOTE_URL"
fi

# ---------- 4. 分支管理 ----------
# 检查是否已有 commit（空仓库没有任何分支）
if ! git rev-parse HEAD &>/dev/null; then
    info "空仓库，创建初始提交..."
    git add .
    git commit -m "initial commit" --allow-empty
    if [ $? -ne 0 ]; then
        error "初始提交失败"
        exit 1
    fi
    info "初始提交完成"
fi

# 检查当前分支是否已经是 main
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" != "main" ]; then
    info "切换分支为 main..."
    git branch -M main
    if [ $? -ne 0 ]; then
        error "git branch -M main 失败"
        exit 1
    fi
    info "分支已切换为 main"
else
    info "当前已在 main 分支"
fi

# ---------- 5. 提交与推送 ----------
echo ""
info "当前工作区状态:"
git status

info "暂存所有变更..."
git add .
if [ $? -ne 0 ]; then
    error "git add . 失败"
    exit 1
fi

# 检查是否有待提交的变更
if git diff --cached --quiet; then
    info "没有待提交的变更，无需推送"
    exit 0
fi

# 提示用户输入 commit message
echo ""
read -p "请输入 commit message（回车使用默认值）: " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="update: $(date '+%Y-%m-%d %H:%M:%S')"
fi

info "提交信息: $commit_msg"

git commit -m "$commit_msg"
if [ $? -ne 0 ]; then
    error "git commit 失败"
    exit 1
fi
info "提交完成"

info "推送到远程仓库..."
git push -u origin main
if [ $? -ne 0 ]; then
    error "git push 失败"
    exit 1
fi

info "=========================================="
info "  推送成功！"
info "  远程: $REMOTE_URL"
info "  分支: main"
info "=========================================="
