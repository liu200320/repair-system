<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth    = useAuthStore()
const list    = ref([])
const loading = ref(false)
const keyword = ref('')

// 新增表单
const addVisible = ref(false)
const addForm    = ref({ name: '', address: '', area: '' })
const addRef     = ref()
const saving     = ref(false)
const addRules   = {
  name: [{ required: true, message: '请填写点位名称', trigger: 'blur' }],
}

// 分页
const page     = ref(1)
const pageSize = 20
const filtered = computed(() =>
  keyword.value
    ? list.value.filter(p => p.name.includes(keyword.value))
    : list.value
)
const paged = computed(() =>
  filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize)
)

async function load() {
  loading.value = true
  try {
    list.value = await http.get('/monitor-points')
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  await addRef.value.validate()
  saving.value = true
  try {
    await http.post('/monitor-points', addForm.value)
    ElMessage.success(`点位「${addForm.value.name}」已添加`)
    addVisible.value = false
    addForm.value = { name: '', address: '', area: '' }
    load()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(
    `确认删除点位「${row.name}」？删除后新建记录时将无法从下拉选择此点位。`,
    '删除确认', { type: 'warning' }
  )
  await http.delete(`/monitor-points/${row.id}`)
  ElMessage.success('已删除')
  load()
}

function resetAdd() {
  addForm.value = { name: '', address: '', area: '' }
  addRef.value?.resetFields()
}

onMounted(load)
</script>

<template>
  <div>
    <!-- 顶部操作栏 -->
    <el-card shadow="never" style="margin-bottom:16px;">
      <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:15px; font-weight:600;">维修点位管理</span>
          <el-tag type="info">共 {{ list.length }} 个点位</el-tag>
        </div>
        <div style="display:flex; gap:8px;">
          <el-input
            v-model="keyword"
            placeholder="搜索点位名称"
            clearable
            style="width:200px"
            @input="page = 1"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" @click="addVisible = true">
            <el-icon><Plus /></el-icon> 添加点位
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 点位列表 -->
    <el-card shadow="never">
      <el-table :data="paged" v-loading="loading" stripe size="default">
        <el-table-column type="index" label="序号" width="60"
          :index="(i) => (page - 1) * pageSize + i + 1" />
        <el-table-column prop="name"    label="点位名称" min-width="200" />
        <el-table-column prop="area"    label="所属区域" width="140" show-overflow-tooltip />
        <el-table-column prop="address" label="详细地址" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="filtered.length > pageSize"
        style="margin-top:16px; justify-content:flex-end;"
        :total="filtered.length"
        :page-size="pageSize"
        :current-page="page"
        layout="total, prev, pager, next"
        @current-change="(p) => page = p"
      />
    </el-card>

    <!-- 添加点位弹窗 -->
    <el-dialog
      v-model="addVisible"
      title="添加维修点位"
      width="440px"
      :close-on-click-modal="false"
      @close="resetAdd"
    >
      <el-form ref="addRef" :model="addForm" :rules="addRules" label-width="80px">
        <el-form-item label="点位名称" prop="name">
          <el-input
            v-model="addForm.name"
            placeholder="如：图书馆配电房旁"
            autofocus
          />
        </el-form-item>
        <el-form-item label="所属区域">
          <el-input v-model="addForm.area" placeholder="可选，如：A区、教学区" />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="addForm.address" placeholder="可选，便于定位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>
