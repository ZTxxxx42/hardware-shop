# Changelog

本文件基于 git 历史（`git log`）整理。项目尚未打 tag，版本号为规划值；每条记录含日期与提交摘要，可对应到具体提交。

## [0.1.0] - 2026-11-13

首个 MVP 开发版本：完成后端 FastAPI 分层脚手架、PostgreSQL 数据层、三个前端（买家端 Web、管理端 Web、买家端小程序）与配套文档。

### 2026-11-13

- **docs**：更新 CLAUDE.md 反映小程序上线改动 `2401957`
- **fix(mp-shop)**：商标改用 logo 图片并修复商品列表参数校验失败 `8404fa3`
- **chore**：纳入微信小程序工程配置，忽略私有配置 `1d24401`
- **feat(mp-shop)**：未登录改为提示引导而非自动跳转 `1ae9057`
- **fix(mp-shop)**：SVG 转 PNG 修复小程序图片加载 `be48a60`
- **style(mp-shop)**：小程序视觉由工业橙改回品牌蓝白统一配色 `f1fb7ce`
- **feat(mp-shop)**：环境配置、微信登录、合规入口（隐私政策/用户协议）、工业橙视觉、订单物流展示 `53623b0`
- **feat(admin-web)**：订单发货弹窗补物流公司/单号输入 `43ec6f9`
- **feat(backend)**：新增微信登录、账号注销申请、订单备注物流字段与支付安全失败桩 `f4d01f2`
- **feat(mp-shop)**：新增微信小程序买家端（uni-app，编译 mp-weixin + h5）`285c5e7`
- **fix(admin-web)**：补回 env.d.ts 的 .vue 模块声明，修复 TS2307 报错 `fc64e20`

### 2026-11-10

- **fix(admin-web)**：管理端添加 favicon 图标 `d17e04c`
- **fix(admin-web)**：重命名 logo 文件消除浏览器缓存不一致 `c5257b9`
- **chore(shop-web)**：favicon 移入 assets 目录统一素材管理 `b83a22e`
- **fix(frontend)**：统一两端品牌名为「恒泰五金」及图标 `0a51028`

### 2026-11-09

- **fix(backend)**：CORS 白名单加入 127.0.0.1，修复前端跨域加载失败 `3d62b95`
- **feat(shop-web)**：购物车与下单接入后端真实 API `88b9180`
- **feat(admin-web)**：管理端接入后端真实 API `c2e3688`
- **feat(shop-web)**：买家端目录接入后端真实 API `f8c1d47`
- **feat(backend)**：新增种子数据脚本（分类/商品/分级价/等级/测试用户）`ddb1ed9`

### 2026-11-08

- **chore(assets)**：添加前端样式参考截图 `f9d567d`
- **feat(admin-web)**：新增管理端 Vue3 脚手架与后台布局 `43a062e`
- **feat(shop-web)**：新增买家端 Vue3 脚手架与响应式首页 `2b7f95b`
- **docs**：同步后端 Python 版本为 3.13 `109c83e`
- **fix(backend)**：统一数据库名并修复 alembic 编码与 204 端点启动错误 `a9c6c12`
- **feat(backend)**：新增 FastAPI 分层脚手架与 API 接口文档 `f795cb5`
- **feat(db)**：新增 PostgreSQL 数据层（SQLAlchemy 模型 + Alembic 迁移）`0393463`
- **docs**：新增核心 ER 图与下单支付流程图 `7231a9b`
- **docs**：架构设计数据库选型由 MySQL 改为 PostgreSQL `a0eef85`

### 2026-11-07

- **docs**：MVP 需求初稿确认为基准版本 `f5f6148`
- **docs**：新增五金商贸网站 MVP 需求初稿 `f266b8f`
