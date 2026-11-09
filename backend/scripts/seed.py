"""填充五金商贸 MVP 联调种子数据。

在 backend 目录执行：``python -m scripts.seed`` 或 ``python scripts/seed.py``。
脚本按业务唯一键更新或插入，可重复执行，不会生成重复数据。
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

# 直接执行 scripts/seed.py 时，确保项目根目录可被导入。
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import hash_password, verify_password
from app.models import Category, CustomerLevel, MemberProfile, Product, ProductPrice, User

LEVELS = (
    ("retail", "零售客户", 1),
    ("wholesale", "批发客户", 2),
    ("vip", "VIP客户", 3),
)

CATEGORIES = ("手动工具", "电动工具", "紧固件", "建筑五金", "机械配件", "五金型材")

PRODUCTS = (
    {
        "name": "不锈钢外六角螺栓",
        "model": "M6-M20",
        "category": "紧固件",
        "description": "304 不锈钢外六角螺栓，适用于机械装配及一般工业紧固。",
        "retail_price": Decimal("12.80"),
        "stock": 1000,
        "main_image": "bolt",
    },
    {
        "name": "六角螺母",
        "model": "M6-M20",
        "category": "紧固件",
        "description": "标准六角螺母，规格齐全，可与对应螺栓配套使用。",
        "retail_price": Decimal("6.50"),
        "stock": 2000,
        "main_image": "nut",
    },
    {
        "name": "平垫圈",
        "model": "M6-M20",
        "category": "紧固件",
        "description": "通用平垫圈，用于分散紧固压力并保护连接件表面。",
        "retail_price": Decimal("4.80"),
        "stock": 3000,
        "main_image": "washer",
    },
    {
        "name": "膨胀螺栓",
        "model": "M8-M16",
        "category": "紧固件",
        "description": "适用于混凝土及砖墙固定安装，膨胀紧固，承载稳定。",
        "retail_price": Decimal("18.00"),
        "stock": 800,
        "main_image": "anchor",
    },
    {
        "name": "不锈钢合页",
        "model": "4寸",
        "category": "建筑五金",
        "description": "不锈钢平开合页，转动顺畅，适用于门窗及柜体安装。",
        "retail_price": Decimal("25.00"),
        "stock": 500,
        "main_image": "hinge",
    },
    {
        "name": "深沟球轴承",
        "model": "6200-6210",
        "category": "机械配件",
        "description": "低摩擦深沟球轴承，适用于电机、泵及通用机械设备。",
        "retail_price": Decimal("32.00"),
        "stock": 600,
        "main_image": "bearing",
    },
    {
        "name": "手动扳手",
        "model": "8-24mm",
        "category": "手动工具",
        "description": "铬钒钢手动扳手，表面防锈处理，适用于日常维修装配。",
        "retail_price": Decimal("45.00"),
        "stock": 300,
        "main_image": "wrench",
    },
    {
        "name": "电钻",
        "model": "220V/550W",
        "category": "电动工具",
        "description": "家用及轻工业手持电钻，支持正反转与无级调速。",
        "retail_price": Decimal("299.00"),
        "stock": 100,
        "main_image": "drill",
    },
)

USERS = (
    ("admin", "admin123", "admin", None),
    ("member", "member123", "member", "wholesale"),
)


def upsert_levels(session: Session) -> None:
    for code, name, sort in LEVELS:
        level = session.get(CustomerLevel, code)
        if level is None:
            level = CustomerLevel(code=code)
            session.add(level)
        level.name = name
        level.sort = sort


def upsert_categories(session: Session) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for sort, name in enumerate(CATEGORIES, start=1):
        category = session.scalar(
            select(Category).where(Category.name == name, Category.parent_id.is_(None))
        )
        if category is None:
            category = Category(name=name)
            session.add(category)
        category.parent_id = None
        category.sort = sort
        categories[name] = category
    session.flush()
    return categories


def upsert_products(session: Session, categories: dict[str, Category]) -> None:
    for item in PRODUCTS:
        product = session.scalar(select(Product).where(Product.name == item["name"]))
        if product is None:
            product = Product(name=item["name"])
            session.add(product)
        product.category = categories[item["category"]]
        product.model = item["model"]
        product.description = item["description"]
        product.retail_price = item["retail_price"]
        product.stock = item["stock"]
        product.status = "ON_SALE"
        product.main_image = item["main_image"]
        session.flush()

        for level_code, multiplier in (("wholesale", "0.85"), ("vip", "0.7")):
            price = session.scalar(
                select(ProductPrice).where(
                    ProductPrice.product_id == product.id,
                    ProductPrice.level_code == level_code,
                )
            )
            if price is None:
                price = ProductPrice(product=product, level_code=level_code)
                session.add(price)
            price.price = (item["retail_price"] * Decimal(multiplier)).quantize(Decimal("0.01"))


def upsert_users(session: Session) -> None:
    for username, password, role, level_code in USERS:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=hash_password(password))
            session.add(user)
        elif not verify_password(password, user.password_hash):
            user.password_hash = hash_password(password)
        user.role = role
        session.flush()

        if level_code is None:
            continue
        profile = session.get(MemberProfile, user.id)
        if profile is None:
            profile = MemberProfile(user=user)
            session.add(profile)
        profile.level_code = level_code


def seed() -> None:
    with SessionLocal() as session:
        with session.begin():
            upsert_levels(session)
            categories = upsert_categories(session)
            upsert_products(session, categories)
            upsert_users(session)

    print(
        f"种子数据完成：{len(LEVELS)} 个客户等级，{len(CATEGORIES)} 个顶级分类，"
        f"{len(PRODUCTS)} 个商品，{len(PRODUCTS) * 2} 条分级价格，"
        f"{len(USERS)} 个测试用户，1 份会员资料。"
    )


if __name__ == "__main__":
    seed()
