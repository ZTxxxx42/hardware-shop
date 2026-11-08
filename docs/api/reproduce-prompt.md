# 复现提示词:五金商贸 MVP 后端 FastAPI 分层脚手架

> 本文件为**严格约束提示词**。任何拿到本文件 + `docs/architecture/架构设计.md` 的 agent,
> 均应能**自足复现** `backend/` 全部代码与 `docs/api/` 全部文档,无需额外上下文。
> 本文件即权威任务描述;与架构设计.md 冲突时,以架构设计.md 为数据源、以本文件为工程落地约束。

---

## 1. 任务目标

为「五金商贸网站」MVP 搭建 FastAPI **分层脚手架** + 核心实体(Pydantic schema)+ API 接口说明文档 + issues 记录 + 本复现提示词文件。

产出两层:
1. `backend/` —— 可运行的最小骨架 + 核心路由/服务/领域规则的接口与实现(可含 TODO 标注待联调项)。
2. `docs/api/` —— `api.md`(接口说明)、`issues.md`(问题/决策/理由)、`reproduce-prompt.md`(本文件)。

## 2. 权威输入

- 唯一权威数据源:`C:/Users/朱涛/Desktop/五金商贸/docs/architecture/架构设计.md`
  - 重点:第 1 节技术选型(FastAPI/Pydantic v2/SQLAlchemy/JWT);
  - 第 2 节后端分层(表现层/应用服务层/领域层/数据访问层);
  - 第 3 节业务流程与订单状态机;
  - 第 4 节数据模型(13 表);
  - 第 5 节权限模型;
  - 第 6 节支付回调与幂等。
- 按需读 skill:`C:/Users/朱涛/.agents/skills/python-design-patterns/SKILL.md`(分层与职责划分、KISS/SRP/组合优于继承)。

## 3. 技术栈

FastAPI 0.115+ / Python 3.13 / Pydantic v2 / SQLAlchemy 2.0 / JWT(PyJWT 或 python-jose)+ passlib[bcrypt] / pydantic-settings。

`requirements.txt` 至少含:fastapi、uvicorn[standard]、sqlalchemy、alembic、psycopg[binary]、pydantic-settings、PyJWT、passlib[bcrypt]、python-multipart。**passlib 与 bcrypt 4.1+ 不兼容,需固定 `bcrypt==4.0.1`。**

## 4. 目录与分层(严格遵循架构设计.md 第 2 节)

```
backend/
├── requirements.txt
├── .env.example
└── app/
    ├── __init__.py
    ├── main.py                 # FastAPI 实例、路由注册、CORS、异常处理、/healthz
    ├── core/
    │   ├── config.py           # pydantic-settings(SECRET_KEY/DATABASE_URL/CORS_ORIGINS 等)
    │   ├── db.py               # engine + SessionLocal(应用层会话,不在 models 中)
    │   ├── exceptions.py       # 统一业务异常(AppError/NotFoundError/BusinessError/...)
    │   ├── security.py         # JWT 生成/校验 + bcrypt 密码哈希 + AuthUser dataclass
    │   └── deps.py             # get_db / get_current_user / get_optional_user / require_member / require_admin
    ├── schemas/                # Pydantic v2 请求/响应模型,字段与架构文档第 4 节一致
    ├── api/                    # 表现层:仅参数校验/鉴权/分发,不写业务
    ├── services/               # 应用服务层:用例编排
    └── domain/                 # 领域层:纯规则,独立可测
```

**绝对不要碰** `backend/app/models/` 与 `backend/alembic/`(由 database agent 并行负责)。
后端代码一律 `from app.models import ...` 引用,按架构文档约定写,不必等 models 完成。

## 5. 模块划分

### 5.1 表现层 `app/api/`(路由前缀 `/api`)

- `auth.py`:POST `/auth/register`、POST `/auth/login`、GET `/auth/me`
- `catalog.py`:GET `/catalog/categories`、GET `/catalog/products`、GET `/catalog/products/{id}`(游客可访问,价格按登录态动态返回)
- `cart.py`:GET `/cart`、POST `/cart/items`、PATCH `/cart/items/{id}`、DELETE `/cart/items/{id}`(require_member)
- `order.py`:POST `/orders`、GET `/orders`、GET `/orders/{id}`、POST `/orders/{id}/cancel`、POST `/orders/{id}/confirm`(require_member)
- `member.py`:GET/PATCH `/member/profile`、GET `/member/level`、GET/POST/PATCH/DELETE `/member/addresses...`(require_member)
- `admin.py`:分类/商品/分级价/订单发货/支付流水管理(require_admin)
- `payment.py`:POST `/payment/notify/{channel}`(**仅验签不鉴权**)

### 5.2 应用服务层 `app/services/`

- `auth`:注册(role=member,不建 member_profile)/登录/签发 token
- `catalog`:分类/列表/详情,`_effective_price` 按等级取价
- `cart`:增删改查 + 实时计价(价格不落库)
- `order`:下单=校验库存+按等级锁价+预占库存+创建订单+创建支付单+清空购物车;取消/确认收货/后台发货
- `payment`:回调验签桩 + 幂等处理 + 状态流转
- `member`:资料/地址/等级

### 5.3 领域层 `app/domain/`(纯规则)

- `order_state.py`:状态机 + 合法流转表 + `assert_transition`
- `pricing.py`:`resolve_product_price` + `subtotal`
- `inventory.py`:`assert_stock_sufficient` / `deduct_stock` / `restore_stock`
- `payment.py`:渠道/状态枚举 + `is_success_payment`

## 6. 全部关键业务规则(必须实现)

### 6.1 订单状态机(架构文档 3.3)

只允许:`待支付→已支付/已取消`;`已支付→已发货→已完成`;非法流转拒绝;MVP 不做退款。
状态码:`PENDING_PAYMENT / PAID / SHIPPED / COMPLETED / CANCELLED`。
非法流转抛 `INVALID_STATE_TRANSITION`(HTTP 400)。

### 6.2 分级价格(架构文档 3.2)

- 会员按 `level` 取 `product_price`,**无则回退** `product.retail_price`;游客取零售价。
- 下单与展示**只读 `product_price`,不运行时算折扣**。
- 后台「按等级批量折扣」即时展开写入 `product_price` 冗余落库。
- 价格接口按登录态动态返回:游客零售价/会员等级价;分级价格列表仅管理员可见。

### 6.3 库存(本项目落地决策,见 issues.md 第 3 条)

- **下单预占扣减库存,取消回补;支付回调仅幂等状态流转,不二次扣减。**
- 下单前 `assert_stock_sufficient`;库存不足抛 `INSUFFICIENT_STOCK`。

### 6.4 支付回调幂等(架构文档 6.2)

- 靠 `payment(order_id, channel)` 唯一键 + 订单状态机 + 事务。
- 流水已 SUCCESS → 直接应答成功;并发冲突捕获 `IntegrityError` 回滚后重载幂等应答。
- 回调路由不鉴权,仅验签(本期验签为桩,标注 TODO)。

### 6.5 权限(架构文档 5)

- JWT 无状态,payload 含 `sub/role/level_code`;`role ∈ {member, admin}`。
- 依赖注入:`require_member`(买家)、`require_admin`(管理)、`get_optional_user`(价格接口游客可访问)。
- 会员等级默认空 → 回退零售价,由后台人工指定等级。

## 7. 数据模型契约(与 database agent 交接,写入 api.md 第 5 节)

后端 import 的符号:`Base` 及 13 个模型(由 `app.models` 导出):
`User, CustomerLevel, MemberProfile, Category, Product, ProductImage, ProductSpec, ProductPrice, CartItem, Address, Order, OrderItem, Payment`。
会话工厂 `SessionLocal` 由 `app.core.db` 提供(不在 models 中)。
关键列:订单地址快照为展开列 `receiver_name/receiver_phone/receiver_region/receiver_detail`;`payment` 唯一 `(order_id, channel)`;`product_price` 唯一 `(product_id, level_code)`;等级 code 枚举为 `retail|wholesale|vip`。

## 8. 产出文件清单与路径(必须全部写入)

代码:
- `backend/requirements.txt`、`backend/.env.example`
- `backend/app/__init__.py`、`backend/app/main.py`
- `backend/app/core/{__init__,config,db,exceptions,security,deps}.py`
- `backend/app/domain/{__init__,order_state,pricing,inventory,payment}.py`
- `backend/app/schemas/{__init__,common,auth,catalog,cart,order,member,payment,admin}.py`
- `backend/app/services/{__init__,common,auth,catalog,cart,order,payment,member}.py`
- `backend/app/api/{__init__,router,auth,catalog,cart,order,member,admin,payment}.py`

文档:
- `docs/api/api.md` —— 模块、端点列表(方法/路径/鉴权/请求/响应/错误码)、鉴权方式、下单支付回调时序要点、与订单状态机的对应、数据模型契约。
- `docs/api/issues.md` —— 每条含「问题/决策/理由」,至少覆盖:JWT 库选型、passlib/bcrypt 版本、库存占用时机、支付回调幂等、验签桩与异步化、分层边界、CORS、依赖注入、models 契约、分级价落库、状态枚举、运费、等级默认值、不引入 Redis/MQ。
- `docs/api/reproduce-prompt.md` —— 本文件,自足完整。

## 9. 验收标准

1. `backend/` 目录结构与上述清单完全一致,不包含 `app/models/` 与 `alembic/`。
2. 分层正确:API 层无业务规则;服务层编排用例;领域层纯规则(不 import ORM/HTTP)。
3. 订单状态机仅允许合法流转,非法流转返回 400 `INVALID_STATE_TRANSITION`。
4. 分级价、库存预占/回补、支付幂等逻辑落在领域层纯函数 + 服务层编排。
5. 全部路由挂载于 `/api` 前缀;支付回调 `/api/payment/notify/{channel}` 不鉴权。
6. schemas 字段与架构文档第 4 节一致;`from app.models import ...` 引用而非重定义模型。
7. 三份 docs 文档齐全、路径正确、内容自足。
8. 不执行 git 提交(由主 agent 统一提交)。
