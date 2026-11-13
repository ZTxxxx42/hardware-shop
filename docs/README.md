# 五金商贸网站 · 项目文档总纲

> 项目：五金商贸网站（买家端品牌「恒泰五金」）。本文件是 `docs/` 的文档入口，覆盖项目定位、整体架构、技术栈、模块划分与文档索引。内容以实际代码为准，项目变动时需同步更新。

## 1. 项目定位

面向五金工具、五金配件/辅料的在线商贸平台，同一站点同时服务 **零售** 与 **批发** 两类客户，按客户等级展示不同价格，通过 **在线支付** 完成交易。

MVP 目标：跑通「商品展示 → 下单 → 在线支付 → 订单履约」闭环。完整需求见 [MVP需求初稿.md](MVP需求初稿.md)。

## 2. 整体架构

前后端分离，**单体 FastAPI 后端 + 三个前端**：

```
买家端 Web（shop-web / Vue3 SPA）
管理端 Web（admin-web / Vue3 SPA）
买家端小程序（mp-shop / uni-app，mp-weixin + h5）
        │  HTTPS / REST JSON
        ▼
FastAPI 单体（api → services → domain → models）
        │
        ▼
PostgreSQL 16          微信/支付宝支付网关（MVP 桩实现）
```

架构决策、技术选型理由、部署拓扑见 [architecture/架构设计.md](architecture/架构设计.md)。

## 3. 技术栈

| 层 | 选型 | 版本 |
| --- | --- | --- |
| 后端框架 | FastAPI + Pydantic v2 | FastAPI 0.115+ / Pydantic 2.7+ |
| ORM / 迁移 | SQLAlchemy 2.0 + Alembic | 2.0 / 1.13 |
| 数据库 | PostgreSQL 16 | psycopg3 驱动 |
| 认证 | JWT（PyJWT）+ passlib[bcrypt] | PyJWT 2.8+ / bcrypt 4.0.1 |
| 买家端 Web | Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router | Vite 6 |
| 管理端 Web | 同上 | Vite 6 |
| 买家端小程序 | uni-app（Vue 3）+ Pinia | uni-app 3.0 alpha |

## 4. 各端模块划分

| 端 | 目录 | 职责 |
| --- | --- | --- |
| 后端 | `backend/` | 认证、商品目录、购物车、订单、会员、后台管理、支付回调 |
| 买家端 Web | `frontend/shop-web/` | 商城前台：首页、分类、商品、购物车、下单、订单中心、账号 |
| 管理端 Web | `frontend/admin-web/` | 运营后台：商品、分类、价格、客户、订单、支付流水 |
| 买家端小程序 | `frontend/mp-shop/` | 微信小程序买家端，功能对齐买家端 Web |

各端页面/组件/文案/状态管理详见 [frontend/前端文案与组件清单.md](frontend/前端文案与组件清单.md)。

## 5. 仓库结构总览

```
五金商贸/
├── backend/          # FastAPI 后端
├── frontend/         # shop-web / admin-web / mp-shop 三个前端
├── docs/             # 项目文档（本目录）
└── shots/            # 界面样式参考截图
```

完整目录树与各目录职责见 [目录结构说明.md](目录结构说明.md)。

## 6. 文档索引

### 需求与架构

| 文档 | 说明 |
| --- | --- |
| [MVP需求初稿.md](MVP需求初稿.md) | MVP 需求基准（角色、功能清单、假设） |
| [architecture/架构设计.md](architecture/架构设计.md) | 技术选型、分层、流程、数据模型、权限、部署（权威架构） |
| [architecture/目录结构说明.md](architecture/目录结构说明.md) | 仓库目录树与职责 |
| [architecture/system-architecture.drawio](architecture/system-architecture.drawio) | 系统架构图 |
| [architecture/er-diagram.drawio](architecture/er-diagram.drawio) | 核心 ER 图 |
| [architecture/order-payment-flow.drawio](architecture/order-payment-flow.drawio) | 下单支付流程图 |

### 业务与数据

| 文档 | 说明 |
| --- | --- |
| [business/业务合同.md](business/业务合同.md) | 订单状态机、分级价格、库存、角色权限、业务流程 |
| [database/schema.md](database/schema.md) | 13 张表数据模型（权威） |
| [database/seed-data.md](database/seed-data.md) | 种子数据（等级/分类/商品/分级价/测试账号） |
| [database/issues.md](database/issues.md) | 数据层开发问题记录（内部） |
| [database/reproduce-prompt.md](database/reproduce-prompt.md) | 数据层复现提示词（内部） |

### 接口与前端

| 文档 | 说明 |
| --- | --- |
| [api/api.md](api/api.md) | REST API 接口说明（权威） |
| [api/api-client-mapping.md](api/api-client-mapping.md) | 各端调用对应关系 + api.md 与代码差异核对 |
| [api/issues.md](api/issues.md) | 后端开发问题记录（内部） |
| [api/reproduce-prompt.md](api/reproduce-prompt.md) | 后端复现提示词（内部） |
| [frontend/前端文案与组件清单.md](frontend/前端文案与组件清单.md) | 三端页面/组件/文案/状态/API 模块 |
| [frontend/素材清单.md](frontend/素材清单.md) | 三端素材资产与用途 |

### 测试、部署与变更

| 文档 | 说明 |
| --- | --- |
| [testing/验收用例.md](testing/验收用例.md) | 端到端验收测试用例 |
| [deployment/部署说明.md](deployment/部署说明.md) | 后端/Web/小程序部署与上线要点 |
| [CHANGELOG.md](CHANGELOG.md) | 变更日志（基于 git 历史） |

## 7. 快速开始

```bash
# 后端（见 deployment/部署说明.md）
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed

# 买家端 Web
cd frontend/shop-web && npm install && npm run dev   # http://localhost:5173

# 管理端 Web
cd frontend/admin-web && npm install && npm run dev  # http://localhost:5174

# 买家端小程序（H5 预览）
cd frontend/mp-shop && npm install && npm run dev:h5
```

测试账号：`admin / admin123`（管理员）、`member / member123`（批发客户）。
