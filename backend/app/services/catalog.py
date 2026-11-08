"""商品目录用例:分类、商品列表/详情,按登录态动态取价。"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.security import AuthUser
from app.domain.pricing import resolve_product_price
from app.models import (  # 由 database agent 提供
    Category,
    Product,
    ProductImage,
    ProductPrice,
    ProductSpec,
)
from app.schemas.catalog import (
    CategoryOut,
    ProductBrief,
    ProductDetail,
    ProductImageOut,
    ProductPriceItem,
    ProductSpecOut,
)
from app.schemas.common import PageResult

ON_SALE_STATUS = "ON_SALE"  # TODO: 与 database agent 的 product.status 枚举对齐


def list_categories(db: Session) -> list[CategoryOut]:
    rows = db.scalars(select(Category).order_by(Category.sort, Category.id)).all()
    return [CategoryOut.model_validate(r) for r in rows]


def _price_map(db: Session, product_id: int) -> dict[str, Decimal]:
    rows = db.scalars(select(ProductPrice).where(ProductPrice.product_id == product_id)).all()
    return {r.level_code: r.price for r in rows}


def _effective_price(db: Session, product: Product, level_code: str | None) -> Decimal:
    return resolve_product_price(product.retail_price, level_code, _price_map(db, product.id))


def _to_brief(db: Session, product: Product, level_code: str | None) -> ProductBrief:
    return ProductBrief(
        id=product.id,
        category_id=product.category_id,
        name=product.name,
        model=product.model,
        main_image=product.main_image,
        retail_price=product.retail_price,
        price=_effective_price(db, product, level_code),
        stock=product.stock,
        status=product.status,
    )


def list_products(
    db: Session,
    user: AuthUser | None,
    category_id: int | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PageResult[ProductBrief]:
    level_code = user.level_code if user else None
    stmt = select(Product).where(Product.status == ON_SALE_STATUS)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if keyword:
        stmt = stmt.where(Product.name.ilike(f"%{keyword}%"))

    # MVP 简化:先取 total 再取分页;量大时用 count() 子查询优化
    total = len(db.scalars(stmt).all())
    rows = db.scalars(stmt.order_by(Product.id).offset((page - 1) * page_size).limit(page_size)).all()
    items = [_to_brief(db, p, level_code) for p in rows]
    return PageResult(total=total, items=items)


def get_product(db: Session, user: AuthUser | None, product_id: int) -> ProductDetail:
    product = db.get(Product, product_id)
    if product is None or product.status != ON_SALE_STATUS:
        raise NotFoundError("商品不存在")

    level_code = user.level_code if user else None
    brief = _to_brief(db, product, level_code)
    images = db.scalars(
        select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.sort)
    ).all()
    specs = db.scalars(select(ProductSpec).where(ProductSpec.product_id == product_id)).all()
    prices = db.scalars(select(ProductPrice).where(ProductPrice.product_id == product_id)).all()

    # 分级价格仅管理员可见,避免游客/会员看到其他等级价
    level_prices = (
        [ProductPriceItem(level_code=p.level_code, price=p.price) for p in prices]
        if user is not None and user.role == "admin"
        else []
    )

    return ProductDetail(
        **brief.model_dump(),
        description=product.description,
        images=[ProductImageOut.model_validate(i) for i in images],
        specs=[ProductSpecOut.model_validate(s) for s in specs],
        level_prices=level_prices,
    )
