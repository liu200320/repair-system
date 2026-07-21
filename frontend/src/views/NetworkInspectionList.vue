<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listNetworkInspections, deleteNetworkInspection, exportNetworkInspectionRange } from '../api/networkInspection'

const router  = useRouter()
const loading  = ref(false)
const exporting= ref(null)
const records  = ref([])
const total    = ref(0)

const query = reactive({ page: 1, page_size: 20, location: '', inspect_date: '' })

// 批量导出
const rangeDialogVisible = ref(false)
const exportRange        = ref([])
const exportingRange     = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.location)     params.location     = query.location
    if (query.inspect_date) params.inspect_date = query.inspect_date
    const res = await listNetworkInspections(params)
    records.value = res.items
    total.value   = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() { query.page = 1; fetchList() }
function resetSearch()  { query.location = ''; query.inspect_date = ''; handleSearch() }

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除「${row.record_no}」？此操作不可恢复。`, '删除确认', { type: 'warning' })
  await deleteNetworkInspection(row.id)
  ElMessage.success('已删除')
  fetchList()
}

async function handleExport(row) {
  exporting.value = row.id
  try {
    const token = localStorage.getItem('repair_token')
    const resp  = await fetch(`/api/v1/network-inspections/${row.id}/export`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const blob = await resp.blob()
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `网络基础设施巡检表_${row.record_no}.docx`
    document.body.appendChild(a); a.click(); a.remove()
    URL.revokeObjectURL(url)
    ElMessage.success('Word 已导出')
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally {
    exporting.value = null
  }
}

async function handleExportRange() {
  if (!exportRange.value || exportRange.value.length < 2) {
    ElMessage.warning('请先选择日期范围')
    return
  }
  const [start, end] = exportRange.value
  exportingRange.value = true
  try {
    await exportNetworkInspectionRange(start, end)
    ElMessage.success('批量导出成功，文件已下载')
    rangeDialogVisible.value = false
    exportRange.value = []
  } catch (err) {
    ElMessage.error(err.message || '导出失败')
  } finally {
    exportingRange.value = false
  }
}

onMounted(fetchList)
</script>

<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
        <el-form inline style="flex:1;">
          <el-form-item label="巡检地点">
            <el-input v-model="query.location" placeholder="模糊搜索" clearable style="width:200px"
              @keyup.enter="handleSearch" />
          </el-form-item>
          <el-form-item label="巡检日期">
            <el-date-picker v-model="query.inspect_date" type="date" value-format="YYYY-MM-DD"
              placeholder="精确查询" clearable style="width:160px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <div style="display:flex; gap:8px; flex-shrink:0;">
          <el-button type="warning" @click="rangeDialogVisible = true">
            按时间段批量导出 Word
          </el-button>
          <el-button type="success" @click="router.push('/network-inspections/create')">
            <el-icon><Plus /></el-icon> 新建巡检记录
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table :data="records" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="record_no"    label="单号"     width="160" />
        <el-table-column prop="inspect_date" label="巡检日期" width="120" />
        <el-table-column prop="location"     label="巡检地点" min-width="200" show-overflow-tooltip />
        <el-table-column prop="inspector"    label="巡检人员" width="120" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/network-inspections/${row.id}`)">详情</el-button>
            <el-button size="small" type="primary" @click="router.push(`/network-inspections/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" type="success" :loading="exporting === row.id" @click="handleExport(row)">导出Word</el-button>
            <el-button size="small" type="danger"  @click="handleDelete(row)">删除</el-button>
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

    <!-- 批量导出对话框 -->
    <el-dialog
      v-model="rangeDialogVisible"
      title="按时间段批量导出 Word"
      width="420px"
      :close-on-click-modal="false"
    >
      <div style="padding:8px 0;">
        <p style="margin-bottom:16px; color:#606266;">
          选择日期范围后，该时间段内的所有巡检记录将汇总导出到
          <strong>一个 Word 文档</strong>，每条记录独占一页，含照片。
        </p>
        <el-form label-width="80px">
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="exportRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width:100%;"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="rangeDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="exportingRange"
          :disabled="!exportRange || exportRange.length < 2"
          @click="handleExportRange"
        >
          {{ exportingRange ? '导出中...' : '开始导出' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
