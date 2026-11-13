#!/bin/sh
set -eu

# 数据库就绪由 compose 的 depends_on: db(service_healthy) 保证。
# 迁移幂等,容器每次启动执行是安全的。
echo "[entrypoint] 执行数据库迁移 alembic upgrade head"
alembic upgrade head

# 可选:填充/刷新种子数据(幂等)。设置 SEED_DATA=true 启用。
if [ "${SEED_DATA:-false}" = "true" ]; then
  echo "[entrypoint] 填充种子数据 python -m scripts.seed"
  python -m scripts.seed
fi

echo "[entrypoint] 启动: $*"
exec "$@"
