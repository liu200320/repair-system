<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listConsumables, deleteConsumable, exportConsumable } from '../api/consumable'

const router = useRouter()

const loading    = ref(false)
const exporting  = ref(null)   // 正在导出的记录 id
const records    = ref([])
const total      = ref(0)

const query = reactive({ page: 1, page_size: 20, location: '', use_date: '' })

async function fetchList() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.location) params.location = query.location
    if (query.use_date) params.use_date = query.use_date
    const res = await listConsumables(params)
    records.value = res.items
    total.value   = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() { query.page = 1; fetchList() }
function resetSearch()  { query.location = ''; query.use_date = ''; handleSearch() }

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除「${row.record_no}」？此操作不可恢复。`, '删除确认', { type: 'warning' })
  await deleteConsumable(row.id)
  ElMessage.success('已删除')
  fetchList()
}

async function handleExport(row) {
  exporting.value = row.id
  try {
    // 使用原生 fetch 处理 blob 下载（axios blob 需要手动触发）
    const token = localStorage.getItem('repair_token')
    const resp  = await fetch(`/api/v1/consumables/${row.id}/export`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const blob     = await resp.blob()
    const url      = URL.createObjectURL(blob)
    const a        = document.createElement('a')
    a.href         = url
    a.download     = `耗材使用情况表_${row.record_no}.docx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    ElMessage.success('Word 已导出')
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally {
    exporting.value = null
  }
}

onMounted(fetchList)
</script>

<template>
  <div>
    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom:16px;">
      <el-form inline>
        <el-form-item label="使用地点">
          <el-input v-model="query.location" placeholder="模糊搜索" clearable style="width:200px"
            @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="使用日期">
          <el-date-picker v-model="query.use_date" type="date" value-format="YYYY-MM-DD"
            placeholder="精确查询" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
        <el-form-item style="margin-left:auto;">
          <el-button type="success" @click="router.push('/consumables/create')">
            <el-icon><Plus /></el-icon> 新建耗材记录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table :data="records" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="record_no" label="单号" width="160" />
        <el-table-column prop="use_date"  label="使用日期" width="120" />
        <el-table-column prop="location"  label="使用地点" min-width="200" show-overflow-tooltip />
        <el-table-column prop="item_count" label="耗材种类" width="90" align="center" />
        <el-table-column prop="notes" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/consumables/${row.id}`)">详情</el-button>
            <el-button size="small" type="primary" @click="router.push(`/consumables/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" type="success" :loading="exporting === row.id"
              @click="handleExport(row)">导出Word</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display:flex; justify-content:flex-end; margin-top:16px;">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchList"
          @size-change="() => { query.page = 1; fetchList() }"
        />
      </div>
    </el-card>
  </div>
</template>
