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
  { path: '/consumables',        name: 'ConsumableList',   component: () => import('../views/ConsumableList.vue'), meta: { title: '耗材使用情况' } },
  { path: '/consumables/create', name: 'ConsumableCreate', component: () => import('../views/ConsumableForm.vue'), meta: { title: '新建耗材记录' } },
  { path: '/consumables/:id',    name: 'ConsumableDetail', component: () => import('../views/ConsumableForm.vue'), meta: { title: '耗材记录详情' } },
  { path: '/consumables/:id/edit', name: 'ConsumableEdit', component: () => import('../views/ConsumableForm.vue'), meta: { title: '编辑耗材记录' } },
  { path: '/network-inspections',        name: 'NetworkInspectionList',   component: () => import('../views/NetworkInspectionList.vue'), meta: { title: '网络基础设施巡检' } },
  { path: '/network-inspections/create', name: 'NetworkInspectionCreate', component: () => import('../views/NetworkInspectionForm.vue'), meta: { title: '新建巡检记录' } },
  { path: '/network-inspections/:id',    name: 'NetworkInspectionDetail', component: () => import('../views/NetworkInspectionForm.vue'), meta: { title: '巡检记录详情' } },
  { path: '/network-inspections/:id/edit', name: 'NetworkInspectionEdit', component: () => import('../views/NetworkInspectionForm.vue'), meta: { title: '编辑巡检记录' } },
  { path: '/access-inspections',          name: 'AccessInspectionList',   component: () => import('../views/AccessInspectionList.vue'), meta: { title: '门禁日常巡检' } },
  { path: '/access-inspections/create',   name: 'AccessInspectionCreate', component: () => import('../views/AccessInspectionForm.vue'), meta: { title: '新建门禁巡检记录' } },
  { path: '/access-inspections/:id',      name: 'AccessInspectionDetail', component: () => import('../views/AccessInspectionForm.vue'), meta: { title: '门禁巡检记录详情' } },
  { path: '/access-inspections/:id/edit', name: 'AccessInspectionEdit',   component: () => import('../views/AccessInspectionForm.vue'), meta: { title: '编辑门禁巡检记录' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — 维修记录系统` : '维修记录系统'
  if (to.meta.public) return true
  const token = localStorage.getItem('repair_token')
  if (!token) return { name: 'Login' }
})

export default router
