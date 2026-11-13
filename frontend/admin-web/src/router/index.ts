import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory('/admin/'),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { title: '登录', public: true },
    },
    {
      path: '/',
      component: () => import('@/layout/AdminLayout.vue'),
      redirect: '/products',
      children: [
        { path: 'products', name: 'products', component: () => import('@/views/products/ProductList.vue'), meta: { title: '商品管理' } },
        { path: 'categories', name: 'categories', component: () => import('@/views/categories/CategoryList.vue'), meta: { title: '分类管理' } },
        { path: 'prices', name: 'prices', component: () => import('@/views/prices/PriceList.vue'), meta: { title: '价格管理' } },
        { path: 'customers', name: 'customers', component: () => import('@/views/customers/CustomerList.vue'), meta: { title: '客户管理' } },
        { path: 'orders', name: 'orders', component: () => import('@/views/orders/OrderList.vue'), meta: { title: '订单管理' } },
        { path: 'payments', name: 'payments', component: () => import('@/views/payments/PaymentList.vue'), meta: { title: '支付流水' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/products' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  document.title = `${to.meta.title ?? '运营管理'} · 恒泰五金`
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.isAuthenticated) return { name: 'products' }
  return true
})

export default router
