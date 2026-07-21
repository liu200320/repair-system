<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Upload } from '@element-plus/icons-vue'
import {
  createAccessInspection, getAccessInspection, updateAccessInspection,
  uploadAccessInspectionPhoto, deleteAccessInspectionPhoto, getAccessLocations,
} from '../api/accessInspection'

const router = useRouter()
const route  = useRoute()

const isEdit    = computed(() => !!route.params.id)
const recordId  = computed(() => isEdit.value ? Number(route.params.id) : null)
const pageTitle = computed(() => isEdit.value ? '编辑门禁巡检记录' : '新建门禁巡检记录')

const locationOptions = ref([])
const formRef = ref()
const saving  = ref(false)
const form = ref({
  inspect_date: '', location: '', inspector: '',
  gate_status: '', flap_status: '', system_status: '', other_device: '',
  fault_description: '', repair_content: '',
})
const rules = {
  inspect_date: [{ required: true, message: '请选择巡检日期', trigger: 'change' }],
  location:     [{ required: true, message: '请选择门禁地点', trigger: 'change' }],
}

const photos    = ref([])
const uploading = ref(false)

onMounted(async () => {
  locationOptions.value = await getAccessLocations()
  if (!isEdit.value) return
  try {
    const record = await getAccessInspection(recordId.value)
    Object.keys(form.value).forEach(k => { form.value[k] = record[k] ?? '' })
    photos.value = record.photos || []
  } catch { ElMessage.error('加载记录失败') }
})

async function handleSubmit() {
  await formRef.value.validate()
  saving.value = true
  try {
    const payload = { ...form.value }
    Object.keys(payload).forEach(k => { if (payload[k] === '') payload[k] = null })
    payload.inspect_date = form.value.inspect_date
    payload.location = form.value.location
    if (isEdit.value) {
      await updateAccessInspection(recordId.value, payload)
      ElMessage.success('保存成功')
      router.push(`/access-inspections/${recordId.value}`)
    } else {
      const created = await createAccessInspection(payload)
      ElMessage.success('创建成功，可在详情页上传现场照片')
      router.push(`/access-inspections/${created.id}`)
    }
  } finally { saving.value = false }
}

async function handlePhotoUpload(file) {
  uploading.value = true
  try {
    const photo = await uploadAccessInspectionPhoto(recordId.value, file.raw || file)
    photos.value.push(photo)
    ElMessage.success(`图${photo.photo_index} 上传成功`)
  } finally { uploading.value = false }
}

async function handlePhotoDelete(photo) {
  await ElMessageBox.confirm(`确认删除图${photo.photo_index}？`, '确认', { type: 'warning' })
  await deleteAccessInspectionPhoto(recordId.value, photo.id)
  photos.value = photos.value.filter(p => p.id !== photo.id)
  ElMessage.success('已删除')
}

const exporting = ref(false)
async function handleExport() {
  exporting.value = true
  try {
    const token = localStorage.getItem('repair_token')
    const resp = await fetch(`/api/v1/access-inspections/${recordId.value}/export`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `门禁日常巡检表_${route.params.id}.docx`
    document.body.appendChild(a); a.click(); a.remove()
    URL.revokeObjectURL(url)
    ElMessage.success('Word 已导出')
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally { exporting.value = false }
}
</script>

<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px;">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <span style="font-size:16px; font-weight:600;">{{ pageTitle }}</span>
          <div style="display:flex; gap:8px;">
            <el-button v-if="isEdit" type="success" :loading="exporting" @click="handleExport">导出 Word</el-button>
            <el-button @click="router.back()">返回</el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="巡检日期" prop="inspect_date">
              <el-date-picker v-model="form.inspect_date" type="date" value-format="YYYY-MM-DD"
                placeholder="请选择" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="门禁地点" prop="location">
              <el-select v-model="form.location" placeholder="请选择门禁地点" filterable style="width:100%">
                <el-option v-for="loc in locationOptions" :key="loc.id" :label="loc.name" :value="loc.name" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="巡检人员">
              <el-input v-model="form.inspector" placeholder="请填写巡检人员姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">巡检情况</el-divider>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="道闸情况">
              <el-input v-model="form.gate_status" placeholder="如：正常 / 道闸故障" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="翼闸情况">
              <el-input v-model="form.flap_status" placeholder="如：正常 / 翼闸卡阻" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="门禁系统情况">
              <el-input v-model="form.system_status" placeholder="如：正常 / 刷卡异常" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="其他设备">
              <el-input v-model="form.other_device" placeholder="如：正常 / 无" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">故障与处理</el-divider>
        <el-form-item label="故障描述">
          <el-input v-model="form.fault_description" type="textarea" :rows="3" placeholder="描述发现的故障现象…" />
        </el-form-item>
        <el-form-item label="维修内容">
          <el-input v-model="form.repair_content" type="textarea" :rows="3" placeholder="描述采取的维修措施…" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="isEdit" shadow="never">
      <template #header>
        <span style="font-size:15px; font-weight:600;">现场照片
          <el-tag size="small" style="margin-left:8px;">{{ photos.length }} 张</el-tag>
        </span>
      </template>
      <el-upload :show-file-list="false" accept="image/*"
        :http-request="(opt) => handlePhotoUpload(opt.file)" :disabled="uploading" drag style="margin-bottom:16px;">
        <el-icon :size="48" style="color:#c0c4cc;"><Upload /></el-icon>
        <div style="font-size:14px; color:#606266; margin-top:8px;">
          拖拽图片到此处，或 <em>点击上传</em>（支持 jpg / png / webp）
        </div>
      </el-upload>
      <div v-if="photos.length" style="display:flex; flex-wrap:wrap; gap:12px;">
        <div v-for="photo in photos" :key="photo.id"
          style="position:relative; border:1px solid #e4e7ed; border-radius:6px; overflow:hidden; width:160px;">
          <img :src="'/uploads/' + (photo.thumb_filename || photo.filename)"
            style="width:160px; height:120px; object-fit:cover; display:block;" loading="lazy" />
          <div style="padding:4px 8px; background:#fafafa; font-size:12px; color:#606266;">
            图{{ photo.photo_index }} {{ photo.original_name || '' }}
          </div>
          <el-button link type="danger" size="small"
            style="position:absolute; top:4px; right:4px; background:rgba(255,255,255,0.85); border-radius:4px;"
            @click="handlePhotoDelete(photo)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      <el-empty v-else description="暂无照片，请上传现场图片" :image-size="80" />
    </el-card>
  </div>
</template>
