# syntax=docker/dockerfile:1

# 五金商贸 MVP 后端镜像:FastAPI + uvicorn(Python 3.13)
# 构建上下文:backend/
FROM python:3.13-slim

# 不生成 .pyc、日志不缓冲,便于容器日志收集
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 先复制依赖清单,充分利用构建层缓存
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用、迁移与入口脚本
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 非 root 运行(生产最佳实践)
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000

# 健康检查:用标准库发起请求,避免额外安装 curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
