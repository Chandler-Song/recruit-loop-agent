# ---- 阶段1: 构建前端 ----
FROM node:18-alpine AS builder

WORKDIR /build

# 先复制依赖文件，利用 Docker 缓存层
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund 2>/dev/null || npm install --no-audit --no-fund

# 复制源码并构建
COPY public/ ./public/
COPY src/ ./src/

RUN npm run build

# ---- 阶段2: nginx 托管静态文件 ----
FROM nginx:1.25-alpine AS production

LABEL maintainer="Chandler Song"

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从 builder 阶段复制构建产物
COPY --from=builder /build/build /usr/share/nginx/html

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
