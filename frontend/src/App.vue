<script setup>
import { computed, ref, markRaw, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { ElMessageBox } from 'element-plus'
import {
  Tools, Box, Connection, Lock, DataAnalysis,
  Location, UserFilled, ArrowDown, Fold, Expand,
} from '@element-plus/icons-vue'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const isLoginPage  = computed(() => route.name === 'Login')
const isCollapsed  = ref(false)
const isMobile     = ref(false)
const showOverlay  = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isCollapsed.value = true
    showOverlay.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => window.removeEventListener('resize', checkMobile))

function toggleSidebar() {
  if (isMobile.value) {
    showOverlay.value = !showOverlay.value
  } else {
    isCollapsed.value = !isCollapsed.value
  }
}

function closeOverlay() {
  showOverlay.value = false
}

// 桌面端: 展开220 / 收起64；移动端: 始终220（overlay）
const sidebarWidth  = computed(() => isCollapsed.value && !isMobile.value ? '64px' : '220px')
const contentMargin = computed(() => isMobile.value ? '0px' : (isCollapsed.value ? '64px' : '220px'))
// 移动端侧边栏可见性由 showOverlay 控制
const sidebarVisible = computed(() => isMobile.value ? showOverlay.value : true)

async function handleLogout() {
  await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
  auth.logout()
  router.push('/login')
}

const menuItems = computed(() => [
  { index: '/repairs',             label: '维修记录', icon: markRaw(Tools) },
  { index: '/consumables',         label: '耗材管理', icon: markRaw(Box) },
  { index: '/network-inspections', label: '网络巡检', icon: markRaw(Connection) },
  { index: '/access-inspections',  label: '门禁巡检', icon: markRaw(Lock) },
  { index: '/dashboard',           label: '统计看板', icon: markRaw(DataAnalysis) },
  ...(auth.isAdmin ? [
    { index: '/locations', label: '点位管理', icon: markRaw(Location) },
    { index: '/users',     label: '用户管理', icon: markRaw(UserFilled) },
  ] : []),
])

const avatarLetter = computed(() => {
  const name = auth.user?.full_name || auth.user?.username || '?'
  return name[0].toUpperCase()
})
</script>

<template>
  <template v-if="isLoginPage">
    <router-view />
  </template>

  <div v-else class="app-layout">
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && showOverlay" class="sidebar-overlay" @click="closeOverlay" />

    <!-- 左侧边栏 -->
    <aside
      class="app-sidebar"
      :class="{ 'sidebar-hidden': isMobile && !showOverlay, 'sidebar-collapsed': isCollapsed && !isMobile }"
      :style="{ width: sidebarWidth }"
    >
      <!-- Logo区 + 桌面收起按钮 -->
      <div class="sidebar-logo" @click="router.push('/')">
        <el-icon size="20" style="flex-shrink:0"><Tools /></el-icon>
        <span v-show="!isCollapsed || isMobile" class="logo-text">维修记录系统</span>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="isCollapsed && !isMobile"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        :style="{
          '--el-menu-bg-color': 'transparent',
          '--el-menu-text-color': 'rgba(255,255,255,0.75)',
          '--el-menu-active-color': '#ffffff',
          '--el-menu-hover-bg-color': 'rgba(255,255,255,0.15)',
        }"
        @select="isMobile && closeOverlay()"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部：用户信息 + 收起按钮 -->
      <div class="sidebar-footer">
        <!-- 用户信息（收起时只显示头像） -->
        <el-dropdown @command="cmd => cmd === 'logout' && handleLogout()">
          <div class="sidebar-user" :class="{ 'user-collapsed': isCollapsed && !isMobile }">
            <el-avatar size="32" class="user-avatar">{{ avatarLetter }}</el-avatar>
            <div v-show="!isCollapsed || isMobile" class="user-text">
              <span class="user-name">{{ auth.user?.full_name || auth.user?.username }}</span>
              <span class="user-role">{{ auth.isAdmin ? '管理员' : '只读' }}</span>
            </div>
            <el-icon v-show="!isCollapsed || isMobile" class="user-arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 收起/展开按钮（仅桌面端） -->
        <button v-if="!isMobile" class="collapse-btn" @click="toggleSidebar">
          <el-icon size="16">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="app-content" :style="{ marginLeft: contentMargin }">
      <!-- 移动端顶栏（汉堡菜单） -->
      <div v-if="isMobile" class="mobile-topbar">
        <button class="hamburger" @click="toggleSidebar">
          <span /><span /><span />
        </button>
        <span class="mobile-title">维修记录系统</span>
      </div>

      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout { display: flex; min-height: 100vh; }

.app-sidebar {
  position: fixed;
  top: 0; left: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  z-index: 200;
  transition: width 0.25s ease, transform 0.25s ease;
  overflow: hidden;
}
.sidebar-hidden { transform: translateX(-100%); }

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 18px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  border: none !important;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
}
:deep(.sidebar-menu .el-menu-item) {
  height: 44px;
  line-height: 44px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: rgba(255,255,255,0.75);
  white-space: nowrap;
}
:deep(.sidebar-menu:not(.el-menu--collapse) .el-menu-item) { margin: 2px 10px; }
:deep(.sidebar-menu.el-menu--collapse .el-menu-item) {
  margin: 2px 4px;
  padding: 0 !important;
  justify-content: center;
}
:deep(.sidebar-menu .el-menu-item.is-active) {
  background-color: rgba(255,255,255,0.18) !important;
  color: #ffffff !important;
}
:deep(.sidebar-menu .el-menu-item:hover) {
  background-color: rgba(255,255,255,0.12) !important;
  color: #ffffff !important;
}

.sidebar-footer {
  padding: 10px 12px 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 6px 8px;
  transition: background 0.2s;
  overflow: hidden;
}
.sidebar-user:hover { background: rgba(255,255,255,0.1); }
.user-collapsed { justify-content: center; padding: 6px 4px; }
.user-avatar {
  flex-shrink: 0;
  background: rgba(255,255,255,0.2) !important;
  color: #fff !important;
  font-size: 14px;
}
.user-text {
  flex: 1; overflow: hidden;
  display: flex; flex-direction: column; gap: 2px; min-width: 0;
}
.user-name {
  color: #fff; font-size: 13px; font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;
}
.user-role  { color: rgba(255,255,255,0.55); font-size: 11px; display: block; }
.user-arrow { color: rgba(255,255,255,0.45); flex-shrink: 0; }

.collapse-btn {
  width: 100%;
  background: rgba(255,255,255,0.08);
  border: none;
  border-radius: var(--radius-sm);
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 6px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.collapse-btn:hover { background: rgba(255,255,255,0.16); }

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 199;
}

.app-content {
  flex: 1;
  min-height: 100vh;
  background: var(--color-bg);
  padding: 24px;
  transition: margin-left 0.25s ease;
}

.mobile-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: -24px -24px 20px;
  padding: 12px 16px;
  background: var(--color-primary);
  color: #fff;
}
.mobile-title { font-size: 15px; font-weight: 700; }

.hamburger {
  background: none; border: none; cursor: pointer;
  padding: 4px; display: flex; flex-direction: column; gap: 5px;
}
.hamburger span { display: block; width: 22px; height: 2px; background: #fff; border-radius: 2px; }
</style>
