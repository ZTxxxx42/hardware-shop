# 五金商贸网站 · 数据模型说明（PostgreSQL 16）

> 版本 v1.0 ｜ 2026-11-08 ｜ 依据：`docs/architecture/架构设计.md` 第 4 节（唯一权威数据源）
> 实现：`backend/app/models/`（SQLAlchemy 2.0）+ `backend/alembic/versions/0001_initial_schema.py`、`0002_wechat_account_deletion_order_logistics.py`（Alembic 1.13）

## 1. 统一约定

| 项 | 约定 | 说明 |
| --- | --- | --- |
| 数据库 | PostgreSQL 16 | 驱动 psycopg3（`postgresql+psycopg://`） |
| ORM | SQLAlchemy 2.0 | `DeclarativeBase` + `Mapped` / `mapped_column` |
| 主键 | `BIGINT GENERATED ALWAYS AS IDENTITY` | `BigInteger` + `Identity(always=True)` |
| 外键列名 | `<被引用表单数>_id` | 如 `user_id` / `product_id` / `category_id` / `order_id`；自引用 `category.parent_id` |
| 时间 | `DateTime(timezone=True)`（timestamptz） | `created_at` / `updated_at` / `paid_at` |
| 时间默认值 | `server_default=now()` | `updated_at` 另配 ORM `onupdate=now()` |
| 金额 | `Numeric(10, 2)` | 精确十进制，避免浮点误差 |
| 枚举 | VARCHAR 字符串 | 不用 PG enum 类型，便于迁移与扩展 |

枚举取值约定：

| 字段 | 取值 |
| --- | --- |
| `user.role` | `member` / `admin` |
| `user.deletion_status` | `NONE` / `PENDING` |
| `customer_level.code` | `retail` / `wholesale` / `vip` |
| `product.status` | `ON_SALE` / `OFF_SALE` |
| `order.status` | `PENDING_PAYMENT` / `PAID` / `SHIPPED` / `COMPLETED` / `CANCELLED` |
| `payment.channel` | `wechat` / `alipay` |
| `payment.status` | `PENDING` / `SUCCESS` / `FAILED` |

> 状态值以 VARCHAR 存储；合法流转（状态机）在领域层校验，数据库层不额外加 CHECK（详见 `issues.md`）。

## 2. 表清单（13 张）

| # | 表 | 模型类 | 主键 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `user` | `User` | `id` 自增 | 用户（role 区分买家/管理员） |
| 2 | `customer_level` | `CustomerLevel` | `code` 自然主键 | 客户等级字典（零售/批发/VIP） |
| 3 | `member_profile` | `MemberProfile` | `user_id` 共享主键 | 会员资料（1:1 user） |
| 4 | `category` | `Category` | `id` 自增 | 多级分类（自引用） |
| 5 | `product` | `Product` | `id` 自增 | 商品 SPU |
| 6 | `product_image` | `ProductImage` | `id` 自增 | 商品多图 |
| 7 | `product_spec` | `ProductSpec` | `id` 自增 | 规格属性文本 |
| 8 | `product_price` | `ProductPrice` | `id` 自增 | 分级价格（商品 × 等级） |
| 9 | `cart_item` | `CartItem` | `id` 自增 | 购物车项 |
| 10 | `address` | `Address` | `id` 自增 | 收货地址 |
| 11 | `order` | `Order` | `id` 自增 | 订单主表 |
| 12 | `order_item` | `OrderItem` | `id` 自增 | 订单项（价格/名称快照） |
| 13 | `payment` | `Payment` | `id` 自增 | 支付流水 |

## 3. 字段定义

### 3.1 user

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| username | VARCHAR(64) | NOT NULL, UNIQUE | 登录名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| role | VARCHAR(16) | NOT NULL, DEFAULT 'member' | member / admin |
| phone | VARCHAR(20) | NULL | 手机号 |
| openid | VARCHAR(64) | NULL, UNIQUE | 微信小程序 openid（微信登录绑定） |
| unionid | VARCHAR(64) | NULL, INDEX | 微信开放平台 unionid（可选，回填用） |
| deletion_status | VARCHAR(16) | NOT NULL, DEFAULT 'NONE' | 注销状态：NONE / PENDING |
| deletion_requested_at | TIMESTAMPTZ | NULL | 注销申请时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`uq_user_username`（唯一）、`uq_user_openid`（唯一）、`ix_user_unionid`（unionid）。

### 3.2 customer_level

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| code | VARCHAR(32) | PK | retail / wholesale / vip |
| name | VARCHAR(64) | NOT NULL | 等级名称 |
| sort | INTEGER | NOT NULL, DEFAULT 0 | 排序 |

> 静态字典表，无 `id`、无时间戳。

### 3.3 member_profile

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| user_id | BIGINT | PK, FK→user.id ON DELETE CASCADE | 与 user 1:1 共享主键 |
| level_code | VARCHAR(32) | NOT NULL, FK→customer_level.code ON DELETE RESTRICT | 等级 |
| real_name | VARCHAR(64) | NULL | 真实姓名 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_member_profile_level_code`（level_code）。

### 3.4 category

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| parent_id | BIGINT | NULL, FK→category.id ON DELETE SET NULL | 自引用，NULL 为顶级分类 |
| name | VARCHAR(128) | NOT NULL | |
| sort | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_category_parent_id`（parent_id）。

### 3.5 product

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| category_id | BIGINT | NOT NULL, FK→category.id ON DELETE RESTRICT | |
| name | VARCHAR(255) | NOT NULL | 商品名 |
| model | VARCHAR(128) | NULL | 型号 |
| description | TEXT | NULL | 描述 |
| retail_price | NUMERIC(10,2) | NOT NULL | 零售价（基础价） |
| stock | INTEGER | NOT NULL, DEFAULT 0 | 库存 |
| status | VARCHAR(16) | NOT NULL, DEFAULT 'ON_SALE' | ON_SALE / OFF_SALE |
| main_image | VARCHAR(512) | NULL | 主图 URL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_product_category_id`（category_id，查询热点）。

### 3.6 product_image

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| product_id | BIGINT | NOT NULL, FK→product.id ON DELETE CASCADE | |
| url | VARCHAR(512) | NOT NULL | |
| sort | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_product_image_product_id`（product_id）。

### 3.7 product_spec

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| product_id | BIGINT | NOT NULL, FK→product.id ON DELETE CASCADE | |
| spec_name | VARCHAR(128) | NOT NULL | 规格名（如「材质」） |
| spec_value | VARCHAR(255) | NOT NULL | 规格值（如「不锈钢」） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_product_spec_product_id`（product_id）。

### 3.8 product_price

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| product_id | BIGINT | NOT NULL, FK→product.id ON DELETE CASCADE | |
| level_code | VARCHAR(32) | NOT NULL, FK→customer_level.code ON DELETE RESTRICT | |
| price | NUMERIC(10,2) | NOT NULL | 等级价 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

约束/索引：
- UNIQUE `uq_product_price_product_level`（product_id, level_code）——保证同商品同等级仅一条价格。
- `ix_product_price_level_code`（level_code）。

### 3.9 cart_item

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| user_id | BIGINT | NOT NULL, FK→user.id ON DELETE CASCADE | |
| product_id | BIGINT | NOT NULL, FK→product.id ON DELETE CASCADE | |
| quantity | INTEGER | NOT NULL, DEFAULT 1 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_cart_item_user_id`（user_id，查询热点）、`ix_cart_item_product_id`（product_id）。

### 3.10 address

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| user_id | BIGINT | NOT NULL, FK→user.id ON DELETE CASCADE | |
| receiver | VARCHAR(64) | NOT NULL | 收货人 |
| phone | VARCHAR(20) | NOT NULL | |
| region | VARCHAR(255) | NOT NULL | 地区 |
| detail | VARCHAR(512) | NOT NULL | 详细地址 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_address_user_id`（user_id）。

### 3.11 order

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| order_no | VARCHAR(32) | NOT NULL, UNIQUE | 订单号 |
| user_id | BIGINT | NOT NULL, FK→user.id ON DELETE RESTRICT | |
| status | VARCHAR(32) | NOT NULL, DEFAULT 'PENDING_PAYMENT' | 见状态机 |
| product_amount | NUMERIC(10,2) | NOT NULL, DEFAULT 0 | 商品总额 |
| freight_amount | NUMERIC(10,2) | NOT NULL, DEFAULT 0 | 运费 |
| total_amount | NUMERIC(10,2) | NOT NULL, DEFAULT 0 | 应付总额 |
| receiver_name | VARCHAR(64) | NOT NULL | 收货人快照 |
| receiver_phone | VARCHAR(20) | NOT NULL | 电话快照 |
| receiver_region | VARCHAR(255) | NOT NULL | 地区快照 |
| receiver_detail | VARCHAR(512) | NOT NULL | 详细地址快照 |
| remark | VARCHAR(500) | NULL | 订单备注 |
| carrier | VARCHAR(64) | NULL | 物流公司（发货时写入） |
| tracking_no | VARCHAR(64) | NULL | 物流单号（发货时写入） |
| shipped_at | TIMESTAMPTZ | NULL | 发货时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 下单时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

约束/索引：
- UNIQUE `uq_order_order_no`（order_no）。
- `ix_order_user_id`（user_id，查询热点）、`ix_order_status`（status，查询热点）。

> `order` 为 SQL 保留字，SQLAlchemy PostgreSQL 方言自动加引号生成 `"order"`；Python 模型类名使用 `Order`。

> 收货地址采用 4 个快照列（receiver_name / receiver_phone / receiver_region / receiver_detail），下单时固化，避免后续修改地址影响历史订单。

### 3.12 order_item

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| order_id | BIGINT | NOT NULL, FK→order.id ON DELETE CASCADE | |
| product_id | BIGINT | NULL, FK→product.id ON DELETE SET NULL | 商品删除后置空 |
| product_name | VARCHAR(255) | NOT NULL | 商品名快照 |
| price | NUMERIC(10,2) | NOT NULL | 单价快照 |
| quantity | INTEGER | NOT NULL | |
| subtotal | NUMERIC(10,2) | NOT NULL | 小计（price × quantity） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

索引：`ix_order_item_order_id`（order_id）、`ix_order_item_product_id`（product_id）。

### 3.13 payment

| 字段 | 类型 | 约束/默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PK, IDENTITY(ALWAYS) | |
| order_id | BIGINT | NOT NULL, FK→order.id ON DELETE CASCADE | |
| channel | VARCHAR(16) | NOT NULL | wechat / alipay |
| trade_no | VARCHAR(64) | NULL | 第三方交易号 |
| amount | NUMERIC(10,2) | NOT NULL | 支付金额 |
| status | VARCHAR(16) | NOT NULL, DEFAULT 'PENDING' | PENDING / SUCCESS / FAILED |
| paid_at | TIMESTAMPTZ | NULL | 支付成功时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

约束/索引：
- UNIQUE `uq_payment_order_channel`（order_id, channel）——支付幂等唯一键，防重复回调。
- `ix_payment_status`（status，查询热点）。

> `paid_at` 成功前为 NULL，不设 `server_default`，由支付回调成功时写入。

## 4. 表间关系

```
user 1 ──── 1 member_profile N ──── 1 customer_level
user 1 ──── N cart_item   N ──── 1 product
user 1 ──── N address
user 1 ──── N order
category 1 ──── N category（parent_id 自引用，多级树）
category 1 ──── N product
product 1 ──── N product_image
product 1 ──── N product_spec
product 1 ──── N product_price N ──── 1 customer_level
order 1 ──── N order_item N ──── 1 product（product_id 可空，保快照）
order 1 ──── N payment
```

外键删除策略：

| 关系 | ON DELETE | 理由 |
| --- | --- | --- |
| member_profile.user_id → user | CASCADE | 1:1 扩展，随用户删除 |
| cart_item.user_id / product_id | CASCADE | 购物车项随父删除 |
| address.user_id | CASCADE | 地址随用户删除 |
| product_image / product_spec / product_price → product | CASCADE | 商品子资源随商品删除 |
| order_item.order_id → order | CASCADE | 订单项随订单删除 |
| payment.order_id → order | CASCADE | 支付流水随订单删除（MVP 无订单物理删除路径） |
| member_profile.level_code / product_price.level_code → customer_level | RESTRICT | 保护等级字典 |
| product.category_id → category | RESTRICT | 有商品的分类不可删 |
| order.user_id → user | RESTRICT | 保护订单历史 |
| category.parent_id → category | SET NULL | 删除父分类时子分类转顶级 |
| order_item.product_id → product | SET NULL | 商品删除后订单项保留快照 |

## 5. 索引汇总

| 索引 | 表.列 | 类型 | 目的 |
| --- | --- | --- | --- |
| uq_user_username | user.username | UNIQUE | 登录唯一 |
| uq_user_openid | user.openid | UNIQUE | 微信登录唯一 |
| ix_user_unionid | user.unionid | 普通 | 微信 unionid 查询 |
| uq_order_order_no | order.order_no | UNIQUE | 订单号唯一 |
| uq_product_price_product_level | product_price(product_id, level_code) | UNIQUE | 分级价唯一 + 覆盖 product_id 外键 |
| uq_payment_order_channel | payment(order_id, channel) | UNIQUE | 支付幂等 + 覆盖 order_id 外键 |
| ix_member_profile_level_code | member_profile.level_code | 普通 | 外键 |
| ix_category_parent_id | category.parent_id | 普通 | 外键/自引用 |
| ix_product_category_id | product.category_id | 普通 | 外键 + 分类列表热点 |
| ix_product_image_product_id | product_image.product_id | 普通 | 外键 |
| ix_product_spec_product_id | product_spec.product_id | 普通 | 外键 |
| ix_product_price_level_code | product_price.level_code | 普通 | 外键 |
| ix_cart_item_user_id | cart_item.user_id | 普通 | 外键 + 我的购物车热点 |
| ix_cart_item_product_id | cart_item.product_id | 普通 | 外键 |
| ix_address_user_id | address.user_id | 普通 | 外键 |
| ix_order_user_id | order.user_id | 普通 | 外键 + 我的订单热点 |
| ix_order_status | order.status | 普通 | 订单状态筛选热点 |
| ix_order_item_order_id | order_item.order_id | 普通 | 外键 |
| ix_order_item_product_id | order_item.product_id | 普通 | 外键 |
| ix_payment_status | payment.status | 普通 | 支付状态对账热点 |

设计要点：所有外键列均有索引；`product_price.product_id` 与 `payment.order_id` 由复合唯一索引的最左前缀覆盖，不重复建单列索引。

## 6. 设计要点

1. **支付幂等唯一键**：`payment(order_id, channel)` 唯一约束，配合订单状态机与事务，保证支付回调重复通知不重复发货/扣减。
2. **金额精度**：金额统一 `Numeric(10,2)`，杜绝 FLOAT/DOUBLE 浮点误差，契合支付场景强校验。
3. **时间戳**：统一 `timestamptz`（带时区），数据库层 `now()` 兜底，`updated_at` 由 ORM `onupdate` 维护。
4. **状态机约定**：订单 `PENDING_PAYMENT → PAID → SHIPPED → COMPLETED`，可取消为 `CANCELLED`；支付 `PENDING → SUCCESS/FAILED`。合法流转由领域层校验。
5. **快照防改价**：`order_item.product_name/price` 与 `order` 收货地址均为下单时快照，历史订单不受后续商品/地址变更影响。
6. **不使用 PG enum / 多租户**：保持 MVP 简洁，枚举用 VARCHAR，商品/地址等删除策略依赖外键级联。账号注销为「申请制软状态」例外：`user.deletion_status` 记录 PENDING，不物理删除账号与历史订单。
7. **微信登录绑定**：`user.openid` 唯一，微信登录按 openid 幂等匹配账号；`unionid` 建索引供开放平台关联回填。
