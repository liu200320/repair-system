<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRepairStore } from '../stores/repair'
import http from '../api/http'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route  = useRoute()
const store  = useRepairStore()

const isEdit    = computed(() => !!route.params.id)
const title     = computed(() => isEdit.value ? '编辑维修记录' : '新建维修记录')
const locations = ref([])   // 来自 monitor_points 的点位列表

const form = ref({ repair_date: '', location: '', description: '', repair_content: '', repairer: '', status: 'pending' })
const rules = {
  repair_date: [{ required: true, message: '请选择维修日期', trigger: 'change' }],
  location:    [{ required: true, message: '请选择或输入维修点位', trigger: 'blur'   }],
}
const formRef = ref()
const saving  = ref(false)

onMounted(async () => {
  // 从 monitor_points 表加载点位下拉列表
  try {
    locations.value = await http.get('/monitor-points')
  } catch {}

  if (isEdit.value) {
    await store.fetchOne(Number(route.params.id))
    const r = store.current
    if (r) form.value = { repair_date: r.repair_date, location: r.location,
      description: r.description || '', repair_content: r.repair_content || '',
      repairer: r.repairer || '', status: r.status }
  }
})

async function submit() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await store.update(Number(route.params.id), form.value)
      ElMessage.success('更新成功')
      router.back()
    } else {
      const created = await store.create(form.value)
      ElMessage.success('创建成功，可在详情页上传照片')
      router.push(`/repairs/${created.id}`)
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <el-card shadow="never">
    <template #header><span style="font-size:16px;font-weight:600;">{{ title }}</span></template>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="max-width:600px">
      <el-form-item label="维修日期" prop="repair_date">
        <el-date-picker v-model="form.repair_date" type="date" value-format="YYYY-MM-DD"
          placeholder="请选择" style="width:100%" />
      </el-form-item>

      <el-form-item label="维修点位" prop="location">
        <!-- 有点位库时显示下拉+可自由输入；无点位库时退化为普通输入框 -->
        <el-select v-if="locations.length"
          v-model="form.location"
          filterable
          allow-create
          default-first-option
          placeholder="选择或输入点位名称"
          style="width:100%"
        >
          <el-option v-for="loc in locations" :key="loc.id" :label="loc.name" :value="loc.name" />
        </el-select>
        <el-input v-else v-model="form.location" placeholder="如：3号厂房-配电柜-A区" />
        <div style="font-size:12px;color:#909399;margin-top:4px;">
          可在「点位管理」中预设点位列表；也可直接输入新名称
        </div>
      </el-form-item>

      <el-form-item label="维修人员">
        <el-input v-model="form.repairer" placeholder="可选" />
      </el-form-item>

      <el-form-item label="状态">
        <el-select v-model="form.status" style="width:100%">
          <el-option label="待维修" value="pending" />
          <el-option label="维修中" value="in_progress" />
          <el-option label="已完成" value="completed" />
        </el-select>
      </el-form-item>

      <el-form-item label="故障描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="描述故障现象" />
      </el-form-item>

      <el-form-item label="维修内容">
        <el-input v-model="form.repair_content" type="textarea" :rows="3" placeholder="描述维修措施" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
