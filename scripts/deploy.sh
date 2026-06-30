#!/bin/bash
# ============================================================
# deploy.sh - Recruiting Loop Agent 一键部署脚本
# 用法: bash deploy.sh 或 curl <url> | bash
# ============================================================
set -e

# ---------- 配置 ----------
REPO_URL="git@github.com:Chandler-Song/recruit-loop-agent.git"
PROJECT_NAME="recruit-loop-agent"
INSTALL_DIR="$HOME/$PROJECT_NAME"

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step()  { echo -e "${BLUE}[STEP]${NC}  $1"; }

banner() {
    echo -e "${BLUE}"
    echo "  ============================================"
    echo "    Recruiting Loop Agent - 一键部署"
    echo "  ============================================"
    echo -e "${NC}"
}

# ============================================================
# 1. 环境检查
# ============================================================
check_environment() {
    step "检查服务器环境..."

    # 检查是否为 root 或有 sudo 权限
    if [ "$(id -u)" -ne 0 ] && ! command -v sudo &>/dev/null; then
        warn "非 root 用户且无 sudo，部分安装步骤可能失败"
        warn "建议使用 root 用户或有 sudo 权限的用户运行"
    fi

    # 检查 Docker
    if command -v docker &>/dev/null; then
        DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        info "Docker 已安装: v$DOCKER_VERSION"
    else
        warn "Docker 未安装，正在自动安装..."
        install_docker
    fi

    # 检查 Docker Compose
    if docker compose version &>/dev/null; then
        COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || docker compose version)
        info "Docker Compose 已安装: $COMPOSE_VERSION"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        info "docker-compose 已安装: $COMPOSE_VERSION"
    else
        warn "Docker Compose 未安装，正在自动安装..."
        install_docker_compose
    fi

    # 检查 Git
    if ! command -v git &>/dev/null; then
        warn "Git 未安装，正在自动安装..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get update -qq && sudo apt-get install -y -qq git
        elif command -v yum &>/dev/null; then
            sudo yum install -y -q git
        else
            error "无法自动安装 Git，请手动安装后重试"
            exit 1
        fi
    fi
    info "Git: $(git --version)"

    # 确保 Docker 服务正在运行
    if ! docker info &>/dev/null; then
        error "Docker 服务未运行，请执行: sudo systemctl start docker"
        exit 1
    fi

    info "环境检查通过"
}

# ============================================================
# Docker 安装
# ============================================================
install_docker() {
    info "使用官方脚本安装 Docker..."
    curl -fsSL https://get.docker.com | sh

    # 将当前用户加入 docker 组
    if [ "$(id -u)" -ne 0 ]; then
        sudo usermod -aG docker "$USER" 2>/dev/null || true
        warn "已将 $USER 加入 docker 组，如遇到权限问题请重新登录"
    fi

    # 启动 Docker
    sudo systemctl enable docker 2>/dev/null || true
    sudo systemctl start docker 2>/dev/null || true

    if ! command -v docker &>/dev/null; then
        error "Docker 安装失败"
        exit 1
    fi
    info "Docker 安装完成: $(docker --version)"
}

install_docker_compose() {
    # 尝试安装 docker compose plugin
    sudo mkdir -p /usr/local/lib/docker/cli-plugins
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="x86_64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="aarch64"
    fi

    sudo curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${ARCH}" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose 2>/dev/null
    sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

    if ! docker compose version &>/dev/null; then
        # 回退：安装独立版本
        sudo curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${ARCH}" \
            -o /usr/local/bin/docker-compose 2>/dev/null
        sudo chmod +x /usr/local/bin/docker-compose
    fi

    info "Docker Compose 安装完成"
}

# ============================================================
# 2. 代码获取
# ============================================================
fetch_code() {
    step "获取项目代码..."

    if [ -d "$INSTALL_DIR/.git" ]; then
        info "项目目录已存在，拉取最新代码..."
        cd "$INSTALL_DIR"
        git pull origin main || {
            warn "git pull 失败，尝试强制重置..."
            git fetch origin main
            git reset --hard origin/main
        }
    else
        if [ -d "$INSTALL_DIR" ]; then
            warn "目录 $INSTALL_DIR 已存在但不是 Git 仓库"
            read -p "是否删除并重新克隆？(y/N) " confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                error "取消部署"
                exit 1
            fi
            rm -rf "$INSTALL_DIR"
        fi

        info "克隆项目代码..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        if [ $? -ne 0 ]; then
            error "代码克隆失败，请检查 Git SSH 密钥配置"
            exit 1
        fi
    fi

    cd "$INSTALL_DIR"
    info "代码获取完成: $INSTALL_DIR"
}

# ============================================================
# 3. 环境变量配置
# ============================================================
configure_env() {
    step "配置环境变量..."

    if [ -f .env ]; then
        info ".env 文件已存在，跳过生成"
        echo ""
        warn "如需修改配置，请编辑: $INSTALL_DIR/.env"
        return
    fi

    if [ ! -f .env.example ]; then
        error ".env.example 文件不存在"
        exit 1
    fi

    cp .env.example .env
    info "已从 .env.example 生成 .env 文件"

    echo ""
    echo -e "${YELLOW}=====================================${NC}"
    echo -e "${YELLOW}  请填写以下关键配置（按 Enter 跳过）${NC}"
    echo -e "${YELLOW}=====================================${NC}"
    echo ""

    read -p "GitHub Token (用于搜索候选人): " github_token
    if [ -n "$github_token" ]; then
        sed -i.bak "s|^GITHUB_TOKEN=.*|GITHUB_TOKEN=$github_token|" .env && rm -f .env.bak
    fi

    read -p "SMTP Host (默认 smtp.gmail.com): " smtp_host
    if [ -n "$smtp_host" ]; then
        sed -i.bak "s|^SMTP_HOST=.*|SMTP_HOST=$smtp_host|" .env && rm -f .env.bak
    fi

    read -p "SMTP User (邮箱地址): " smtp_user
    if [ -n "$smtp_user" ]; then
        sed -i.bak "s|^SMTP_USER=.*|SMTP_USER=$smtp_user|" .env && rm -f .env.bak
    fi

    read -p "SMTP Password (应用专用密码): " smtp_password
    if [ -n "$smtp_password" ]; then
        sed -i.bak "s|^SMTP_PASSWORD=.*|SMTP_PASSWORD=$smtp_password|" .env && rm -f .env.bak
    fi

    read -p "Email From (发件人邮箱): " email_from
    if [ -n "$email_from" ]; then
        sed -i.bak "s|^EMAIL_FROM=.*|EMAIL_FROM=$email_from|" .env && rm -f .env.bak
    fi

    info "环境变量配置完成"
}

# ============================================================
# 4. Docker Compose 构建与启动
# ============================================================
build_and_start() {
    step "构建 Docker 镜像并启动服务..."

    cd "$INSTALL_DIR"

    # 停止旧服务（如有）
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

    # 构建镜像
    info "构建 Docker 镜像（首次构建可能需要几分钟）..."
    if docker compose version &>/dev/null; then
        docker compose build --no-cache
    else
        docker-compose build --no-cache
    fi

    if [ $? -ne 0 ]; then
        error "Docker 镜像构建失败"
        exit 1
    fi
    info "镜像构建完成"

    # 启动服务
    info "启动服务..."
    if docker compose version &>/dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    if [ $? -ne 0 ]; then
        error "服务启动失败"
        exit 1
    fi

    info "服务启动完成"
}

# ============================================================
# 5. 健康检查与结果输出
# ============================================================
health_check() {
    step "等待服务就绪..."

    # 等待后端
    RETRIES=30
    for i in $(seq 1 $RETRIES); do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            info "后端服务已就绪"
            break
        fi
        if [ "$i" -eq "$RETRIES" ]; then
            warn "后端服务尚未就绪，请检查日志: docker compose logs backend"
        fi
        sleep 2
    done

    # 等待前端
    RETRIES=15
    for i in $(seq 1 $RETRIES); do
        if curl -sf http://localhost/ >/dev/null 2>&1; then
            info "前端服务已就绪"
            break
        fi
        if [ "$i" -eq "$RETRIES" ]; then
            warn "前端服务尚未就绪，请检查日志: docker compose logs frontend"
        fi
        sleep 2
    done

    # 获取服务器 IP
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "your-server-ip")

    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}  部署完成！${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo -e "  前端地址:   ${BLUE}http://${SERVER_IP}${NC}"
    echo -e "  后端 API:   ${BLUE}http://${SERVER_IP}:8000${NC}"
    echo -e "  API 文档:   ${BLUE}http://${SERVER_IP}:8000/docs${NC}"
    echo ""
    echo -e "  查看日志:   ${YELLOW}docker compose logs -f${NC}"
    echo -e "  停止服务:   ${YELLOW}docker compose down${NC}"
    echo -e "  重启服务:   ${YELLOW}docker compose restart${NC}"
    echo ""

    # 显示容器状态
    echo -e "${BLUE}容器状态:${NC}"
    docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null
}

# ============================================================
# 主流程
# ============================================================
main() {
    banner
    check_environment
    echo ""
    fetch_code
    echo ""
    configure_env
    echo ""
    build_and_start
    echo ""
    health_check
}

main "$@"
