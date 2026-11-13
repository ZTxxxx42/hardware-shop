# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

「恒泰五金」商贸网站(MVP):面向五金工具/配件的在线商贸平台,前后端分离,含 Web 买家端、Web 管理端、微信小程序买家端。最终目标部署到微信小程序(uni-app 一套代码编译 mp-weixin + h5)。

## 技术栈

- **后端**:FastAPI + SQLAlchemy 2.0 + PostgreSQL 16 + Alembic + Pydantic v2(Python 3.13)
- **Web 前端**:Vue3 + TypeScript + Vite + Element Plus + Pinia + Vue Router
- **小程序前端**:uni-app + Vue3 + Pinia(CLI/vite 方式)
- **部署**:Docker Compose(nginx + api + postgres)

## 常用命令

### 后端(`backend/`)

所有后端命令必须用 conda 环境「五金商贸」的 Python,勿用全局 Python(版本不一致会报依赖错误):

```bash
# 启动(在 backend/ 目录)
"C:\Users\朱涛\.conda\envs\五金商贸\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000

# 数据库迁移(在 backend/ 目录)
"C:\Users\朱涛\.conda\envs\五金商贸\Scripts\alembic.exe" upgrade head

# 种子数据(幂等,可重复执行)
"C:\Users\朱涛\.conda\envs\五金商贸\python.exe" -m scripts.seed

# 测试(在 backend/ 目录,需先 pip install -r requirements-dev.txt)
"C:\Users\朱涛\.conda\envs\五金商贸\python.exe" -m pytest tests/
```

测试账号:`admin/admin123`(管理员)、`member/member123`(会员,等级 wholesale)。

### 前端(`frontend/`)

| 端 | 目录 | 命令 | 端口/路径 |
|---|---|---|---|
| Web 买家端 | `shop-web` | `npm run dev` / `npm run build` | 5173 |
| Web 管理端 | `admin-web` | `npm run dev` / `npm run build` | 5174(`/admin/` 子路径) |
| 小程序买家端 | `mp-shop` | `npm run dev:h5` / `npm run build:mp-weixin` / `npm run type-check` | h5 端口 5175 |

### 数据库

- PostgreSQL 跑在 Docker 容器 `hardware-shop-postgres`(库 `hardware_shop`,数据卷 `hardware-shop-pgdata`)。
- 本地开发需先启动 Docker Desktop,再 `docker start hardware-shop-postgres`。

## 架构

### 后端分层(`backend/app/`)

```
api/        表现层:路由、鉴权(require_admin/require_member)、参数校验、分发,不写业务
services/   应用服务层:用例编排(下单 = 校验库存 + 锁价 + 预占库存 + 建单 + 建支付单)
domain/     领域层:纯规则,不依赖 ORM/HTTP —— 订单状态机、分级价格、库存扣减/回补、支付幂等
models/     SQLAlchemy 2.0 ORM(13 张表,见 docs/database/schema.md)
schemas/    Pydantic v2 请求/响应模型
core/       config(pydantic-settings)、db(SessionLocal)、deps(依赖注入)、security(JWT/bcrypt)、exceptions
```

关键业务规则(详见 `docs/business/业务合同.md`):

- **分级价格**:游客看零售价;会员按 `level_code`(retail/wholesale/vip)取 `product_price`,无则回退 `retail_price`;购物车价格不落库,下单时按等级实时锁定。
- **订单状态机**:待支付→已支付/已取消;已支付→已发货→已完成。非法流转由 `domain/order_state.py` 拒绝。
- **支付回调幂等**:`payment(order_id, channel)` 唯一约束 + 状态机 + 数据库事务。
- **库存**:下单预占扣减、取消回补;支付回调不二次扣减。
- **微信登录**:`POST /api/auth/wechat/login`(code → jscode2session → openid/unionid,`services/wechat.py`);`session_key` 不下发;未配置 AppID/AppSecret 时安全失败返回不可用。
- **账号注销**:`POST /api/member/account-deletion` 记录 `deletion_status=PENDING`,不物理删除。
- **订单物流**:发货 `PATCH /admin/orders/{id}/ship` 必填 `carrier`/`tracking_no`;订单存 `remark/carrier/tracking_no/shipped_at`。
- **微信支付**:当前为**安全失败桩**(`_verify_signature` 直接拒绝),未配置商户证书不允许伪造已支付;无 `prepay` 下单接口。

### 前端三端

- `shop-web`(Web 买家端):游客浏览 + 会员购物车/下单/订单中心;axios + token 拦截。
- `admin-web`(Web 管理端):商品/分类/价格/客户/订单/支付流水管理;`vite base='/admin/'`,路由 `createWebHistory('/admin/')`,登录后 `role=admin`。
- `mp-shop`(小程序买家端):uni-app 复用 shop-web 的 API 逻辑与品牌素材,`uni.request` 替代 axios;`pages.json`/`manifest.json` 在 `src/` 下;tabBar 图标与页面图片**必须用 PNG**(小程序 `<image>` 不支持 SVG)。

### 小程序未登录引导(mp-shop 特有)

- `utils/auth.ts`:`ensureLogin()` 纯判断(不跳转)、`goLogin(redirect)` 显式跳转登录。
- 会员页(购物车/订单/地址/结算/订单详情)未登录时显示 `components/LoginPrompt.vue` 引导,用户点「去登录/注册」才跳转;登录后经 `redirect` 回跳原页。
- 加购按钮未登录时 `uni.showModal` 确认后跳登录。

### 文档(`docs/`)

`docs/README.md` 是总纲与文档索引。子目录:`architecture`、`api`、`database`、`business`、`frontend`、`testing`、`deployment`。根目录另有 `小程序项目档案.md`(小程序进度/提审记录)。**约定:项目代码变动后需同步更新对应 docs 文档。**

## 关键约定

- 后端依赖在 conda 环境「五金商贸」(路径 `C:\Users\朱涛\.conda\envs\五金商贸`),不要用全局 Python。
- 前端 API 地址通过 `VITE_API_BASE_URL` 环境变量配置,默认 `http://127.0.0.1:8000`。
- 品牌名统一为「恒泰五金」;logo 图片在 `src/assets/brand/logo.png`(Web)/ `src/static/brand/logo.png`(小程序)。
- 端口:后端 8000、shop-web 5173、admin-web 5174、mp-shop h5 5175。CORS 白名单含 localhost 与 127.0.0.1 的 5173/5174/5175。
- 金额/价格用字符串 Decimal 传输,前端仅展示,不做浮点运算。
- 商品图 `main_image` 字段存 slug,前端映射到本地 PNG(如 `bolt`→`/static/products/bolt.png`)。
- 微信小程序真机联调:导入 `frontend/mp-shop/dist/build/mp-weixin`;本地需在微信开发者工具「详情→本地设置」勾选「不校验合法域名」;本地 API 地址用 `frontend/mp-shop/.env.production.local` 覆盖(已 gitignore),正式上线用 HTTPS 备案域名。
- 微信 AppID/AppSecret、商户号/证书等敏感值不入库、不写代码,由 `.env`/私密配置注入。
