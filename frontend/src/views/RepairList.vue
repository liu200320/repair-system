<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRepairStore } from '../stores/repair'
import { exportWord, exportWordRange } from '../api/repair'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const store = useRepairStore()

const query = ref({ page: 1, page_size: 20, location: '', repair_date: '', status: '' })

// 批量导出日期范围
const rangeDialogVisible = ref(false)
const exportRange = ref([])          // [startDate, endDate]
const exporting = ref(false)

const statusMap = {
  pending:     { label: '待维修', type: 'warning' },
  in_progress: { label: '维修中', type: 'primary' },
  completed:   { label: '已完成', type: 'success' },
}

async function load() {
  const p = { ...query.value }
  if (!p.location)     delete p.location
  if (!p.repair_date)  delete p.repair_date
  if (!p.status)       delete p.status
  await store.fetchList(p)
}

function handlePageChange(page) {
  query.value.page = page
  load()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确认删除该维修记录？操作不可恢复', '删除确认', { type: 'warning' })
  await store.remove(id)
  ElMessage.success('删除成功')
  load()
}

async function handleExportSingle(row) {
  try {
    await exportWord(row.id, row.record_no)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  }
}

async function handleExportRange() {
  if (!exportRange.value || exportRange.value.length < 2) {
    ElMessage.warning('请先选择日期范围')
    return
  }
  const [start, end] = exportRange.value
  exporting.value = true
  try {
    await exportWordRange(start, end)
    ElMessage.success('批量导出成功，文件已下载')
    rangeDialogVisible.value = false
    exportRange.value = []
  } catch (err) {
    ElMessage.error(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 16px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
        <el-form :model="query" inline style="flex:1;">
          <el-form-item label="维修点位">
            <el-input v-model="query.location" placeholder="模糊搜索" clearable style="width:180px" />
          </el-form-item>
          <el-form-item label="维修日期">
            <el-date-picker
              v-model="query.repair_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width:160px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" placeholder="全部" clearable style="width:120px">
              <el-option label="待维修" value="pending" />
              <el-option label="维修中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="load">查询</el-button>
            <el-button @click="() => { query.location=''; query.repair_date=''; query.status=''; load() }">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 批量导出按钮 -->
        <el-button type="warning" @click="rangeDialogVisible = true">
          <el-icon><Download /></el-icon>&nbsp;按时间段批量导出 Word
        </el-button>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table :data="store.list" v-loading="store.loading" stripe>
        <el-table-column prop="record_no" label="工单编号" width="160" />
        <el-table-column prop="repair_date" label="维修日期" width="120" />
        <el-table-column prop="location" label="维修点位" min-width="160" show-overflow-tooltip />
        <el-table-column prop="repairer" label="维修人员" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">
              {{ statusMap[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="照片数" width="80" align="center">
          <template #default="{ row }">{{ row.photos?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/repairs/${row.id}`)">详情</el-button>
            <el-button size="small" type="primary" @click="router.push(`/repairs/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" type="success" @click="handleExportSingle(row)">导出</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 16px; justify-content: flex-end;"
        :total="store.total"
        :page-size="query.page_size"
        :current-page="query.page"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 批量导出对话框 -->
    <el-dialog
      v-model="rangeDialogVisible"
      title="按时间段批量导出 Word"
      width="420px"
      :close-on-click-modal="false"
    >
      <div style="padding: 8px 0;">
        <p style="margin-bottom:16px; color:#606266;">
          选择日期范围后，该时间段内的所有维修记录将汇总导出到<strong>一个 Word 文档</strong>，
          每条记录独占一页，照片按<strong>维修前 / 维修中 / 维修后</strong>各两张排列。
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
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="rangeDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="exporting"
          :disabled="!exportRange || exportRange.length < 2"
          @click="handleExportRange"
        >
          {{ exporting ? '导出中...' : '开始导出' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
