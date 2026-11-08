# 恒泰五金商贸 · shop-web 买家端

基于 Vue 3、TypeScript、Vite、Element Plus、Pinia 与 Vue Router 的五金商贸前台买家端 MVP。

当前首页使用静态示例数据和本地 SVG 素材渲染，不依赖后端数据或外部图片服务。Axios 客户端已按后端 `/api` 端点预留，后续可逐页接入真实数据。

## 环境要求

- Node.js 20.19+ 或 22.12+（已在 Node.js 26 验证）
- npm 10+
- 开发端口：`5173`
- 后端默认地址：`http://127.0.0.1:8000`

## 安装与启动

```bash
cd frontend/shop-web
npm install
npm run dev
```

访问 <http://localhost:5173>。开发服务器使用严格端口模式，若 5173 被占用会直接退出，不会自动切换端口。

## 构建与预览

```bash
# TypeScript 类型检查 + 生产构建
npm run build

# 本地预览 dist
npm run preview
```

生产文件输出至 `dist/`。部署到 Nginx 时，SPA history 路由需要配置 `try_files $uri $uri/ /index.html;`。

## 环境变量

开发环境已提供 `.env.development`：

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

其他部署环境可复制 `.env.example` 为 `.env.production` 并按实际后端地址修改。地址末尾不要添加斜杠，API 模块会在此基础上请求 `/api/...`。

## 已实现页面

- 首页：桌面工业横幅、移动轮播、产品分类、热销产品、服务优势、关于我们、新闻资讯、页脚与移动底部导航。
- 产品分类与产品中心：使用同一套静态分类和商品示例数据。
- 路由占位页：商品详情、搜索、购物车、结算下单、订单中心、登录、注册、个人中心、地址管理、关于我们、新闻资讯、服务支持、联系我们及 404。

## 目录说明

```text
src/
├── api/                 # Axios 客户端、认证与商品目录 API
├── assets/              # 品牌、商品、分类、工业场景 SVG 与本地二维码
│   └── styles/          # Element Plus 品牌主色与全局响应式样式
├── components/
│   ├── home/            # 首页六个内容区块
│   └── layout/          # 头部、页脚、移动 Tabbar
├── data/                # 首页静态示例数据
├── router/              # 全部买家端路由
├── stores/              # Pinia 购物车与用户状态
├── types/               # 商品与分类类型
└── views/               # 首页、分类、列表与业务占位页面
```

## 对接说明

- `src/api/http.ts` 自动从 `localStorage` 读取 `hengtai_access_token` 并附加 Bearer Token。
- 商品接口位于 `src/api/catalog.ts`，认证接口位于 `src/api/auth.ts`。
- 首页数据集中在 `src/data/home.ts`，后续可替换为 API 请求结果。
- 当前商品询价跳转至联系页并携带商品名称；购物车与订单仅为脚手架状态或占位页面，尚未调用后端。
- 所有产品图、分类图标、品牌标志、Hero 工业场景与厂房图均为项目内本地素材；二维码内容为客服热线 `tel:4001234567`。
