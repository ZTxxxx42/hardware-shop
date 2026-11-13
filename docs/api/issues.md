# 五金商贸 MVP · 后端开发问题记录

> 每条含「问题 / 决策 / 理由」。用于沉淀本次 FastAPI 分层脚手架的权衡,便于后续评审与演进。

## 1. JWT 库选型

- 问题:pyjwt 与 python-jose 二选一。
- 决策:选 PyJWT。
- 理由:本项目仅需 HS256 对称签名与 decode,无复杂 OIDC/JWE 需求;PyJWT 维护活跃、依赖少、API 简洁;python-jose 更适合需要完整 JOSE 能力的场景,属于过度引入。

## 2. passlib 与 bcrypt 版本兼容

- 问题:passlib 1.7.4 未适配 bcrypt 4.1+(bcrypt 移除了 `__about__` 属性,passlib 探测版本时报错/告警)。
- 决策:锁定 `bcrypt==4.0.1`,requirements 中显式固定。
- 理由:架构文档指定 passlib[bcrypt];在 passlib 升级或换用原生 bcrypt 前,固定版本是零成本、可复现的解法。后续演进可考虑直接用 `bcrypt` 库(带 try/except 与 salt 管理)。

## 3. 库存占用时机(下单校验 vs 预占)

- 问题:架构设计 3.1 存在表述不一致——步骤 3 说「校验库存」、步骤 6 说支付成功「扣减库存」、步骤 7 说取消「回补占用库存」。
- 决策:采用「**下单预占扣减库存,取消回补,支付回调仅做幂等状态流转(不二次扣减)**」。
- 理由:
  - 消除「已付款但库存被其他订单抢光」的边界,避免 MVP 无退款机制下的死结;
  - 与步骤 7「回补占用库存」一致;
  - 领域层「库存扣减/回补」两条纯规则均被实际使用;
  - 支付回调专注验签 + 幂等 + 状态流转,符合幂等约束,避免重复扣减。

## 4. 支付回调幂等实现

- 问题:网关可能重复回调、并发回调,如何保证不重复发货/扣减。
- 决策:`payment(order_id, channel)` 唯一约束 + 订单状态机 + 事务;服务层先查流水,已 SUCCESS 直接应答;并发冲突捕获 `IntegrityError` 后回滚重载幂等应答。
- 理由:架构设计 6.2 明确此方案;不引入 Redis 分布式锁,靠数据库唯一约束与状态机即可满足 MVP。

## 5. 支付回调验签桩与异步化

- 问题:真实微信/支付宝验签依赖商户配置,且回调格式各不相同。
- 决策:本期 `services/payment.py::_verify_signature` 为安全失败桩(未配置商户证书时直接拒绝,不伪造已支付);联调时替换为微信 v3(AEAD_AES_256_GCM)/支付宝(RSA2)验签并适配表单/XML 参数。
- 理由:MVP 先跑通「幂等 + 状态机」闭环;验签属于联调外部依赖,过早实现会引入无验证的伪代码。

## 6. 分层边界(表现层不写业务)

- 问题:如何避免路由函数膨胀成「上帝函数」。
- 决策:API 层仅参数校验/鉴权/分发;应用服务层编排用例;领域层放纯规则(分级价/状态机/库存/幂等)。管理端无跨实体业务规则的简单 CRUD 暂直接落在 admin 路由,涉及状态流转的「发货」复用 `order_service.ship_order`。
- 理由:遵循架构设计第 2 节与 KISS/SRP;admin CRUD 是纯持久化,抽 service 属于当前阶段无收益的抽象(Rule of Three)。

## 7. CORS 配置方式

- 问题:双前端 SPA(买家端/管理端)跨域访问同一 API。
- 决策:白名单来源由 `Settings.cors_origins`(JSON 数组)配置,`CORSMiddleware` 统一放开方法/头。
- 理由:开发期两端不同端口,Vite 代理与后端 CORS 二选一;直接 CORS 白名单最简单,生产由 Nginx 反代收敛为同源后白名单可收窄。

## 8. 依赖注入方式

- 问题:会话、当前用户、角色校验的注入粒度。
- 决策:`get_db` + `get_current_user` + `require_member/require_admin` 的 FastAPI Depends 链;价格接口用 `get_optional_user` 返回 `None` 实现「游客/会员」动态取价。
- 理由:接口级鉴权与架构文档第 5 节一致;`get_optional_user` 避免为价格接口拆两套路由。

## 9. 订单地址快照与 models 契约

- 问题:架构文档只写「address 快照」,未定列名;`app.models` 由 database agent 并行产出。
- 决策:以 database agent 实际落库为准,订单地址快照采用展开列 `receiver_name/receiver_phone/receiver_region/receiver_detail`;服务层拼装为响应中的 `address_snapshot` dict,在 api.md 第 5 节写明契约。
- 理由:并行产出后以实际模型为准(与项目既有规范冲突时以项目为准);展开列查询与约束更直接,响应仍对前端保持稳定结构。

## 10. 分级价格不运行时算折扣

- 问题:会员折扣是运行时计算还是落库。
- 决策:后台「按等级批量折扣」即时展开写入 `product_price` 冗余落库;下单与展示只读 `product_price`,会员无等级价回退 `retail_price`,游客取零售价。
- 理由:架构设计 3.2 明确要求;避免历史订单/展示口径受折扣规则变更影响,且查询路径简单。

## 11. 商品上下架状态枚举

- 问题:架构文档未显式定义 `product.status` 取值。
- 决策:买家侧以 `status == "ON_SALE"` 作为可售条件,常量化在 `services/catalog.py::ON_SALE_STATUS`。
- 理由:最小约定,待 database agent 落地 status 枚举后统一;集中一处便于后续对齐。

## 12. 运费规则

- 问题:架构文档 7.1 写「统一运费(可选满额包邮)」但未给具体值。
- 决策:MVP 运费取 0,`services/common.py::calculate_freight` 预留满额包邮阈值。
- 理由:运费模板是明确的后续演进项,当前以单一函数承载规则,替换不侵入下单逻辑。

## 13. 会员等级默认值

- 问题:注册的会员 level_code 从哪来。
- 决策:注册不创建 member_profile,level_code 为空 → 价格回退零售价;等级由后台指定(架构文档 7.1「后台人工指定」)。
- 理由:符合「固定 3 级、后台人工指定」;空等级自然回退零售价,行为正确且无需种子耦合。

## 14. 未引入 Redis / 消息队列

- 问题:是否需要为库存锁、回调异步引入中间件。
- 决策:不引入,购物车/订单状态用 PostgreSQL,幂等靠唯一约束 + 状态机 + 事务。
- 理由:架构文档 1.1 明确 Redis 为后续演进项;MVP 无高并发秒杀,引入会扩大部署面。

## 15. 与 database agent 实际模型的对齐修正

- 问题:并行开发后发现三处假设与 `app.models` 实际产物不一致:User 关系名为 `profile` 而非 `member_profile`;等级 code 为 `retail/wholesale/vip` 而非中文;无会话工厂导出。
- 决策:代码改用 `user.profile`;文档等级枚举改为英文 code;会话工厂落位 `app/core/db.py`(不侵入 models/alembic)。
- 理由:并行 agent 产出后必须回归真实模型对齐,避免运行时 ImportError/AttributeError;`get_db` 属核心基础设施,放在 core 层合理。
