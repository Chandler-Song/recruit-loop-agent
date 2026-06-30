# ---- 阶段1: 构建依赖 ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- 阶段2: 生产运行 ----
FROM python:3.11-slim AS production

LABEL maintainer="Chandler Song"

# 安装 curl 用于 healthcheck，然后清理缓存
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制已安装的 Python 依赖
COPY --from=builder /install /usr/local

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# 复制应用源码
COPY app/ ./app/
COPY .env.example ./

# 创建数据和日志目录
RUN mkdir -p /app/db /app/logs /app/data \
    && chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
