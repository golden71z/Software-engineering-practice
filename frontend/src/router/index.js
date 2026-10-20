import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

/**
 * 路由表。
 *
 * 权限控制分两层：
 * - 前端 meta.requiresAuth / meta.roles 只做"体验优化"（未登录直接跳走，不发无效请求）
 * - 真正的安全边界在后端：每个接口自己校验令牌和角色
 * 前端守卫可以被绕过（改 localStorage 就行），所以绝不能当成唯一防线。
 */
const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { guestOnly: true, title: '登录' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { guestOnly: true, title: '注册' },
  },
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/Home.vue'), meta: { title: '首页' } },
      {
        path: 'items',
        name: 'items',
        component: () => import('@/views/item/ItemList.vue'),
        meta: { title: '失物招领' },
      },
      {
        path: 'items/:id',
        name: 'item-detail',
        component: () => import('@/views/item/ItemDetail.vue'),
        meta: { title: '详情' },
      },
      {
        path: 'publish',
        name: 'publish',
        component: () => import('@/views/item/ItemPublish.vue'),
        meta: { title: '发布信息', requiresAuth: true },
      },
      {
        path: 'my/items',
        name: 'my-items',
        component: () => import('@/views/item/MyItems.vue'),
        meta: { title: '我的发布', requiresAuth: true },
      },
      {
        path: 'my/claims',
        name: 'my-claims',
        component: () => import('@/views/claim/MyClaims.vue'),
        meta: { title: '我的认领', requiresAuth: true },
      },
      {
        path: 'my/received',
        name: 'received-claims',
        component: () => import('@/views/claim/ReceivedClaims.vue'),
        meta: { title: '收到的申请', requiresAuth: true },
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据看板' },
      },
      {
        path: 'items',
        name: 'admin-items',
        component: () => import('@/views/admin/ItemManage.vue'),
        meta: { title: '内容管理' },
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: () => import('@/views/admin/CategoryManage.vue'),
        meta: { title: '分类管理' },
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'notices',
        name: 'admin-notices',
        component: () => import('@/views/admin/NoticeManage.vue'),
        meta: { title: '公告管理' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const user = useUserStore()

  if (to.meta.requiresAuth && !user.isLogin) {
    ElMessage.warning('请先登录')
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.meta.roles && !to.meta.roles.includes(user.profile?.role)) {
    ElMessage.error('没有访问权限')
    return { path: '/' }
  }

  if (to.meta.guestOnly && user.isLogin) {
    return { path: '/' }
  }

  document.title = to.meta.title ? `${to.meta.title} · 校园失物招领` : '校园失物招领'
  return true
})

export default router
