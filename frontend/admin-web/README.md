# 恒泰五金 · admin-web 管理后台

五金商贸 MVP 的后台管理端脚手架，基于 Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router。当前使用静态示例数据渲染，所有新增、编辑、删除、发货等操作只修改浏览器内存，不会请求后端或持久化。

## 环境要求

- Node.js 20.19+（当前已在 Node.js 26 / npm 12 验证）
- npm 10+

## 安装与启动

```bash
cd frontend/admin-web
npm install
npm run dev
```

开发服务器固定使用 **5174** 端口，访问：<http://localhost:5174>。

脚手架登录账号：`admin`，密码：`admin123`。该账号仅用于本地模拟登录。

## 构建与预览

```bash
# TypeScript 类型检查 + 生产构建
npm run build

# 本地预览 dist 构建产物
npm run preview
```

生产文件输出到 `dist/`。

## 环境变量

开发环境配置位于 `.env.development`：

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

复制 `.env.example` 可创建其他环境配置。`src/api/http.ts` 中的 axios 客户端读取该变量，并自动携带 `Authorization: Bearer <JWT>`。管理端端点统一预留为 `/api/admin/*`，当前页面尚未调用这些接口。

## 已实现页面

| 路由 | 页面 | 骨架能力 |
| --- | --- | --- |
| `/login` | 管理员登录 | 表单校验、模拟 JWT 登录态、退出登录 |
| `/products` | 商品管理 | 搜索筛选、新增/编辑、本地多图选择、规格文本、库存、上下架、删除 |
| `/categories` | 分类管理 | 两级树形表格、新增/编辑、启停用、删除约束 |
| `/prices` | 价格管理 | 商品 × 零售/批发/VIP 等级定价、零售价回退、按等级批量折扣展开 |
| `/customers` | 客户管理 | 客户列表、资料编辑、指定客户等级 |
| `/orders` | 订单管理 | 状态筛选、详情与价格快照、五种状态展示、已支付订单发货 |
| `/payments` | 支付流水 | 渠道/状态筛选、订单金额对账、跳转关联订单 |

## 目录结构

```text
src/
├── api/                 # axios 客户端与管理端 API 预留
├── assets/              # 本地品牌标识、商品 SVG 示例素材
├── components/          # 通用页头组件
├── layout/              # Element Plus 经典后台布局
├── mock/                # 静态商品、客户、订单与支付数据
├── router/              # 路由与登录守卫
├── stores/              # Pinia 管理员登录态
├── styles/              # 品牌 token 与全局样式
├── types/               # 业务类型与路由类型扩展
├── utils/               # 金额、等级与状态显示工具
├── views/               # 各业务页面
├── App.vue
└── main.ts
```

## 后续联调建议

1. 将 `src/stores/auth.ts` 的模拟登录替换为 `POST /api/auth/login`，并校验 JWT 中 `role=admin`。
2. 各页面以 `src/api/admin.ts` 替换 `src/mock/` 数据源，保留现有加载、空态和表单校验。
3. 商品图片上传需接入后端文件存储；当前 `el-upload` 已关闭自动上传。
4. 发货接口当前为 `PATCH /api/admin/orders/{id}/ship`，物流公司和单号仅为界面占位字段。
