"""商品目录路由(游客可浏览,价格按登录态动态返回)。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_optional_user
from app.core.security import AuthUser
from app.schemas.catalog import CategoryOut, ProductBrief, ProductDetail
from app.schemas.common import PageResult
from app.services import catalog as catalog_service

router = APIRouter(prefix="/catalog", tags=["商品目录"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    return catalog_service.list_categories(db)


@router.get("/products", response_model=PageResult[ProductBrief])
def list_products(
    category_id: int | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser | None = Depends(get_optional_user),
) -> PageResult[ProductBrief]:
    return catalog_service.list_products(db, user, category_id, keyword, page, page_size)


@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: AuthUser | None = Depends(get_optional_user),
) -> ProductDetail:
    return catalog_service.get_product(db, user, product_id)
