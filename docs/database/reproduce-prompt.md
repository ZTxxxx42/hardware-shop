# 五金商贸网站 · 数据层复现提示词（严格约束版）

> 用途：本文件是「可复现交付物」。任何 agent 拿到本文件 + `docs/architecture/架构设计.md`（唯一权威数据源），即可**完整复现**本次数据层产出的全部内容。
> 约束优先级：架构设计.md 第 4 节 ＞ 本文件 ＞ 其他推测。遇到冲突以架构文档为准并记录。

---

## 1. 任务目标

为「五金商贸网站」MVP 设计并落地 PostgreSQL 数据层，产出：

1. SQLAlchemy 2.0 ORM 模型（13 张表）。
2. Alembic 1.13 初始迁移（建 13 表 + 索引 + 约束，与模型一致）。
3. 数据模型说明文档。
4. 问题记录文档。
5. 本复现提示词文件（即你要产出的 `reproduce-prompt.md`）。

## 2. 权威输入

- 必读：`docs/architecture/架构设计.md`
  - 第 1 节技术选型：PostgreSQL 16、SQLAlchemy 2.0、Alembic 1.13、psycopg3（`psycopg[binary]`）、FastAPI/Pydantic v2。
  - 第 4 节数据模型：13 张表、字段、关系、唯一约束（唯一权威字段来源）。
- 参考：`docs/architecture/er-diagram.drawio`（完整 ER 图，含字段与基数，`member_profile.user_id` 为 PK·FK、`customer_level.code` 为 PK 等细节以此为准）。
- 可选 skill：`~/.agents/skills/postgresql-database-engineering/SKILL.md`（索引/迁移规范，按需读）。

## 3. 技术栈与硬性约定（必须严格遵守）

- PostgreSQL 16 + SQLAlchemy 2.0（declarative，`Mapped`/`mapped_column` 风格）+ Alembic 1.13 + psycopg3。
- **表名/模型类名/字段名严格以架构设计.md 第 4 节为准，不增删字段、不改名。** 13 表：`user`、`customer_level`、`member_profile`、`category`、`product`、`product_image`、`product_spec`、`product_price`、`cart_item`、`address`、`order`、`order_item`、`payment`。
- 主键 `id`：`BigInteger` + `Identity(always=True)`（即 `BIGINT GENERATED ALWAYS AS IDENTITY`）。**例外**：`customer_level` 以 `code`（VARCHAR）为主键；`member_profile` 以 `user_id`（BigInteger，FK→user.id）为主键（与 user 1:1 共享主键）。
- 外键列名：`<被引用表单数>_id`，如 `user_id`/`product_id`/`category_id`/`order_id`；自引用 `category.parent_id`。
- 时间：`created_at`/`updated_at` 用 `DateTime(timezone=True)` + `server_default=func.now()`；`order.created_at` 同理。`updated_at` 另加 ORM `onupdate=func.now()`。
- 金额统一 `Numeric(10,2)`：`product.retail_price`、`product_price.price`、`order.product_amount/freight_amount/total_amount`、`order_item.price/subtotal`、`payment.amount`。
- 状态/枚举用 VARCHAR 字符串（**不用 PG enum 类型**，不加 CHECK）：
  - 订单 `PENDING_PAYMENT/PAID/SHIPPED/COMPLETED/CANCELLED`；
  - 支付 `PENDING/SUCCESS/FAILED`；
  - 角色 `member/admin`；
  - 等级 code `retail/wholesale/vip`；
  - 商品状态 `ON_SALE/OFF_SALE`；支付渠道 `wechat/alipay`。
- 唯一约束（仅这 4 个，不额外添加）：`product_price(product_id, level_code)`、`payment(order_id, channel)`、`order(order_no)`、`user(username)`。
- 索引：所有外键列建索引；查询热点 `product.category_id`、`order.user_id`、`order.status`、`payment.status`、`cart_item.user_id` 建索引。
- 定义 SQLAlchemy `relationship`（供后端用）与合理的 `ondelete`/级联；`order` 是 SQL 保留字，SQLAlchemy 方言会自动加引号，模型类名用 `Order`，注意在 issues 记录。
- 不做软删除/多租户，保持 MVP 简洁。

## 4. 13 张表完整字段清单（字段名/类型/约束/索引）

> 命名约定：约束名 `uq_<表>_<列>`、复合唯一名 `uq_product_price_product_level`、`uq_payment_order_channel`；索引名 `ix_<表>_<列>`。默认值字符串用 `text("'X'")`，数值用裸字符串 `"0"`/`"1"`。

### 4.1 user（模型类 User）
- id BIGINT PK Identity(always)
- username VARCHAR(64) NOT NULL UNIQUE（uq_user_username）
- password_hash VARCHAR(255) NOT NULL
- role VARCHAR(16) NOT NULL DEFAULT 'member'
- phone VARCHAR(20) NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.2 customer_level（模型类 CustomerLevel，无 id、无时间戳）
- code VARCHAR(32) PK（retail/wholesale/vip）
- name VARCHAR(64) NOT NULL
- sort INTEGER NOT NULL DEFAULT 0

### 4.3 member_profile（模型类 MemberProfile）
- user_id BIGINT PK，FK→user.id ON DELETE CASCADE（共享主键）
- level_code VARCHAR(32) NOT NULL，FK→customer_level.code ON DELETE RESTRICT，索引 ix_member_profile_level_code
- real_name VARCHAR(64) NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.4 category（模型类 Category，自引用多级树）
- id BIGINT PK Identity(always)
- parent_id BIGINT NULL，FK→category.id ON DELETE SET NULL，索引 ix_category_parent_id
- name VARCHAR(128) NOT NULL
- sort INTEGER NOT NULL DEFAULT 0
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.5 product（模型类 Product）
- id BIGINT PK Identity(always)
- category_id BIGINT NOT NULL，FK→category.id ON DELETE RESTRICT，索引 ix_product_category_id（热点）
- name VARCHAR(255) NOT NULL
- model VARCHAR(128) NULL
- description TEXT NULL
- retail_price NUMERIC(10,2) NOT NULL
- stock INTEGER NOT NULL DEFAULT 0
- status VARCHAR(16) NOT NULL DEFAULT 'ON_SALE'
- main_image VARCHAR(512) NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.6 product_image（模型类 ProductImage，仅 created_at）
- id BIGINT PK Identity(always)
- product_id BIGINT NOT NULL，FK→product.id ON DELETE CASCADE，索引 ix_product_image_product_id
- url VARCHAR(512) NOT NULL
- sort INTEGER NOT NULL DEFAULT 0
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.7 product_spec（模型类 ProductSpec，仅 created_at）
- id BIGINT PK Identity(always)
- product_id BIGINT NOT NULL，FK→product.id ON DELETE CASCADE，索引 ix_product_spec_product_id
- spec_name VARCHAR(128) NOT NULL
- spec_value VARCHAR(255) NOT NULL
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.8 product_price（模型类 ProductPrice）
- id BIGINT PK Identity(always)
- product_id BIGINT NOT NULL，FK→product.id ON DELETE CASCADE（由复合唯一索引覆盖，不单独建索引）
- level_code VARCHAR(32) NOT NULL，FK→customer_level.code ON DELETE RESTRICT，索引 ix_product_price_level_code
- price NUMERIC(10,2) NOT NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
- UNIQUE(product_id, level_code) 名 uq_product_price_product_level

### 4.9 cart_item（模型类 CartItem）
- id BIGINT PK Identity(always)
- user_id BIGINT NOT NULL，FK→user.id ON DELETE CASCADE，索引 ix_cart_item_user_id（热点）
- product_id BIGINT NOT NULL，FK→product.id ON DELETE CASCADE，索引 ix_cart_item_product_id
- quantity INTEGER NOT NULL DEFAULT 1
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.10 address（模型类 Address）
- id BIGINT PK Identity(always)
- user_id BIGINT NOT NULL，FK→user.id ON DELETE CASCADE，索引 ix_address_user_id
- receiver VARCHAR(64) NOT NULL
- phone VARCHAR(20) NOT NULL
- region VARCHAR(255) NOT NULL
- detail VARCHAR(512) NOT NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.11 order（模型类 Order；`order` 为保留字，方言自动加引号）
- id BIGINT PK Identity(always)
- order_no VARCHAR(32) NOT NULL UNIQUE（uq_order_order_no）
- user_id BIGINT NOT NULL，FK→user.id ON DELETE RESTRICT，索引 ix_order_user_id（热点）
- status VARCHAR(32) NOT NULL DEFAULT 'PENDING_PAYMENT'，索引 ix_order_status（热点）
- product_amount NUMERIC(10,2) NOT NULL DEFAULT 0
- freight_amount NUMERIC(10,2) NOT NULL DEFAULT 0
- total_amount NUMERIC(10,2) NOT NULL DEFAULT 0
- receiver_name VARCHAR(64) NOT NULL（地址快照）
- receiver_phone VARCHAR(20) NOT NULL（快照）
- receiver_region VARCHAR(255) NOT NULL（快照）
- receiver_detail VARCHAR(512) NOT NULL（快照）
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.12 order_item（模型类 OrderItem，仅 created_at）
- id BIGINT PK Identity(always)
- order_id BIGINT NOT NULL，FK→order.id ON DELETE CASCADE，索引 ix_order_item_order_id
- product_id BIGINT NULL，FK→product.id ON DELETE SET NULL，索引 ix_order_item_product_id
- product_name VARCHAR(255) NOT NULL（名称快照）
- price NUMERIC(10,2) NOT NULL（单价快照）
- quantity INTEGER NOT NULL
- subtotal NUMERIC(10,2) NOT NULL
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

### 4.13 payment（模型类 Payment，仅 created_at + paid_at）
- id BIGINT PK Identity(always)
- order_id BIGINT NOT NULL，FK→order.id ON DELETE CASCADE（由复合唯一索引覆盖，不单独建索引）
- channel VARCHAR(16) NOT NULL（wechat/alipay）
- trade_no VARCHAR(64) NULL
- amount NUMERIC(10,2) NOT NULL
- status VARCHAR(16) NOT NULL DEFAULT 'PENDING'，索引 ix_payment_status（热点）
- paid_at TIMESTAMPTZ NULL（成功前为 NULL，不设 server_default，回调成功时写入）
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- UNIQUE(order_id, channel) 名 uq_payment_order_channel

## 5. relationship 与级联约定

- user 1:1 member_profile（`uselist=False`，cascade delete-orphan，passive_deletes=True）
- user 1:N cart_item / address / order；order N:1 user
- customer_level 1:N member_profile / product_price
- category 自引用：`parent`（remote_side="Category.id"）/ `children`
- category 1:N product；product 1:N image/spec/price/cart_item/order_item
- order 1:N order_item / payment（cascade delete-orphan）
- ondelete：CASCADE（member_profile→user、cart_item→user/product、address→user、product_image/spec/price→product、order_item→order、payment→order）；RESTRICT（product→category、order→user、level_code→customer_level）；SET NULL（category.parent_id、order_item.product_id）。

## 6. 产出文件清单与路径（必须全部写入，路径固定）

1. `backend/app/models/base.py`：`Base(DeclarativeBase)` + 命名约定 + `IntPkMixin`（id BigInteger Identity(always) PK）+ `TimestampMixin`（created_at/updated_at）+ `CreatedAtMixin`（仅 created_at）。
2. `backend/app/models/user.py`：User、CustomerLevel、MemberProfile、Address。
3. `backend/app/models/catalog.py`：Category、Product、ProductImage、ProductSpec、ProductPrice。
4. `backend/app/models/cart.py`：CartItem。
5. `backend/app/models/order.py`：Order、OrderItem、Payment。
6. `backend/app/models/__init__.py`：统一导出 Base 与 13 个模型类。
7. `backend/alembic.ini`：`script_location = alembic`、`postgresql+psycopg://` 连接串、日志配置。
8. `backend/alembic/env.py`：加载 `app.models.Base.metadata`，支持 `DATABASE_URL` 环境变量覆盖，在线/离线迁移。
9. `backend/alembic/script.py.mako`：标准迁移模板。
10. `backend/alembic/versions/0001_initial_schema.py`：`revision="0001"`、`down_revision=None`；`upgrade()` 按依赖顺序建 13 表 + 索引 + 约束，`downgrade()` 反向 drop。
11. `docs/database/schema.md`：每表字段/类型/约束/索引、表间关系、设计要点（幂等唯一键、金额精度、时间戳、状态机约定）。
12. `docs/database/issues.md`：问题/决策/理由记录（为何不用 PG enum、为何 NUMERIC、IDENTITY vs SERIAL、`order` 保留字、索引取舍、外键 ondelete、member_profile/customer_level 主键例外、paid_at 不设 server_default 等）。
13. `docs/database/reproduce-prompt.md`：本文件（自足完整）。

**目录约束**：只写上述路径；**不要碰** `backend/app/schemas|api|services|domain|core|main.py` 与 `backend/requirements.txt`（由后端 agent 负责）。

## 7. 验收标准

1. 模型可被 SQLAlchemy 加载：从 `backend/` 目录 `python -c "from app.models import Base, User, Order; print(len(Base.metadata.tables))"` 输出 13。
2. Alembic 迁移可执行：配置好 PostgreSQL 后 `alembic upgrade head` 成功建 13 表；`alembic downgrade base` 可回滚。
3. 与架构文档一致：13 张表名、字段名、关系、唯一约束一一对应，无增删改字段。
4. 类型/约束/索引符合第 3、4、5 节约定；`order` 表名被正确引用。
5. `alembic check` 或 autogenerate 对比模型与迁移无差异（约束/索引命名一致）。

## 8. 完成报告要求

- 报告产出文件路径清单、13 表清单、关键约束与索引、issues 要点、复现提示词路径。
- **不要执行 git 提交**（由主 agent 统一提交）。
- 用简体中文，专业简洁。
