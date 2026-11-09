import type { Category, CategoryIconName } from '@/types/catalog'

const categoryIcons: Record<string, CategoryIconName> = {
  手动工具: 'wrench',
  电动工具: 'drill',
  紧固件: 'fastener',
  建筑五金: 'hinge',
  机械配件: 'bearing',
  五金型材: 'profile',
}

const categoryDescriptions: Record<string, string> = {
  手动工具: '扳手 · 钳类 · 套筒',
  电动工具: '钻孔 · 切割 · 打磨',
  紧固件: '螺栓 · 螺母 · 垫圈',
  建筑五金: '合页 · 锁具 · 连接件',
  机械配件: '轴承 · 传动 · 密封',
  五金型材: '钢材 · 铝材 · 管材',
}

export function getCategoryIcon(category: Pick<Category, 'name'>): CategoryIconName {
  return categoryIcons[category.name] ?? 'grid'
}

export function getCategoryDescription(category: Pick<Category, 'name'>): string {
  return categoryDescriptions[category.name] ?? `浏览全部${category.name}商品`
}

export function formatPrice(value: string): string {
  const amount = Number(value)
  if (!Number.isFinite(amount)) return value
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function isZeroAmount(value: string): boolean {
  return value === '' || value === '0' || value === '0.00'
}

export function getProductStatus(status: string): string {
  const statuses: Record<string, string> = {
    ON_SALE: '在售',
    OFF_SALE: '已下架',
    DRAFT: '未发布',
  }
  return statuses[status] ?? '状态待确认'
}
