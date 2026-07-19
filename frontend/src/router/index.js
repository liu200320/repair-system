import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true, title: '登录' } },
  { path: '/', redirect: '/repairs' },
  { path: '/repairs', name: 'RepairList', component: () => import('../views/RepairList.vue'), meta: { title: '维修记录列表' } },
  { path: '/repairs/create', name: 'RepairCreate', component: () => import('../views/RepairForm.vue'), meta: { title: '新建维修记录' } },
  { path: '/repairs/:id', name: 'RepairDetail', component: () => import('../views/RepairDetail.vue'), meta: { title: '维修记录详情' } },
  { path: '/repairs/:id/edit', name: 'RepairEdit', component: () => import('../views/RepairForm.vue'), meta: { title: '编辑维修记录' } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '统计看板' } },
  { path: '/locations', name: 'Locations', component: () => import('../views/LocationManager.vue'), meta: { title: '点位管理' } },
  { path: '/users',     name: 'Users',     component: () => import('../views/UserManager.vue'),    meta: { title: '用户管理' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — 维修记录系统` : '维修记录系统'
  if (to.meta.public) return true
  const token = localStorage.getItem('repair_token')
  if (!token) return { name: 'Login' }
})

export default router
