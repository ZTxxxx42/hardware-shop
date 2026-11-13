# 五金商贸 MVP · API 各端调用对应关系与差异核对

> 本文件是 [api.md](api.md) 的**补充**，不重复接口定义。`api.md` 为接口说明权威文档；本文补充「哪个前端调用了哪些端点」，并核对 `api.md` 与 `backend/` 实际代码的差异。差异项以实际代码为准，待后续同步 `api.md`。

## 1. 各端调用对应关系

### 1.1 买家端 Web（shop-web）

API 封装：`frontend/shop-web/src/api/{auth,cart,catalog,member,order,http}.ts`

| 前端 API 模块 | 方法 | 后端端点 |
| --- | --- | --- |
| authApi | login | `POST /api/auth/login` |
| authApi | register | `POST /api/auth/register` |
| authApi | me | `GET /api/auth/me` |
| catalogApi | categories | `GET /api/catalog/categories` |
| catalogApi | products | `GET /api/catalog/products` |
| catalogApi | product | `GET /api/catalog/products/{id}` |
| cartApi | summary | `GET /api/cart` |
| cartApi | addItem | `POST /api/cart/items` |
| cartApi | updateItem | `PATCH /api/cart/items/{id}` |
| cartApi | removeItem | `DELETE /api/cart/items/{id}` |
| memberApi | profile | `GET /api/member/profile` |
| memberApi | level | `GET /api/member/level` |
| memberApi | addresses | `GET /api/member/addresses` |
| memberApi | createAddress | `POST /api/member/addresses` |
| memberApi | updateAddress | `PATCH /api/member/addresses/{id}` |
| memberApi | removeAddress | `DELETE /api/member/addresses/{id}` |
| orderApi | list | `GET /api/orders` |
| orderApi | detail | `GET /api/orders/{id}` |
| orderApi | create | `POST /api/orders` |
| orderApi | cancel | `POST /api/orders/{id}/cancel` |
| orderApi | confirm | `POST /api/orders/{id}/confirm` |

### 1.2 买家端小程序（mp-shop）

API 封装：`frontend/mp-shop/src/api/{auth,cart,catalog,member,order,http}.ts`

调用端点与 shop-web 完全一致（同一套会员 API）。差异仅在 HTTP 客户端：`uni.request`（`mp-shop`）vs `axios`（`shop-web`）；401 时统一清 token 并触发 `auth:unauthorized` 事件。

### 1.3 管理端 Web（admin-web）

API 封装：`frontend/admin-web/src/api/admin.ts`（含登录与后台端点）。

| 前端 API 方法 | 后端端点 | 说明 |
| --- | --- | --- |
| adminApi.login | `POST /api/auth/login` | 登录后校验 `role=admin` |
| adminApi.getProducts | `GET /api/admin/products` | |
| adminApi.getProductDetail | `GET /api/catalog/products/{id}` | 复用买家目录详情，获取 `level_prices` |
| adminApi.createProduct | `POST /api/admin/products` | |
| adminApi.updateProduct | `PATCH /api/admin/products/{id}` | |
| adminApi.updateProductPrices | `PUT /api/admin/products/{id}/prices` | |
| adminApi.getCategories | `GET /api/admin/categories` | |
| adminApi.createCategory | `POST /api/admin/categories` | |
| adminApi.updateCategory | `PATCH /api/admin/categories/{id}` | |
| adminApi.deleteCategory | `DELETE /api/admin/categories/{id}` | |
| adminApi.getOrders | `GET /api/admin/orders` | |
| adminApi.shipOrder | `PATCH /api/admin/orders/{id}/ship` | |
| adminApi.getPayments | `GET /api/admin/payments` | |

> 管理端集成状态：登录（`stores/auth.ts`）与商品/分类/价格/**客户**/订单/支付流水列表均已接入真实 API。详见下文差异核对。

## 2. api.md 与实际代码差异核对

| # | 事项 | api.md 表述 | 实际代码 | 结论 |
| --- | --- | --- | --- | --- |
| 1 | 分类路径参数名 | `PATCH/DELETE /admin/categories/{id}` | `PATCH/DELETE /admin/categories/{category_id}`（`backend/app/api/admin.py`） | 语义一致，参数名以代码为准，待同步 api.md |
| 2 | 订单发货路径参数名 | `PATCH /admin/orders/{id}/ship` | `PATCH /admin/orders/{order_id}/ship` | 同上 |
| 3 | 客户管理端点 | 未在 api.md 列出 | 后端已实现 `GET/PATCH /admin/customers`（列表+指定等级，commit 2e446ba） | **已落地**，api.md 2.6 已补 |
| 4 | `GET /auth/me` 返回字段 | `UserBrief`（含 phone） | `backend/app/api/auth.py::me` 未返回 `phone`（仅 id/username/role/level_code） | 差异待核对，建议补 `phone` 或统一口径 |
| 5 | 下单库存时机 | api.md 第 3 节第 3 步「预占扣减库存」 | 与 `services/order.py` 一致（下单预占，回调不二次扣减） | 一致 |
| 6 | 支付状态 | api.md 未列 `CLOSED` | `PaymentStatus.CLOSED` 存在，取消订单时 PENDING 流水转 CLOSED | api.md 建议补 `CLOSED` |

> 说明：`api.md` 第 2.6 节的 `PATCH /admin/orders/{id}/ship` 与 `backend/app/api/admin.py` 路径参数名不一致，不影响调用（前端按实际端点路径拼装），但文档需同步。

## 3. 已确认的接口事实（供后续维护）

- 鉴权：`HTTPBearer` + JWT，`Authorization: Bearer <token>`；会员接口 `require_member`，管理接口 `require_admin`，价格接口 `get_optional_user`。
- 错误响应统一 `{code, message, detail?}`；HTTP 401 未登录/凭证无效，403 角色无权限。
- 支付回调 `POST /payment/notify/{channel}` 不鉴权，仅验签（MVP 桩）。
- 前端两端 token 存储 key：shop-web 用 `hengtai_access_token`，admin-web 用 `admin_access_token`，mp-shop 用 `storage` 工具（见 `frontend/mp-shop/src/utils/storage.ts`）。
