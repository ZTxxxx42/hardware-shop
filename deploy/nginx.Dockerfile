# syntax=docker/dockerfile:1

# 五金商贸 MVP · 前端构建 + Nginx 运行镜像(多阶段)
# 构建上下文:仓库根目录(见 docker-compose.yml 的 nginx.build)
# 目的:让 `docker compose up -d --build` 一键完成两个 Web 前端构建,
#       无需宿主机安装 Node/npm,也不再要求宿主机的 dist/ 产物。
#
# 说明:根目录 .dockerignore 已排除 **/node_modules、**/dist、**/.env.*,
#       故此处 COPY 不会带入本地依赖与构建产物;VITE_API_BASE_URL 通过
#       构建参数注入(Vite 真实环境变量优先级高于 .env 文件),默认 / 表示同源。

# ---- 阶段一:构建 shop-web(买家端,根路径 /) ----
FROM node:20-alpine AS shop-web-build
WORKDIR /app
COPY frontend/shop-web/package.json frontend/shop-web/package-lock.json ./
RUN npm ci
COPY frontend/shop-web ./
ARG VITE_API_BASE_URL=/
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# ---- 阶段二:构建 admin-web(管理端,子路径 /admin/) ----
FROM node:20-alpine AS admin-web-build
WORKDIR /app
COPY frontend/admin-web/package.json frontend/admin-web/package-lock.json ./
RUN npm ci
COPY frontend/admin-web ./
ARG VITE_API_BASE_URL=/
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# ---- 阶段三:Nginx 运行时 ----
FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=shop-web-build /app/dist /usr/share/nginx/html/shop-web
COPY --from=admin-web-build /app/dist /usr/share/nginx/html/admin-web
