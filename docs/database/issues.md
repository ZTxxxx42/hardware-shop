# 五金商贸网站 · 数据层开发问题记录

> 记录本次数据层设计与实现中的问题 / 权衡 / 决策，供后续 review 与演进参考。

## 1. 为何不用 PostgreSQL enum 类型

- **问题**：订单状态、支付状态、角色、等级等枚举字段，是否使用 PG `ENUM` 类型？
- **决策**：统一使用 VARCHAR 字符串存储，不用 PG `ENUM` 类型。
- **理由**：PG `ENUM` 类型加值需 `ALTER TYPE ... ADD VALUE`，跨环境迁移与回滚繁琐，且与 Alembic autogenerate 配合不佳；VARCHAR + 领域层状态机校验更灵活，符合 MVP 快速迭代。架构文档明确「严格类型 + 强校验」是应用层（Pydantic/领域层）职责，而非把枚举锁死在 DDL 里。

## 2. 金额为何用 NUMERIC(10,2)

- **问题**：金额字段用 FLOAT/DOUBLE 还是 NUMERIC？
- **决策**：所有金额（`retail_price`、`price`、`product_amount/freight_amount/total_amount`、`order_item.price/subtotal`、`payment.amount`）统一 `Numeric(10, 2)`。
- **理由**：支付/订单场景要求精确十进制运算，浮点会引入 0.1 + 0.2 类误差；`NUMERIC` 为 PostgreSQL 精确十进制，适配 Python `Decimal`，与 FastAPI/Pydantic 强校验风格一致。10 位整数 + 2 位小数足以覆盖五金商贸金额量级。

## 3. 主键 ID 用 IDENTITY 还是 SERIAL

- **问题**：自增主键用 `SERIAL`（基于 SEQUENCE）还是 `GENERATED ... AS IDENTITY`？
- **决策**：`BIGINT GENERATED ALWAYS AS IDENTITY`，即 `BigInteger` + `Identity(always=True)`。
- **理由**：`IDENTITY` 是 SQL 标准，序列与表生命周期绑定更清晰、权限/所有权更安全；PostgreSQL 官方自 PG 10 起推荐 IDENTITY 优先于 SERIAL。`ALWAYS` 避免应用层显式插入绕过序列导致主键冲突。BIGINT 而非 INTEGER，为长期增长留余量。

## 4. `order` 与 `user` 是 SQL 保留字

- **问题**：表名 `order`、`user` 与 SQL 关键字冲突。
- **决策**：保持 `__tablename__ = "order"` / `"user"`，Python 模型类名用 `Order` / `User`；依赖 SQLAlchemy PostgreSQL 方言自动为保留字加引号生成 `"order"` / `"user"`。
- **理由**：表名/字段名严格以架构文档第 4 节为准，不能改名；SQLAlchemy 的 `PGIdentifierPreparer` 会正确引用（`ORDER`/`USER` 均在 PostgreSQL 保留字表），Alembic 手写迁移中同样自动处理，无需手工加引号。已验证编译产物为 `CREATE TABLE "order" (...)`、`CREATE TABLE "user" (...)`。

## 5. member_profile 与 customer_level 的主键特殊处理

- **问题**：架构 ER 图中 `member_profile` 以 `user_id` 为「PK·FK」（1:1 共享主键），`customer_level` 以 `code` 为自然主键；而任务通用约定写「主键 id 自增」。
- **决策**：遵循 ER 图/架构文档——`member_profile.user_id` 作共享主键（无独立 id、无 Identity），`customer_level.code` 作自然主键（无独立 id）。
- **理由**：1:1 扩展表用共享主键最直接且强制唯一；等级字典用稳定业务 code 作主键，被 `member_profile` / `product_price` 外键引用更可读。其余 11 张表均用自增 `id`。

## 6. `payment.paid_at` 不使用 server_default=now()

- **问题**：任务时间约定把 `payment.paid_at` 与 `order.created_at` 并列为「同理」使用 `server_default=func.now()`。
- **决策**：`paid_at` 用 `DateTime(timezone=True)` 且 `nullable=True`，**不设** `server_default`，由支付回调成功时显式写入。
- **理由**：`paid_at` 语义是「支付成功时间」，成功前必须为 NULL；若加 `server_default=now()`，PENDING 流水也会被自动打上时间戳，破坏语义与对账。此处对字面约定的偏差是修正而非遗漏。

## 7. 订单收货地址「快照」如何落地

- **问题**：架构文档对 `order` 只写「address 快照」，未指定列结构。
- **决策**：展开为 4 个快照列 `receiver_name / receiver_phone / receiver_region / receiver_detail`（VARCHAR，非空）。
- **理由**：与 `address` 表字段一一对应、可读可查、FastAPI 响应扁平；避免 JSONB（架构文档把 JSONB 定位为后续演进能力）。下单时固化，后续修改/删除地址不影响历史订单。

## 8. 外键 ondelete 策略取舍

- **问题**：13 张表间外键删除行为如何定级。
- **决策**：CASCADE（子资源随父删）、RESTRICT（保护主数据/字典/订单历史）、SET NULL（断开引用保留记录）三类，详见 `schema.md` 第 4 节。
- **理由**：
  - CASCADE：`member_profile/cart_item/address` 随 user，`product_image/spec/price` 随 product，`order_item/payment` 随 order（订单作为聚合根）。
  - RESTRICT：`product.category_id`、`order.user_id`、`level_code` 引用字典，避免误删产生孤儿或破坏财务主数据。
  - SET NULL：`category.parent_id`（删父分类子分类转顶级）、`order_item.product_id`（商品删除订单项保留快照）。

## 9. 索引取舍

- **问题**：哪些列建索引，如何避免冗余。
- **决策**：所有外键列建索引；查询热点 `product.category_id`、`order.user_id`、`order.status`、`payment.status`、`cart_item.user_id` 建索引。
- **理由**：PostgreSQL 不会自动为外键建索引，缺索引会导致父表删除/关联查询退化为全表扫描。`product_price.product_id` 与 `payment.order_id` 分别被复合唯一索引 `(product_id, level_code)`、`(order_id, channel)` 的最左前缀覆盖，不重复建单列索引。`product.status` 未单独建索引——任务热点清单未列，MVP 数据量下非必需，后续有筛选需求再加。

## 10. cart_item 是否加 (user_id, product_id) 唯一约束

- **问题**：同一用户对同一商品是否允许重复购物车行。
- **决策**：不加唯一约束，只对 user_id/product_id 建普通索引。
- **理由**：任务列出的唯一约束仅 4 个（username、order_no、product_price 组合、payment 组合），严格按此执行；「同商品加购合并数量」交由后端在写入时 `SELECT ... FOR UPDATE` 或 upsert 处理，保留应用层灵活性。

## 11. 枚举字段暂不加 CHECK 约束

- **问题**：状态/角色/渠道等 VARCHAR 字段是否加 `CHECK (status IN (...))`。
- **决策**：本期不加 CHECK，合法取值与状态流转由领域层/Pydantic 校验。
- **理由**：保持 MVP 简洁、迁移易变；架构把强校验放在应用层。后续需要 DB 级兜底时，可无损加 CHECK（新迁移写 `NOT VALID` + 回填后 `VALIDATE`）。

## 12. 驱动与连接串

- **问题**：psycopg3 与 Alembic 同步引擎如何接线。
- **决策**：`alembic.ini` 使用 `postgresql+psycopg://`（psycopg3），支持 `DATABASE_URL` 环境变量覆盖；`env.py` 加载 `app.models.Base.metadata` 供 autogenerate。
- **理由**：任务规定 `psycopg[binary]`；psycopg3 同时支持同步/异步，迁移用同步即可，应用层异步由后端 agent 决定。

## 13. 时间戳字段的分配（哪些表有 created_at/updated_at）

- **问题**：是否 13 张表全部加 created_at + updated_at。
- **决策**：可变业务实体（user/member_profile/category/product/product_price/cart_item/address/order）加 `created_at + updated_at`；只追加的不可变子记录（product_image/product_spec/order_item/payment）只加 `created_at`（payment 另含 `paid_at`）；静态字典 `customer_level` 不加时间戳。
- **理由**：updated_at 对只追加/不可变记录无意义，customer_level 为固定种子数据；按语义取舍，避免无意义字段。

## 14. 不做软删除 / 多租户

- **问题**：是否需要 deleted_at 软删除或 tenant_id 多租户。
- **决策**：不做。
- **理由**：MVP 单一商户、范围受控，任务明确「不做软删除/多租户，保持 MVP 简洁」；删除语义由外键级联表达即可。
