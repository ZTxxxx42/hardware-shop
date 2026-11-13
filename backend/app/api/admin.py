"""后台管理路由(role=admin)。

MVP 后台 CRUD 为无跨实体业务规则的简单持久化,直接在路由内处理;
涉及订单状态流转的「发货」复用 order_service,保证状态机收敛在领域层。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFoundError
from app.models import (  # 由 database agent 提供
    Category,
    Order,
    Payment,
    Product,
    ProductPrice,
)
from app.schemas.admin import (
    CategoryCreate,
    CategoryUpdate,
    CustomerLevelUpdate,
    ProductCreate,
    ProductPriceUpsert,
    ProductUpdate,
)
from app.schemas.catalog import CategoryOut, ProductBrief, ProductPriceItem
from app.schemas.common import PageResult
from app.schemas.member import ProfileOut
from app.schemas.order import OrderBrief, OrderDetail, OrderShipRequest
from app.schemas.payment import PaymentOut
from app.services import admin as admin_service
from app.services import order as order_service

router = APIRouter(prefix="/admin", tags=["管理"], dependencies=[Depends(require_admin)])


def _admin_brief(p: Product) -> ProductBrief:
    # 管理员以零售身份看价(架构设计.md 第 5 节)
    return ProductBrief(
        id=p.id,
        category_id=p.category_id,
        name=p.name,
        model=p.model,
        main_image=p.main_image,
        retail_price=p.retail_price,
        price=p.retail_price,
        stock=p.stock,
        status=p.status,
    )


# ---------- 分类 ----------

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    rows = db.scalars(select(Category).order_by(Category.sort, Category.id)).all()
    return [CategoryOut.model_validate(r) for r in rows]


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryOut:
    c = Category(name=payload.name, parent_id=payload.parent_id, sort=payload.sort)
    db.add(c)
    db.commit()
    db.refresh(c)
    return CategoryOut.model_validate(c)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)) -> CategoryOut:
    c = db.get(Category, category_id)
    if c is None:
        raise NotFoundError("分类不存在")
    for field in ("name", "parent_id", "sort"):
        value = getattr(payload, field)
        if value is not None:
            setattr(c, field, value)
    db.commit()
    db.refresh(c)
    return CategoryOut.model_validate(c)


@router.delete("/categories/{category_id}", status_code=204, response_model=None)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    c = db.get(Category, category_id)
    if c is None:
        raise NotFoundError("分类不存在")
    db.delete(c)
    db.commit()


# ---------- 商品 ----------

@router.get("/products", response_model=PageResult[ProductBrief])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PageResult[ProductBrief]:
    stmt = select(Product)
    total = len(db.scalars(stmt).all())
    rows = db.scalars(stmt.order_by(Product.id).offset((page - 1) * page_size).limit(page_size)).all()
    return PageResult(total=total, items=[_admin_brief(p) for p in rows])


@router.post("/products", response_model=ProductBrief, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductBrief:
    p = Product(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _admin_brief(p)


@router.get("/products/{product_id}", response_model=ProductBrief)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductBrief:
    p = db.get(Product, product_id)
    if p is None:
        raise NotFoundError("商品不存在")
    return _admin_brief(p)


@router.patch("/products/{product_id}", response_model=ProductBrief)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)) -> ProductBrief:
    p = db.get(Product, product_id)
    if p is None:
        raise NotFoundError("商品不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return _admin_brief(p)


@router.put("/products/{product_id}/prices", response_model=list[ProductPriceItem])
def upsert_product_prices(
    product_id: int,
    payload: ProductPriceUpsert,
    db: Session = Depends(get_db),
) -> list[ProductPriceItem]:
    """按等级批量设置价格,展开写入 product_price 冗余落库(架构设计.md 3.2)。"""
    if db.get(Product, product_id) is None:
        raise NotFoundError("商品不存在")
    for item in payload.prices:
        row = db.scalars(
            select(ProductPrice).where(
                ProductPrice.product_id == product_id,
                ProductPrice.level_code == item.level_code,
            )
        ).first()
        if row is None:
            db.add(ProductPrice(product_id=product_id, level_code=item.level_code, price=item.price))
        else:
            row.price = item.price
    db.commit()
    rows = db.scalars(select(ProductPrice).where(ProductPrice.product_id == product_id)).all()
    return [ProductPriceItem(level_code=r.level_code, price=r.price) for r in rows]


# ---------- 客户 ----------

@router.get("/customers", response_model=list[ProfileOut])
def list_customers(
    keyword: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
) -> list[ProfileOut]:
    """列出所有前台会员;keyword 按账号/手机/姓名模糊过滤。"""
    return admin_service.list_customers(db, keyword)


@router.patch("/customers/{user_id}", response_model=ProfileOut)
def set_customer_level(
    user_id: int,
    payload: CustomerLevelUpdate,
    db: Session = Depends(get_db),
) -> ProfileOut:
    """为客户指定会员等级(零售/批发/VIP)。"""
    return admin_service.set_customer_level(db, user_id, payload.level_code)


# ---------- 订单 ----------

@router.get("/orders", response_model=list[OrderBrief])
def list_orders(db: Session = Depends(get_db)) -> list[OrderBrief]:
    rows = db.scalars(select(Order).order_by(Order.id.desc())).all()
    return [
        OrderBrief(
            id=o.id,
            order_no=o.order_no,
            status=o.status,
            product_amount=o.product_amount,
            freight_amount=o.freight_amount,
            total_amount=o.total_amount,
            remark=o.remark,
            carrier=o.carrier,
            tracking_no=o.tracking_no,
            shipped_at=o.shipped_at,
            created_at=o.created_at,
        )
        for o in rows
    ]


@router.patch("/orders/{order_id}/ship", response_model=OrderDetail)
def ship_order(
    order_id: int,
    payload: OrderShipRequest,
    db: Session = Depends(get_db),
) -> OrderDetail:
    return order_service.ship_order(db, order_id, payload)


# ---------- 支付流水 ----------

@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db)) -> list[PaymentOut]:
    rows = db.scalars(select(Payment).order_by(Payment.id.desc())).all()
    return [PaymentOut.model_validate(r) for r in rows]
