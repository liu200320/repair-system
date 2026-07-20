<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Upload, Picture } from '@element-plus/icons-vue'
import {
  createConsumable, getConsumable, updateConsumable,
  uploadConsumablePhoto, deleteConsumablePhoto,
} from '../api/consumable'

const router = useRouter()
const route  = useRoute()

const isEdit   = computed(() => !!route.params.id)
const recordId = computed(() => isEdit.value ? Number(route.params.id) : null)
const pageTitle= computed(() => isEdit.value ? '编辑耗材记录' : '新建耗材记录')

// ── 表单数据 ──────────────────────────────────────────────────────
const formRef = ref()
const saving  = ref(false)
const form = ref({
  location: '',
  use_date: '',
  notes:    '',
  items: [{ sort_order: 0, name: '', unit: '', quantity: '', signer: '' }],
})
const rules = {
  location: [{ required: true, message: '请填写使用地点', trigger: 'blur' }],
  use_date: [{ required: true, message: '请选择使用日期', trigger: 'change' }],
}

// ── 照片数据（仅编辑模式下使用） ─────────────────────────────────
const photos       = ref([])
const uploading    = ref(false)
const uploadingIdx = ref(-1)

// ── 明细行操作 ────────────────────────────────────────────────────
function addItem() {
  form.value.items.push({ sort_order: form.value.items.length, name: '', unit: '', quantity: '', signer: '' })
}

function removeItem(idx) {
  if (form.value.items.length <= 1) {
    ElMessage.warning('至少保留一行耗材明细')
    return
  }
  form.value.items.splice(idx, 1)
  // 重新编号
  form.value.items.forEach((item, i) => { item.sort_order = i })
}

// ── 加载已有记录（编辑模式） ──────────────────────────────────────
onMounted(async () => {
  if (!isEdit.value) return
  try {
    const record = await getConsumable(recordId.value)
    form.value.location = record.location
    form.value.use_date = record.use_date
    form.value.notes    = record.notes || ''
    form.value.items    = record.items.length
      ? record.items.map(it => ({
          sort_order: it.sort_order,
          name:       it.name,
          unit:       it.unit || '',
          quantity:   it.quantity || '',
          signer:     it.signer || '',
        }))
      : [{ sort_order: 0, name: '', unit: '', quantity: '', signer: '' }]
    photos.value = record.photos || []
  } catch {
    ElMessage.error('加载记录失败')
  }
})

// ── 保存表单 ──────────────────────────────────────────────────────
async function handleSubmit() {
  await formRef.value.validate()
  // 过滤空行
  const validItems = form.value.items.filter(it => it.name.trim())
  if (!validItems.length) {
    ElMessage.warning('请至少填写一行耗材名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      location: form.value.location,
      use_date: form.value.use_date,
      notes:    form.value.notes || null,
      items:    validItems,
    }
    if (isEdit.value) {
      await updateConsumable(recordId.value, payload)
      ElMessage.success('保存成功')
      router.push(`/consumables/${recordId.value}`)
    } else {
      const created = await createConsumable(payload)
      ElMessage.success('创建成功，可在详情页上传现场照片')
      router.push(`/consumables/${created.id}`)
    }
  } finally {
    saving.value = false
  }
}

// ── 照片上传（仅编辑/详情模式使用） ──────────────────────────────
async function handlePhotoUpload(file, idx) {
  uploading.value    = true
  uploadingIdx.value = idx
  try {
    const photo = await uploadConsumablePhoto(recordId.value, file.raw || file)
    photos.value.push(photo)
    ElMessage.success(`图${photo.photo_index} 上传成功`)
  } catch {
    // 错误已由 http 拦截器统一提示
  } finally {
    uploading.value    = false
    uploadingIdx.value = -1
  }
}

async function handlePhotoDelete(photo) {
  await ElMessageBox.confirm(`确认删除图${photo.photo_index}？`, '确认', { type: 'warning' })
  await deleteConsumablePhoto(recordId.value, photo.id)
  photos.value = photos.value.filter(p => p.id !== photo.id)
  ElMessage.success('已删除')
}

// ── 导出 Word ─────────────────────────────────────────────────────
const exporting = ref(false)
async function handleExport() {
  exporting.value = true
  try {
    const token = localStorage.getItem('repair_token')
    const resp  = await fetch(`/api/v1/consumables/${recordId.value}/export`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const blob     = await resp.blob()
    const url      = URL.createObjectURL(blob)
    const a        = document.createElement('a')
    a.href         = url
    a.download     = `耗材使用情况表_${route.params.id}.docx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    ElMessage.success('Word 已导出')
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px;">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <span style="font-size:16px; font-weight:600;">{{ pageTitle }}</span>
          <div style="display:flex; gap:8px;">
            <el-button v-if="isEdit" type="success" :loading="exporting" @click="handleExport">
              <el-icon><Download /></el-icon> 导出 Word
            </el-button>
            <el-button @click="router.back()">返回</el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <!-- 基本信息 -->
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="使用地点" prop="location">
              <el-input v-model="form.location" placeholder="如：鸿鹄楼楼顶鹰眼" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用日期" prop="use_date">
              <el-date-picker v-model="form.use_date" type="date" value-format="YYYY-MM-DD"
                placeholder="请选择" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 耗材明细表 -->
        <el-form-item label="耗材明细">
          <div style="width:100%;">
            <el-table :data="form.items" border style="width:100%; margin-bottom:8px;">
              <el-table-column label="耗材名称" min-width="200">
                <template #default="{ row }">
                  <el-input v-model="row.name" placeholder="如：超六类网线" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="单位" width="100">
                <template #default="{ row }">
                  <el-input v-model="row.unit" placeholder="米/个/根" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="数量" width="100">
                <template #default="{ row }">
                  <el-input v-model="row.quantity" placeholder="如：80" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="使用人签字" min-width="180">
                <template #default="{ row }">
                  <el-input v-model="row.signer" placeholder="如：龙京辉，刘璧珲" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="70" align="center">
                <template #default="{ $index }">
                  <el-button link type="danger" size="small" @click="removeItem($index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button size="small" @click="addItem">
              <el-icon><Plus /></el-icon> 添加耗材行
            </el-button>
          </div>
        </el-form-item>

        <!-- 备注 -->
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3"
            placeholder="如：网线、电源线用于从图三拉到图一这段距离…" />
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 照片上传区（仅编辑模式显示） -->
    <el-card v-if="isEdit" shadow="never">
      <template #header>
        <span style="font-size:15px; font-weight:600;">现场照片
          <el-tag size="small" style="margin-left:8px;">{{ photos.length }} 张</el-tag>
        </span>
      </template>

      <el-upload
        :show-file-list="false"
        accept="image/*"
        :http-request="(opt) => handlePhotoUpload(opt.file)"
        :disabled="uploading"
        drag
        style="margin-bottom:16px;"
      >
        <el-icon :size="48" style="color:#c0c4cc;"><Upload /></el-icon>
        <div style="font-size:14px; color:#606266; margin-top:8px;">
          拖拽图片到此处，或 <em>点击上传</em>（支持 jpg / png / webp）
        </div>
      </el-upload>

      <!-- 已上传照片 -->
      <div v-if="photos.length" style="display:flex; flex-wrap:wrap; gap:12px;">
        <div v-for="photo in photos" :key="photo.id"
          style="position:relative; border:1px solid #e4e7ed; border-radius:6px; overflow:hidden; width:160px;">
          <img
            :src="'/uploads/' + (photo.thumb_filename || photo.filename)"
            style="width:160px; height:120px; object-fit:cover; display:block;"
            loading="lazy"
          />
          <div style="padding:4px 8px; background:#fafafa; font-size:12px; color:#606266;">
            图{{ photo.photo_index }} {{ photo.original_name || '' }}
          </div>
          <el-button
            link type="danger" size="small"
            style="position:absolute; top:4px; right:4px; background:rgba(255,255,255,0.85); border-radius:4px;"
            @click="handlePhotoDelete(photo)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      <el-empty v-else description="暂无照片，请上传现场图片" :image-size="80" />
    </el-card>
  </div>
</template>
