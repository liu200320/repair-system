<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

// ── 通用逻辑工厂 ─────────────────────────────────────────────
function makeTab(apiBase, label) {
  const list    = ref([])
  const loading = ref(false)
  const keyword = ref('')
  const page    = ref(1)
  const PAGE_SIZE = 20
  const addVisible = ref(false)
  const addName    = ref('')
  const saving     = ref(false)

  const filtered = computed(() =>
    keyword.value ? list.value.filter(p => p.name.includes(keyword.value)) : list.value
  )
  const paged = computed(() =>
    filtered.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE)
  )

  async function load() {
    loading.value = true
    try { list.value = await http.get(apiBase) }
    finally { loading.value = false }
  }

  async function handleAdd() {
    const name = addName.value.trim()
    if (!name) { ElMessage.warning('请填写点位名称'); return }
    saving.value = true
    try {
      await http.post(apiBase, { name })
      ElMessage.success(`${label}「${name}」已添加`)
      addVisible.value = false; addName.value = ''
      load()
    } finally { saving.value = false }
  }

  async function handleDelete(row) {
    await ElMessageBox.confirm(
      `确认删除${label}「${row.name}」？删除后巡检记录中将无法从下拉选择此点位。`,
      '删除确认', { type: 'warning' }
    )
    await http.delete(`${apiBase}/${row.id}`)
    ElMessage.success('已删除')
    load()
  }

  onMounted(load)

  return { list, loading, keyword, page, PAGE_SIZE, filtered, paged,
           addVisible, addName, saving, load, handleAdd, handleDelete }
}

// ── 三个 Tab 的数据 ──────────────────────────────────────────
const repair  = makeTab('/monitor-points',   '维修点位')
const network = makeTab('/network-locations', '网络巡检点位')
const access  = makeTab('/access-locations',  '门禁点位')

// 维修点位有额外字段
const repairAddForm = ref({ name: '', address: '', area: '' })
const repairAddRef  = ref()
const repairSaving  = ref(false)

async function handleRepairAdd() {
  await repairAddRef.value.validate()
  repairSaving.value = true
  try {
    await http.post('/monitor-points', repairAddForm.value)
    ElMessage.success(`维修点位「${repairAddForm.value.name}」已添加`)
    repair.addVisible.value = false
    repairAddForm.value = { name: '', address: '', area: '' }
    repair.load()
  } finally { repairSaving.value = false }
}
</script>

<template>
  <div>
    <el-tabs type="border-card">

      <!-- ── Tab 1：维修点位 ─────────────────────────── -->
      <el-tab-pane label="维修点位">
        <el-card shadow="never" style="margin-bottom:16px;">
          <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
              <span style="font-size:15px; font-weight:600;">维修点位管理</span>
              <el-tag type="info">共 {{ repair.list.value.length }} 个</el-tag>
            </div>
            <div style="display:flex; gap:8px;">
              <el-input v-model="repair.keyword.value" placeholder="搜索点位名称" clearable style="width:200px"
                @input="repair.page.value = 1">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
              <el-button type="primary" @click="repair.addVisible.value = true">
                <el-icon><Plus /></el-icon> 添加点位
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card shadow="never">
          <el-table :data="repair.paged.value" v-loading="repair.loading.value" stripe>
            <el-table-column type="index" label="序号" width="60"
              :index="(i) => (repair.page.value - 1) * repair.PAGE_SIZE + i + 1" />
            <el-table-column prop="name"    label="点位名称" min-width="200" />
            <el-table-column prop="area"    label="所属区域" width="140" show-overflow-tooltip />
            <el-table-column prop="address" label="详细地址" min-width="160" show-overflow-tooltip />
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="repair.handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-if="repair.filtered.value.length > repair.PAGE_SIZE"
            style="margin-top:16px; justify-content:flex-end;"
            :total="repair.filtered.value.length" :page-size="repair.PAGE_SIZE"
            :current-page="repair.page.value" layout="total, prev, pager, next"
            @current-change="(p) => repair.page.value = p" />
        </el-card>

        <el-dialog v-model="repair.addVisible.value" title="添加维修点位" width="440px"
          :close-on-click-modal="false" @close="repairAddForm = { name: '', address: '', area: '' }">
          <el-form ref="repairAddRef" :model="repairAddForm"
            :rules="{ name: [{ required: true, message: '请填写点位名称', trigger: 'blur' }] }"
            label-width="80px">
            <el-form-item label="点位名称" prop="name">
              <el-input v-model="repairAddForm.name" placeholder="如：图书馆配电房旁" autofocus />
            </el-form-item>
            <el-form-item label="所属区域">
              <el-input v-model="repairAddForm.area" placeholder="可选，如：A区" />
            </el-form-item>
            <el-form-item label="详细地址">
              <el-input v-model="repairAddForm.address" placeholder="可选" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="repair.addVisible.value = false">取消</el-button>
            <el-button type="primary" :loading="repairSaving" @click="handleRepairAdd">确认添加</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- ── Tab 2：网络巡检点位 ───────────────────────── -->
      <el-tab-pane label="网络巡检点位">
        <el-card shadow="never" style="margin-bottom:16px;">
          <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
              <span style="font-size:15px; font-weight:600;">网络巡检点位管理</span>
              <el-tag type="info">共 {{ network.list.value.length }} 个</el-tag>
            </div>
            <div style="display:flex; gap:8px;">
              <el-input v-model="network.keyword.value" placeholder="搜索点位名称" clearable style="width:200px"
                @input="network.page.value = 1">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
              <el-button type="primary" @click="network.addVisible.value = true">
                <el-icon><Plus /></el-icon> 添加点位
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card shadow="never">
          <el-table :data="network.paged.value" v-loading="network.loading.value" stripe>
            <el-table-column type="index" label="序号" width="60"
              :index="(i) => (network.page.value - 1) * network.PAGE_SIZE + i + 1" />
            <el-table-column prop="name" label="点位名称" min-width="280" />
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="network.handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-if="network.filtered.value.length > network.PAGE_SIZE"
            style="margin-top:16px; justify-content:flex-end;"
            :total="network.filtered.value.length" :page-size="network.PAGE_SIZE"
            :current-page="network.page.value" layout="total, prev, pager, next"
            @current-change="(p) => network.page.value = p" />
        </el-card>

        <el-dialog v-model="network.addVisible.value" title="添加网络巡检点位" width="420px" :close-on-click-modal="false">
          <el-form label-width="80px">
            <el-form-item label="点位名称">
              <el-input v-model="network.addName.value" placeholder="如：综合楼四楼弱电间" autofocus
                @keyup.enter="network.handleAdd()" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="network.addVisible.value = false; network.addName.value = ''">取消</el-button>
            <el-button type="primary" :loading="network.saving.value" @click="network.handleAdd()">确认添加</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- ── Tab 3：门禁点位 ───────────────────────────── -->
      <el-tab-pane label="门禁点位">
        <el-card shadow="never" style="margin-bottom:16px;">
          <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
              <span style="font-size:15px; font-weight:600;">门禁点位管理</span>
              <el-tag type="info">共 {{ access.list.value.length }} 个</el-tag>
            </div>
            <div style="display:flex; gap:8px;">
              <el-input v-model="access.keyword.value" placeholder="搜索点位名称" clearable style="width:200px"
                @input="access.page.value = 1">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
              <el-button type="primary" @click="access.addVisible.value = true">
                <el-icon><Plus /></el-icon> 添加点位
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card shadow="never">
          <el-table :data="access.paged.value" v-loading="access.loading.value" stripe>
            <el-table-column type="index" label="序号" width="60"
              :index="(i) => (access.page.value - 1) * access.PAGE_SIZE + i + 1" />
            <el-table-column prop="name" label="门禁地点名称" min-width="280" />
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="access.handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-if="access.filtered.value.length > access.PAGE_SIZE"
            style="margin-top:16px; justify-content:flex-end;"
            :total="access.filtered.value.length" :page-size="access.PAGE_SIZE"
            :current-page="access.page.value" layout="total, prev, pager, next"
            @current-change="(p) => access.page.value = p" />
        </el-card>

        <el-dialog v-model="access.addVisible.value" title="添加门禁点位" width="420px" :close-on-click-modal="false">
          <el-form label-width="80px">
            <el-form-item label="门禁地点">
              <el-input v-model="access.addName.value" placeholder="如：学校大门口" autofocus
                @keyup.enter="access.handleAdd()" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="access.addVisible.value = false; access.addName.value = ''">取消</el-button>
            <el-button type="primary" :loading="access.saving.value" @click="access.handleAdd()">确认添加</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>
