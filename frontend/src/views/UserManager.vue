<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

// ── 数据 ────────────────────────────────────────────────
const users   = ref([])
const loading = ref(false)

// ── 新建用户 ─────────────────────────────────────────────
const addVisible = ref(false)
const addForm    = ref({ username: '', password: '', full_name: '', role: 'viewer' })
const addRef     = ref()
const addSaving  = ref(false)
const addRules   = {
  username: [{ required: true, message: '请填写用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
}

// ── 编辑用户信息 ──────────────────────────────────────────
const editVisible = ref(false)
const editForm    = ref({ id: null, username: '', full_name: '', role: 'viewer', is_active: true })
const editRef     = ref()
const editSaving  = ref(false)
const editRules   = {
  username: [{ required: true, message: '请填写用户名', trigger: 'blur' }],
}

// ── 修改密码 ─────────────────────────────────────────────
const pwVisible = ref(false)
const pwForm    = ref({ id: null, name: '', password: '', confirm: '' })
const pwRef     = ref()
const pwSaving  = ref(false)
const pwRules   = {
  password: [{ required: true, min: 6, message: '密码至少6位',    trigger: 'blur' }],
  confirm:  [{ required: true,         message: '请再次输入密码',  trigger: 'blur' },
             { validator: (_, v, cb) => v === pwForm.value.password ? cb() : cb(new Error('两次密码不一致')), trigger: 'blur' }],
}

// ── 方法 ─────────────────────────────────────────────────
async function load() {
  loading.value = true
  try { users.value = await http.get('/auth/users') }
  finally { loading.value = false }
}

// 新建用户
async function submitAdd() {
  await addRef.value.validate()
  addSaving.value = true
  try {
    await http.post('/auth/users', addForm.value)
    ElMessage.success(`用户「${addForm.value.username}」已创建`)
    addVisible.value = false
    addForm.value = { username: '', password: '', full_name: '', role: 'viewer' }
    load()
  } finally { addSaving.value = false }
}

// 打开编辑
function openEdit(row) {
  editForm.value = { id: row.id, username: row.username, full_name: row.full_name || '', role: row.role, is_active: row.is_active }
  editVisible.value = true
}

// 保存编辑
async function submitEdit() {
  await editRef.value.validate()
  editSaving.value = true
  try {
    const { id, ...body } = editForm.value
    await http.put(`/auth/users/${id}`, body)
    ElMessage.success('用户信息已更新')
    editVisible.value = false
    load()
  } finally { editSaving.value = false }
}

// 打开改密码
function openPw(row) {
  pwForm.value = { id: row.id, name: row.username, password: '', confirm: '' }
  pwVisible.value = true
}

// 保存密码
async function submitPw() {
  await pwRef.value.validate()
  pwSaving.value = true
  try {
    await http.put(`/auth/users/${pwForm.value.id}/password`, { password: pwForm.value.password })
    ElMessage.success('密码已修改')
    pwVisible.value = false
  } finally { pwSaving.value = false }
}

// 删除用户
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用户「${row.username}」？此操作不可恢复。`, '删除确认', { type: 'warning' })
  await http.delete(`/auth/users/${row.id}`)
  ElMessage.success('用户已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <!-- 顶部操作栏 -->
    <el-card shadow="never" style="margin-bottom:16px;">
      <div style="display:flex; align-items:center; justify-content:space-between;">
        <span style="font-size:15px; font-weight:600;">用户管理</span>
        <el-button type="primary" @click="addVisible = true">
          <el-icon><Plus /></el-icon> 添加用户
        </el-button>
      </div>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="never">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id"        label="ID"   width="60"  align="center" />
        <el-table-column prop="username"  label="用户名" width="140" />
        <el-table-column prop="full_name" label="姓名"  width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'warning'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限说明" min-width="180">
          <template #default="{ row }">
            <span style="color:#909399; font-size:12px;">
              {{ row.role === 'admin'
                ? '可新建、编辑、删除记录，管理用户和点位'
                : '可查看、新建、编辑记录；不能删除记录' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openEdit(row)">编辑信息</el-button>
            <el-button size="small" type="warning" plain @click="openPw(row)">改密码</el-button>
            <el-button
              size="small" type="danger" plain
              :disabled="row.id === auth.user?.id"
              @click="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建用户弹窗 -->
    <el-dialog v-model="addVisible" title="添加用户" width="440px" :close-on-click-modal="false">
      <el-form ref="addRef" :model="addForm" :rules="addRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="addForm.full_name" placeholder="真实姓名（可选）" />
        </el-form-item>
        <el-form-item label="初始密码" prop="password">
          <el-input v-model="addForm.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="addForm.role">
            <el-radio value="viewer">普通用户（只读+新建+编辑）</el-radio>
            <el-radio value="admin">管理员（全部权限）</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="addSaving" @click="submitAdd">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户信息弹窗 -->
    <el-dialog v-model="editVisible" title="编辑用户信息" width="440px" :close-on-click-modal="false">
      <el-form ref="editRef" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.full_name" placeholder="可选" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="editForm.role">
            <el-radio value="viewer">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="账号状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwVisible" :title="`修改密码 — ${pwForm.name}`" width="400px" :close-on-click-modal="false">
      <el-form ref="pwRef" :model="pwForm" :rules="pwRules" label-width="80px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="pwForm.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="pwForm.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwSaving" @click="submitPw">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>
