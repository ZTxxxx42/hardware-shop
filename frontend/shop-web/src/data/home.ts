import type { Category, NewsItem, Product } from '@/types/catalog'

export const categories: Category[] = [
  { id: 1, name: '手动工具', icon: 'wrench', description: '扳手 · 钳类 · 套筒' },
  { id: 2, name: '电动工具', icon: 'drill', description: '钻孔 · 切割 · 打磨' },
  { id: 3, name: '紧固件', icon: 'fastener', description: '螺栓 · 螺母 · 垫圈' },
  { id: 4, name: '建筑五金', icon: 'hinge', description: '合页 · 锁具 · 连接件' },
  { id: 5, name: '机械配件', icon: 'bearing', description: '轴承 · 传动 · 密封' },
  { id: 6, name: '五金型材', icon: 'profile', description: '钢材 · 铝材 · 管材' },
]

export const hotProducts: Product[] = [
  { id: 101, name: '不锈钢外六角螺栓', model: 'M6–M20', material: '304 不锈钢', artwork: 'bolt', tag: '工程常备' },
  { id: 102, name: '高强度六角螺母', model: 'M6–M24', material: '8.8 级碳钢', artwork: 'nut', tag: '规格齐全' },
  { id: 103, name: '加厚不锈钢平垫圈', model: 'M6–M24', material: '316 不锈钢', artwork: 'washer' },
  { id: 104, name: '重型膨胀螺栓', model: 'M6–M16', material: '热镀锌碳钢', artwork: 'anchor', tag: '坚固耐用' },
  { id: 105, name: '不锈钢静音合页', model: '50–100 mm', material: '304 不锈钢', artwork: 'hinge' },
  { id: 106, name: '深沟球轴承', model: '6200 系列', material: '高碳铬轴承钢', artwork: 'bearing', tag: '低噪耐用' },
  { id: 106, name: '深沟球轴承', model: '6200 系列', material: '高碳铬轴承钢', artwork: 'bearing', tag: '低噪耐用' },
]

export const newsItems: NewsItem[] = [
  {
    id: 1,
    date: '09-15',
    year: '2025',
    title: '如何选择高质量的五金紧固件？',
    summary: '从材质、强度等级到表面处理，快速掌握工业紧固件选型要点。',
  },
  {
    id: 2,
    date: '08-28',
    year: '2025',
    title: '五金行业发展趋势：智能化与绿色制造',
    summary: '数字化供应链与低碳工艺，正在重塑五金产品的生产与交付。',
  },
]
