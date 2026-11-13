import type {
  CategoryOut,
  CustomerOut,
  OrderBriefOut,
  OrderDetailOut,
  PaymentOut,
  ProductBriefOut,
  ProductDetailOut,
} from './admin'
import type { Category, Customer, Order, OrderStatus, Payment, Product } from '@/types/business'
import { formatDateTime } from '@/utils/format'

export function mapCategory(item: CategoryOut, productCount = 0): Category {
  return {
    id: item.id,
    parentId: item.parent_id ?? null,
    name: item.name,
    sort: item.sort,
    productCount,
  }
}

export function mapProduct(item: ProductBriefOut, categoryName = '未分类'): Product {
  return {
    id: item.id,
    name: item.name,
    categoryId: item.category_id,
    categoryName,
    model: item.model ?? '',
    retailPrice: Number(item.retail_price),
    stock: item.stock,
    status: item.status === 'ON_SALE' || item.status === 'ON' ? 'ON' : 'OFF',
    mainImage: item.main_image ?? '',
    specs: '',
    description: '',
  }
}

export function mergeProductDetail(target: Product, detail: ProductDetailOut) {
  Object.assign(target, mapProduct(detail, target.categoryName), {
    description: detail.description ?? '',
    specs: detail.specs.map((item) => `${item.spec_name}：${item.spec_value}`).join('\n'),
  })
}

export function mapOrder(item: OrderBriefOut): Order {
  return {
    id: item.id,
    orderNo: item.order_no,
    status: item.status as OrderStatus,
    productAmount: Number(item.product_amount),
    freightAmount: Number(item.freight_amount),
    totalAmount: Number(item.total_amount),
    items: [],
    remark: item.remark,
    carrier: item.carrier,
    trackingNo: item.tracking_no,
    shippedAt: item.shipped_at ? formatDateTime(item.shipped_at) : null,
    createdAt: formatDateTime(item.created_at),
  }
}

export function mapOrderDetail(item: OrderDetailOut): Order {
  const address = item.address_snapshot
  const paidPayment = item.payments.find((payment) => payment.status === 'SUCCESS' && payment.paid_at)
  return {
    ...mapOrder(item),
    items: item.items.map((product) => ({
      id: product.id,
      productName: product.product_name,
      price: Number(product.price),
      quantity: product.quantity,
      subtotal: Number(product.subtotal),
    })),
    receiver: address?.receiver,
    phone: address?.phone,
    address: address ? `${address.region ?? ''}${address.detail ?? ''}` : undefined,
    paidAt: paidPayment?.paid_at ? formatDateTime(paidPayment.paid_at) : undefined,
  }
}

export function mapPayment(item: PaymentOut, orders: Map<number, Order>): Payment {
  const order = orders.get(item.order_id)
  return {
    id: item.id,
    orderId: item.order_id,
    orderNo: order?.orderNo ?? `订单 #${item.order_id}`,
    tradeNo: item.trade_no ?? '—',
    channel: item.channel === 'alipay' ? 'alipay' : 'wechat',
    amount: Number(item.amount),
    orderAmount: order?.totalAmount ?? null,
    status: item.status as Payment['status'],
    paidAt: item.paid_at ? formatDateTime(item.paid_at) : undefined,
  }
}

export function mapCustomer(item: CustomerOut): Customer {
  return {
    id: item.user_id,
    username: item.username,
    realName: item.real_name ?? '',
    phone: item.phone ?? '',
    level: (item.level_code as Customer['level']) ?? null,
    levelName: item.level_name ?? '',
  }
}
