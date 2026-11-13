# 五金商贸 MVP · API 接口说明

> 版本 v1.0 ｜ 依据 `docs/architecture/架构设计.md` ｜ 后端 `backend/`

## 0. 约定

- Base URL:`/api`
- 请求/响应体:`application/json; charset=utf-8`
- 时间格式:ISO 8601;金额:字符串形式的十进制数(Decimal),单位为元
- 鉴权:`Authorization: Bearer <JWT>`
- 错误响应统一结构:

```json
{"code": "错误码", "message": "人类可读信息", "detail": "可选,校验错误明细"}
```

### 0.1 通用错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| VALIDATION_ERROR | 422 | 参数校验失败 |
| NOT_FOUND | 404 | 资源不存在 |
| BUSINESS_ERROR | 400 | 通用业务错误 |
| INSUFFICIENT_STOCK | 400 | 库存不足 |
| INVALID_STATE_TRANSITION | 400 | 非法订单状态流转 |
| PAYMENT_VERIFY_FAILED | 400 | 支付回调验签失败 |

HTTP 401 表示未登录/凭证无效,HTTP 403 表示角色无权限(会员接口用 `role=member`,管理接口用 `role=admin`)。

## 1. 鉴权方式

JWT 无状态认证,payload 携带:

```json
{"sub": "<user_id>", "role": "member|admin", "level_code": "retail|wholesale|vip", "iat": 0, "exp": 0}
```

- 游客:无 JWT,可浏览商品/分类,**仅见零售价**。
- 会员:`role=member`,可购物车/下单/订单中心/地址资料,**按等级取价**(无等级价回退零售价)。
- 管理员:`role=admin`,后台管理接口;前台以零售身份看价。
- 支付回调 `/api/payment/notify/{channel}` **不设登录鉴权,仅验签**。

## 2. 模块与端点

### 2.1 认证 `/auth`

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 说明 |
| --- | --- | --- | --- | --- | --- |
| POST | `/auth/register` | 无 | `{username, password, phone?}` | `TokenResponse` | 注册即会员(role=member),等级由后台指定 |
| POST | `/auth/login` | 无 | `{username, password}` | `TokenResponse` | 登录返回 JWT |
| GET | `/auth/me` | 登录 | — | `UserBrief` | 当前用户信息 |

`TokenResponse`:`{access_token, token_type, expires_in, user: UserBrief}`
`UserBrief`:`{id, username, role, phone?, level_code?}`

### 2.2 商品目录 `/catalog`(游客可访问,价格按登录态动态返回)

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 说明 |
| --- | --- | --- | --- | --- | --- |
| GET | `/catalog/categories` | 无 | — | `list[CategoryOut]` | 分类树(自引用) |
| GET | `/catalog/products` | 可选 | query:`category_id?`, `keyword?`, `page`, `page_size` | `PageResult[ProductBrief]` | 商品列表,`price` 为当前视角价格 |
| GET | `/catalog/products/{product_id}` | 可选 | — | `ProductDetail` | 详情;分级价格仅管理员可见 |

`ProductBrief`:`{id, category_id, name, model?, main_image?, retail_price, price, stock, status}`
其中 `price` = 游客零售价 / 会员等级价(无则零售价)。搜索为 PostgreSQL `ILIKE`。

### 2.3 购物车 `/cart`(会员)

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 说明 |
| --- | --- | --- | --- | --- | --- |
| GET | `/cart` | member | — | `CartSummary` | 实时计价,价格不落库 |
| POST | `/cart/items` | member | `{product_id, quantity}` | `CartSummary` | 加购,同商品累加数量 |
| PATCH | `/cart/items/{item_id}` | member | `{quantity}` | `CartSummary` | 改数量 |
| DELETE | `/cart/items/{item_id}` | member | — | `CartSummary` | 删除项 |

### 2.4 订单 `/orders`(会员)

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 状态流转 |
| --- | --- | --- | --- | --- | --- |
| POST | `/orders` | member | `{address_id, channel?, remark?}` | `OrderDetail` | 创建 → 待支付 |
| GET | `/orders` | member | — | `list[OrderBrief]` | 订单中心 |
| GET | `/orders/{order_id}` | member | — | `OrderDetail` | 订单详情 |
| POST | `/orders/{order_id}/cancel` | member | — | `OrderDetail` | 待支付 → 已取消,回补库存 |
| POST | `/orders/{order_id}/confirm` | member | — | `OrderDetail` | 已发货 → 已完成(确认收货) |

下单内部顺序:**校验库存 → 按等级锁价 → 预占库存 → 创建订单 → 创建支付单 → 清空购物车**,同一事务提交。

### 2.5 会员资料/地址 `/member`(会员)

| 方法 | 路径 | 鉴权 | 请求 | 响应 |
| --- | --- | --- | --- | --- |
| GET | `/member/profile` | member | — | `ProfileOut` |
| PATCH | `/member/profile` | member | `{phone?, real_name?}` | `ProfileOut` |
| GET | `/member/level` | member | — | `LevelOut \| null` |
| GET | `/member/addresses` | member | — | `list[AddressOut]` |
| POST | `/member/addresses` | member | `{receiver, phone, region, detail}` | `AddressOut` |
| PATCH | `/member/addresses/{address_id}` | member | `{receiver, phone, region, detail}` | `AddressOut` |
| DELETE | `/member/addresses/{address_id}` | member | — | 204 |

### 2.6 管理 `/admin`(admin)

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 说明 |
| --- | --- | --- | --- | --- | --- |
| GET | `/admin/categories` | admin | — | `list[CategoryOut]` | |
| POST | `/admin/categories` | admin | `{name, parent_id?, sort?}` | `CategoryOut` | |
| PATCH | `/admin/categories/{category_id}` | admin | 部分字段 | `CategoryOut` | |
| DELETE | `/admin/categories/{category_id}` | admin | — | 204 | |
| GET | `/admin/products` | admin | `page`, `page_size` | `PageResult[ProductBrief]` | 以零售价返回 |
| POST | `/admin/products` | admin | `ProductCreate` | `ProductBrief` | |
| GET | `/admin/products/{product_id}` | admin | — | `ProductBrief` | |
| PATCH | `/admin/products/{product_id}` | admin | `ProductUpdate` | `ProductBrief` | |
| PUT | `/admin/products/{product_id}/prices` | admin | `{prices: [{level_code, price}]}` | `list[ProductPriceItem]` | 展开写入 `product_price` |
| GET | `/admin/customers` | admin | query:`keyword?` | `list[ProfileOut]` | 列出所有 `role=member` 客户,`keyword` 模糊匹配账号/手机/姓名 |
| PATCH | `/admin/customers/{user_id}` | admin | `{level_code}` | `ProfileOut` | 指定客户等级(零售/批发/VIP),无档案则建档 |
| GET | `/admin/orders` | admin | — | `list[OrderBrief]` | |
| PATCH | `/admin/orders/{order_id}/ship` | admin | — | `OrderDetail` | 已支付 → 已发货 |
| GET | `/admin/payments` | admin | — | `list[PaymentOut]` | 支付流水 |

`ProfileOut`:`{user_id, username, phone?, real_name?, level_code?, level_name?}`

### 2.7 支付回调 `/payment`(仅验签,不鉴权)

| 方法 | 路径 | 鉴权 | 请求 | 响应 | 说明 |
| --- | --- | --- | --- | --- | --- |
| POST | `/payment/notify/{channel}` | 无 | `PaymentNotifyPayload` | `{code, message}` | channel ∈ wechat/alipay |

`PaymentNotifyPayload`:`{order_no, channel, trade_no, amount, status, sign?, extra?}`

## 3. 下单支付回调时序要点

1. 会员浏览商品 → `/catalog/products` 按等级实时取价。
2. 加购 → `/cart` 只存 `product_id + 数量`,价格不落库。
3. 结算 → `POST /orders`:选地址,后端校验库存,按等级重新计算单价与总额,生成订单(待支付)+ 支付单(唯一约束 `(order_id, channel)`),**预占扣减库存**。
4. 网关预支付(本期桩实现,联调接入微信 Native/JSAPI 或支付宝)。
5. 支付成功 → 网关异步回调 `POST /payment/notify/{channel}`:后端验签 → 幂等(流水唯一键 + 状态机 + 事务)→ 订单转「已支付」→ 记录流水 → 应答成功。
6. 商家后台 `PATCH /admin/orders/{order_id}/ship` → 「已发货」。
7. 买家 `POST /orders/{order_id}/confirm` → 「已完成」。
8. 待支付订单 `POST /orders/{order_id}/cancel` → 「已取消」并**回补占用库存**。

## 4. 订单状态机对应

| 动作 | 当前状态 | 目标状态 | 端点 |
| --- | --- | --- | --- |
| 下单 | — | PENDING_PAYMENT | POST `/orders` |
| 支付成功回调 | PENDING_PAYMENT | PAID | POST `/payment/notify/{channel}` |
| 买家取消 | PENDING_PAYMENT | CANCELLED | POST `/orders/{order_id}/cancel` |
| 商家发货 | PAID | SHIPPED | PATCH `/admin/orders/{order_id}/ship` |
| 确认收货 | SHIPPED | COMPLETED | POST `/orders/{order_id}/confirm` |

非法流转(如 已发货→待支付、已完成→已取消)由领域层状态机拒绝,返回 `INVALID_STATE_TRANSITION`。MVP 不做退款。

## 5. 数据模型契约(与 database agent 交接)

后端代码 `from app.models import ...` 引用以下符号,由 database agent 产出:

- 模型:`User, CustomerLevel, MemberProfile, Category, Product, ProductImage, ProductSpec, ProductPrice, CartItem, Address, Order, OrderItem, Payment`
- 会话:`Base` 及全部模型由 `app.models` 导出;会话工厂 `SessionLocal` 由 `app.core.db` 提供
- 关键列(架构设计.md 第 4 节):`user.password_hash/role/phone`;`member_profile.level_code/real_name`;`product.retail_price/stock/status/main_image`;`product_price.price + 唯一(product_id, level_code)`;`order.order_no(唯一)/status/product_amount/freight_amount/total_amount/receiver_name/receiver_phone/receiver_region/receiver_detail(地址快照展开列)`;`order_item.product_name/price/quantity/subtotal`;`payment.trade_no/amount/status/paid_at + 唯一(order_id, channel)`。
