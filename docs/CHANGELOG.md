# Changelog

本文件基于 git 历史（`git log`）整理。项目尚未打 tag，版本号为规划值；每条记录含日期与提交摘要，可对应到具体提交。

## [0.1.0] - 2026-11-13

首个 MVP 开发版本：完成后端 FastAPI 分层脚手架、PostgreSQL 数据层、三个前端（买家端 Web、管理端 Web、买家端小程序）与配套文档。

### 2026-11-13

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
