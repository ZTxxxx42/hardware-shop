# 五金商贸 MVP · 种子数据说明

> 来源：`backend/scripts/seed.py`。脚本按业务唯一键 upsert，**可重复执行**，不会产生重复数据。执行前置条件：数据库已创建并完成 Alembic 迁移。

## 1. 运行方式

```bash
cd backend
alembic upgrade head
python -m scripts.seed
# 或
python scripts/seed.py
```

执行成功输出摘要（3 个等级、6 个顶级分类、8 个商品、16 条分级价格、2 个测试用户、1 份会员资料）。

## 2. 客户等级（customer_level）

| code | 名称 | sort |
| --- | --- | --- |
| `retail` | 零售客户 | 1 |
| `wholesale` | 批发客户 | 2 |
| `vip` | VIP客户 | 3 |

## 3. 商品分类（category）

6 个**顶级**分类（无子分类）：

| 名称 | sort |
| --- | --- |
| 手动工具 | 1 |
| 电动工具 | 2 |
| 紧固件 | 3 |
| 建筑五金 | 4 |
| 机械配件 | 5 |
| 五金型材 | 6 |

> 注：种子只生成顶级分类；「五金型材」当前未挂任何商品。管理端 mock 中的二级分类（如「螺栓与螺钉」）仅存在于前端静态数据，与后端种子无关。

## 4. 商品与分级价格（product / product_price）

种子商品均为 `status=ON_SALE`，`main_image` 存**素材标识**（如 `bolt`），前端据此映射本地 SVG（见 [../frontend/素材清单.md](../frontend/素材清单.md)）。分级价格由「零售价 × 系数」生成：批发 `0.85`、VIP `0.7`，`quantize(0.01)`（ROUND_HALF_EVEN）。

| 商品 | 型号 | 分类 | 零售价(元) | 批发价(元) | VIP价(元) | 库存 | main_image |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 不锈钢外六角螺栓 | M6-M20 | 紧固件 | 12.80 | 10.88 | 8.96 | 1000 | bolt |
| 六角螺母 | M6-M20 | 紧固件 | 6.50 | 5.52 | 4.55 | 2000 | nut |
| 平垫圈 | M6-M20 | 紧固件 | 4.80 | 4.08 | 3.36 | 3000 | washer |
| 膨胀螺栓 | M8-M16 | 紧固件 | 18.00 | 15.30 | 12.60 | 800 | anchor |
| 不锈钢合页 | 4寸 | 建筑五金 | 25.00 | 21.25 | 17.50 | 500 | hinge |
| 深沟球轴承 | 6200-6210 | 机械配件 | 32.00 | 27.20 | 22.40 | 600 | bearing |
| 手动扳手 | 8-24mm | 手动工具 | 45.00 | 38.25 | 31.50 | 300 | wrench |
| 电钻 | 220V/550W | 电动工具 | 299.00 | 254.15 | 209.30 | 100 | drill |

## 5. 测试账号（user / member_profile）

| 账号 | 密码 | 角色 | 会员等级 | 说明 |
| --- | --- | --- | --- | --- |
| `admin` | `admin123` | admin | —（无 member_profile） | 管理后台登录 |
| `member` | `member123` | member | `wholesale`（批发客户） | 买家端登录，验证分级价格 |

> 会员 `member` 的等级为 `wholesale`，登录后商品按批发价展示。游客看零售价，可用于对比验证分级价格。注册新会员默认无等级，价格回退零售价。

## 6. 幂等性

脚本通过业务唯一键定位后更新或插入，重复执行安全：

- `customer_level`：主键 `code`；
- `category`：`name`（顶级）查询；
- `product`：`name` 查询；
- `product_price`：`(product_id, level_code)` 查询；
- `user`：`username` 查询，密码哈希不一致时重置为种子密码；
- `member_profile`：`user_id` 查询。
