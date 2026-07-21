<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const isLoginPage = computed(() => route.name === 'Login')

async function handleLogout() {
  await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <!-- 登录页不显示导航 -->
  <template v-if="isLoginPage">
    <router-view />
  </template>

  <el-container v-else style="min-height: 100vh;">
    <!-- 顶部导航 -->
    <el-header style="background:#1a56db; display:flex; align-items:center; justify-content:space-between; padding:0 20px;">
      <!-- 左：Logo + 导航 -->
      <div style="display:flex; align-items:center; gap:24px;">
        <span style="color:#fff; font-size:18px; font-weight:700; cursor:pointer;" @click="router.push('/')">
          🔧 维修记录系统
        </span>
        <el-menu mode="horizontal" background-color="#1a56db" text-color="#c8d9f8" active-text-color="#ffffff"
          :default-active="route.path" router style="border:none; height:60px;">
          <el-menu-item index="/repairs">维修记录</el-menu-item>
          <el-menu-item index="/consumables">耗材管理</el-menu-item>
          <el-menu-item index="/network-inspections">网络巡检</el-menu-item>
          <el-menu-item index="/access-inspections">门禁巡检</el-menu-item>
          <el-menu-item index="/dashboard">统计看板</el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/locations">点位管理</el-menu-item>
          <el-menu-item v-if="auth.isAdmin" index="/users">用户管理</el-menu-item>
        </el-menu>
      </div>

      <!-- 右：用户 -->
      <div style="display:flex; align-items:center; gap:12px;">
        <el-dropdown @command="(cmd) => cmd === 'logout' && handleLogout()">
          <span style="color:#c8d9f8; cursor:pointer; font-size:14px;">
            👤 {{ auth.user?.full_name || auth.user?.username }}
            <el-tag size="small" :type="auth.isAdmin ? 'danger' : 'info'" style="margin-left:4px;">
              {{ auth.isAdmin ? '管理员' : '只读' }}
            </el-tag>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main style="background:#f5f7fa; padding:24px;">
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
.el-menu--horizontal > .el-menu-item { border-bottom: none !important; }
</style>
