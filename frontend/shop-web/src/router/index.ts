import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: '首页' } },
    { path: '/categories', name: 'categories', component: () => import('@/views/CategoryView.vue'), meta: { title: '产品分类' } },
    { path: '/products', name: 'products', component: () => import('@/views/ProductListView.vue'), meta: { title: '产品中心' } },
    { path: '/products/:id', name: 'product-detail', component: () => import('@/views/ProductDetailView.vue'), meta: { title: '商品详情' } },
    { path: '/search', name: 'search', component: () => import('@/views/SearchView.vue'), meta: { title: '搜索商品' } },
    { path: '/cart', name: 'cart', component: () => import('@/views/CartView.vue'), meta: { title: '购物车' } },
    { path: '/checkout', name: 'checkout', component: () => import('@/views/CheckoutView.vue'), meta: { title: '结算下单' } },
    { path: '/orders', name: 'orders', component: () => import('@/views/OrderView.vue'), meta: { title: '订单中心' } },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { title: '登录' } },
    { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { title: '注册' } },
    { path: '/account', name: 'account', component: () => import('@/views/AccountView.vue'), meta: { title: '个人中心' } },
    { path: '/addresses', name: 'addresses', component: () => import('@/views/AddressView.vue'), meta: { title: '地址管理' } },
    { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue'), meta: { title: '关于我们' } },
    { path: '/news', name: 'news', component: () => import('@/views/NewsView.vue'), meta: { title: '新闻资讯' } },
    { path: '/support', name: 'support', component: () => import('@/views/SupportView.vue'), meta: { title: '服务支持' } },
    { path: '/contact', name: 'contact', component: () => import('@/views/ContactView.vue'), meta: { title: '联系我们' } },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue'), meta: { title: '页面未找到' } },
  ],
})

router.afterEach((to) => {
  document.title = `${String(to.meta.title ?? '页面')}｜恒泰五金商贸`
})

export default router
