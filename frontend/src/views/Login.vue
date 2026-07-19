<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth   = useAuthStore()

const form    = ref({ username: '', password: '' })
const loading = ref(false)
const formRef = ref()

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码',   trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.doLogin(form.value.username, form.value.password)
    ElMessage.success(`欢迎回来，${auth.user.full_name || auth.user.username}`)
    router.push('/')
  } catch {
    // 错误已由 axios 拦截器统一弹出
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-box">
      <div class="login-logo">🔧</div>
      <h2 class="login-title">维修记录系统</h2>
      <p class="login-sub">请登录后使用</p>

      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="'User'"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="'Lock'"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          style="width:100%; margin-top:8px;"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <p style="margin-top:16px; color:#909399; font-size:13px; text-align:center;">
        默认账号：admin &nbsp;/&nbsp; admin123（首次登录请修改密码）
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a56db 0%, #0ea5e9 100%);
}
.login-box {
  width: 380px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.login-logo { font-size: 48px; text-align: center; margin-bottom: 8px; }
.login-title {
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: #1a56db;
  margin-bottom: 4px;
}
.login-sub { text-align: center; color: #909399; font-size: 14px; margin-bottom: 24px; }
</style>
