"""数据库引擎与会话工厂。

database agent 负责 `app.models` 元数据与 `alembic`;本模块只提供应用层会话,
URL 取自 `app.core.config.settings.database_url`,避免与 models/alembic 目录冲突。
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
