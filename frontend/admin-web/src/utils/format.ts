import type { CustomerLevel, OrderStatus } from '@/types/business'

type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

export function formatMoney(value: number) {
  return `¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function formatDateTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export const levelMeta: Record<CustomerLevel, { label: string; type: TagType }> = {
  retail: { label: '零售', type: 'info' },
  wholesale: { label: '批发', type: 'primary' },
  vip: { label: 'VIP', type: 'warning' },
}

export const orderStatusMeta: Record<OrderStatus, { label: string; type: TagType }> = {
  PENDING_PAYMENT: { label: '待支付', type: 'warning' },
  PAID: { label: '已支付', type: 'primary' },
  SHIPPED: { label: '已发货', type: 'primary' },
  COMPLETED: { label: '已完成', type: 'success' },
  CANCELLED: { label: '已取消', type: 'info' },
}
