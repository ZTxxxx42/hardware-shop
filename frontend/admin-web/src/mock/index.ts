import boltImage from '@/assets/products/bolt.svg'
import drillImage from '@/assets/products/drill.svg'
import hingeImage from '@/assets/products/hinge.svg'
import gloveImage from '@/assets/products/glove.svg'
import type { Category, Customer, Order, Payment, Product } from '@/types/business'

export const categories: Category[] = [
  { id: 1, parentId: null, name: '紧固件', sort: 10, productCount: 2, status: 'ENABLED' },
  { id: 11, parentId: 1, name: '螺栓与螺钉', sort: 10, productCount: 2, status: 'ENABLED' },
  { id: 12, parentId: 1, name: '螺母与垫圈', sort: 20, productCount: 0, status: 'ENABLED' },
  { id: 2, parentId: null, name: '电动工具', sort: 20, productCount: 1, status: 'ENABLED' },
  { id: 21, parentId: 2, name: '钻孔工具', sort: 10, productCount: 1, status: 'ENABLED' },
  { id: 3, parentId: null, name: '家具五金', sort: 30, productCount: 2, status: 'ENABLED' },
  { id: 31, parentId: 3, name: '铰链与滑轨', sort: 10, productCount: 2, status: 'ENABLED' },
  { id: 4, parentId: null, name: '劳保用品', sort: 40, productCount: 1, status: 'ENABLED' },
]

export const products: Product[] = [
  { id: 1001, name: '304 不锈钢外六角螺栓', categoryId: 11, categoryName: '螺栓与螺钉', model: 'DIN933 / M8×30', retailPrice: 0.68, stock: 12800, status: 'ON', mainImage: boltImage, specs: '材质：304 不锈钢\n规格：M8×30\n性能等级：A2-70', description: '适用于一般工业装配与户外连接，支持整箱采购。' },
  { id: 1002, name: '高强度内六角圆柱头螺钉', categoryId: 11, categoryName: '螺栓与螺钉', model: '12.9 级 / M6×20', retailPrice: 0.42, stock: 8600, status: 'ON', mainImage: boltImage, specs: '材质：合金钢\n表面：发黑\n规格：M6×20', description: '高强度机械设备紧固用螺钉。' },
  { id: 2001, name: '工业级锂电冲击钻', categoryId: 21, categoryName: '钻孔工具', model: '20V / 13mm', retailPrice: 329, stock: 46, status: 'ON', mainImage: drillImage, specs: '电压：20V\n夹头：13mm\n转速：0-1800rpm', description: '双电一充，适用于木材、金属与砖墙钻孔。' },
  { id: 3001, name: '静音液压缓冲铰链', categoryId: 31, categoryName: '铰链与滑轨', model: '全盖 / 冷轧钢', retailPrice: 8.6, stock: 320, status: 'ON', mainImage: hingeImage, specs: '类型：全盖\n材质：冷轧钢\n开启角度：105°', description: '橱柜门用液压阻尼铰链，开合安静顺畅。' },
  { id: 3002, name: '304 不锈钢暗铰链', categoryId: 31, categoryName: '铰链与滑轨', model: '4 寸 / 2.5mm', retailPrice: 12.8, stock: 0, status: 'OFF', mainImage: hingeImage, specs: '材质：304 不锈钢\n尺寸：4 寸\n厚度：2.5mm', description: '室内门用不锈钢平开合页。' },
  { id: 4001, name: '防割耐磨劳保手套', categoryId: 4, categoryName: '劳保用品', model: '5 级防割 / L', retailPrice: 6.5, stock: 760, status: 'ON', mainImage: gloveImage, specs: '等级：5 级防割\n尺码：L\n涂层：PU', description: '适用于五金搬运、玻璃及金属加工。' },
]

export const customers: Customer[] = [
  { id: 501, username: 'chenggong', realName: '陈工', phone: '138 0013 8000', level: 'vip', levelName: 'VIP客户' },
  { id: 502, username: 'hengyuan', realName: '恒源机电采购部', phone: '139 2211 0578', level: 'wholesale', levelName: '批发客户' },
  { id: 503, username: 'liufang', realName: '刘芳', phone: '136 7721 4102', level: 'retail', levelName: '零售客户' },
  { id: 504, username: 'xincheng', realName: '新城装饰', phone: '137 1190 6320', level: 'wholesale', levelName: '批发客户' },
]

export const orders: Order[] = [
  { id: 9001, orderNo: 'HG202611080001', customerName: '陈工', level: 'vip', status: 'PAID', productAmount: 1568, freightAmount: 0, totalAmount: 1568, receiver: '陈工', phone: '138 0013 8000', address: '广东省佛山市顺德区乐从镇工业区 8 号', createdAt: '2026-11-08 10:32', paidAt: '2026-11-08 10:35', items: [{ id: 1, productName: '工业级锂电冲击钻', model: '20V / 13mm', price: 289, quantity: 4, subtotal: 1156 }, { id: 2, productName: '静音液压缓冲铰链', model: '全盖 / 冷轧钢', price: 6.6, quantity: 60, subtotal: 412 }] },
  { id: 9002, orderNo: 'HG202611080002', customerName: '恒源机电采购部', level: 'wholesale', status: 'PENDING_PAYMENT', productAmount: 612, freightAmount: 12, totalAmount: 624, receiver: '周主管', phone: '139 2211 0578', address: '江苏省苏州市吴中区胥口工业园 21 栋', createdAt: '2026-11-08 11:18', items: [{ id: 3, productName: '304 不锈钢外六角螺栓', model: 'DIN933 / M8×30', price: 0.51, quantity: 1200, subtotal: 612 }] },
  { id: 9003, orderNo: 'HG202611070018', customerName: '新城装饰', level: 'wholesale', status: 'SHIPPED', productAmount: 928, freightAmount: 0, totalAmount: 928, receiver: '王经理', phone: '137 1190 6320', address: '浙江省杭州市拱墅区石桥路 156 号', createdAt: '2026-11-07 15:46', paidAt: '2026-11-07 15:49', items: [{ id: 4, productName: '静音液压缓冲铰链', model: '全盖 / 冷轧钢', price: 7.2, quantity: 100, subtotal: 720 }, { id: 5, productName: '防割耐磨劳保手套', model: '5 级防割 / L', price: 5.2, quantity: 40, subtotal: 208 }] },
  { id: 9004, orderNo: 'HG202611060009', customerName: '刘芳', level: 'retail', status: 'COMPLETED', productAmount: 335.5, freightAmount: 12, totalAmount: 347.5, receiver: '刘芳', phone: '136 7721 4102', address: '上海市浦东新区金桥路 88 号', createdAt: '2026-11-06 09:21', paidAt: '2026-11-06 09:23', items: [{ id: 6, productName: '工业级锂电冲击钻', model: '20V / 13mm', price: 329, quantity: 1, subtotal: 329 }, { id: 7, productName: '防割耐磨劳保手套', model: '5 级防割 / L', price: 6.5, quantity: 1, subtotal: 6.5 }] },
  { id: 9005, orderNo: 'HG202611050012', customerName: '刘芳', level: 'retail', status: 'CANCELLED', productAmount: 25.6, freightAmount: 12, totalAmount: 37.6, receiver: '刘芳', phone: '136 7721 4102', address: '上海市浦东新区金桥路 88 号', createdAt: '2026-11-05 17:02', items: [{ id: 8, productName: '304 不锈钢暗铰链', model: '4 寸 / 2.5mm', price: 12.8, quantity: 2, subtotal: 25.6 }] },
]

export const payments: Payment[] = [
  { id: 7001, orderNo: 'HG202611080001', tradeNo: 'WX420000251120261108103501', channel: 'wechat', amount: 1568, orderAmount: 1568, status: 'SUCCESS', createdAt: '2026-11-08 10:33', paidAt: '2026-11-08 10:35' },
  { id: 7002, orderNo: 'HG202611080002', tradeNo: '—', channel: 'alipay', amount: 624, orderAmount: 624, status: 'PENDING', createdAt: '2026-11-08 11:18' },
  { id: 7003, orderNo: 'HG202611070018', tradeNo: '202611072200147812140018', channel: 'alipay', amount: 928, orderAmount: 928, status: 'SUCCESS', createdAt: '2026-11-07 15:47', paidAt: '2026-11-07 15:49' },
  { id: 7004, orderNo: 'HG202611060009', tradeNo: 'WX420000251120261106092301', channel: 'wechat', amount: 347.5, orderAmount: 347.5, status: 'SUCCESS', createdAt: '2026-11-06 09:22', paidAt: '2026-11-06 09:23' },
]
