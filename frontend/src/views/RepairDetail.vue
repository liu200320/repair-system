<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRepairStore } from '../stores/repair'
import { exportWord } from '../api/repair'
import { ElMessage } from 'element-plus'
import PhotoUploader from '../components/PhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const store = useRepairStore()

const statusMap = {
  pending: { label: '待维修', type: 'warning' },
  in_progress: { label: '维修中', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
}
const phases = [
  { key: 'before', label: '维修前' },
  { key: 'during', label: '维修中' },
  { key: 'after',  label: '维修后' },
]

const exporting = ref(false)

async function load() {
  await store.fetchOne(Number(route.params.id))
}

async function handleExport() {
  exporting.value = true
  try {
    await exportWord(store.current.id, store.current.record_no)
    ElMessage.success('Word 文档已下载')
  } catch {
    ElMessage.error('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

function photosByPhase(phase) {
  return store.current?.photos?.filter(p => p.phase === phase) || []
}

onMounted(load)
</script>

<template>
  <div v-if="store.current">
    <!-- 工具栏 -->
    <div style="display:flex; gap:8px; margin-bottom:16px;">
      <el-button @click="router.push('/repairs')">← 返回列表</el-button>
      <el-button type="primary" @click="router.push(`/repairs/${store.current.id}/edit`)">编辑</el-button>
      <el-button type="success" :loading="exporting" @click="handleExport">
        <el-icon><Download /></el-icon> 导出 Word
      </el-button>
    </div>

    <!-- 基本信息 -->
    <el-card shadow="never" style="margin-bottom:16px;">
      <template #header>
        <span style="font-weight:600;">基本信息</span>
        <el-tag :type="statusMap[store.current.status]?.type" style="margin-left:12px;">
          {{ statusMap[store.current.status]?.label }}
        </el-tag>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="工单编号">{{ store.current.record_no }}</el-descriptions-item>
        <el-descriptions-item label="维修日期">{{ store.current.repair_date }}</el-descriptions-item>
        <el-descriptions-item label="维修点位" :span="2">{{ store.current.location }}</el-descriptions-item>
        <el-descriptions-item label="维修人员">{{ store.current.repairer || '—' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ store.current.created_at?.slice(0, 19).replace('T', ' ') }}</el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ store.current.description || '—' }}</el-descriptions-item>
        <el-descriptions-item label="维修内容" :span="2">{{ store.current.repair_content || '—' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 维修照片（维修前/中/后） -->
    <el-card shadow="never" v-for="phase in phases" :key="phase.key" style="margin-bottom:16px;">
      <template #header>
        <span style="font-weight:600;">📷 {{ phase.label }}照片</span>
      </template>
      <PhotoUploader
        :repair-id="store.current.id"
        :phase="phase.key"
        :photos="photosByPhase(phase.key)"
        @uploaded="load"
        @deleted="load"
      />
    </el-card>
  </div>

  <div v-else-if="store.loading" style="text-align:center; padding:60px;">
    <el-text>加载中...</el-text>
  </div>
</template>
