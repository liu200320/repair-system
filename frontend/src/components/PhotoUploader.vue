<script setup>
import { ref } from 'vue'
import { uploadPhoto, deletePhoto } from '../api/repair'
import { ElMessage, ElMessageBox } from 'element-plus'
import imageCompression from 'browser-image-compression'

const props = defineProps({
  repairId: { type: Number, required: true },
  phase: { type: String, required: true },          // 'before' | 'during' | 'after'
  photos: { type: Array, default: () => [] },
})

const emit = defineEmits(['uploaded', 'deleted'])

const uploading = ref(false)
const uploadProgress = ref(0)
const previewVisible = ref(false)
const previewUrl = ref('')

// 压缩选项（手机图片通常很大）
const compressOptions = {
  maxSizeMB: 2,
  maxWidthOrHeight: 1920,
  useWebWorker: true,
}

async function handleFileChange(event) {
  const files = Array.from(event.target.files)
  if (!files.length) return

  uploading.value = true
  uploadProgress.value = 0

  try {
    for (let i = 0; i < files.length; i++) {
      const file = files[i]

      // 压缩图片（移动端拍摄照片通常 3-10MB，压缩后体验更好）
      let compressedFile
      try {
        const blob = await imageCompression(file, compressOptions)
        // 压缩后用原始文件名重新封装，防止 browser-image-compression 丢失扩展名
        compressedFile = new File([blob], file.name, { type: file.type })
      } catch {
        compressedFile = file // 压缩失败则使用原文件
      }

      await uploadPhoto(
        props.repairId,
        props.phase,
        compressedFile,
        (progress) => {
          uploadProgress.value = Math.round(((i + progress / 100) / files.length) * 100)
        }
      )
    }
    ElMessage.success(`上传成功 ${files.length} 张`)
    emit('uploaded')
  } catch (err) {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    // 重置 input，允许再次选同一张图
    event.target.value = ''
  }
}

async function handleDelete(photo) {
  await ElMessageBox.confirm('确认删除该照片？', '提示', { type: 'warning' })
  await deletePhoto(props.repairId, photo.id)
  ElMessage.success('已删除')
  emit('deleted')
}

function openPreview(photo) {
  previewUrl.value = `/uploads/${photo.filename}`
  previewVisible.value = true
}
</script>

<template>
  <div>
    <!-- 已上传照片展示 -->
    <div class="photo-grid" v-if="photos.length">
      <div class="photo-item" v-for="photo in photos" :key="photo.id">
        <img
          :src="`/uploads/${photo.filename}`"
          :alt="photo.original_name"
          class="photo-thumb"
          @click="openPreview(photo)"
        />
        <div class="photo-actions">
          <el-button size="small" type="danger" circle @click.stop="handleDelete(photo)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <div class="photo-name">{{ photo.original_name }}</div>
      </div>
    </div>

    <el-empty v-else description="暂无照片" :image-size="80" />

    <!-- 上传按钮（兼容手机相机和相册） -->
    <div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
      <!-- 调用相机直接拍照 -->
      <label class="upload-btn camera-btn">
        <el-icon><Camera /></el-icon>
        拍照上传
        <input
          type="file"
          accept="image/*"
          capture="camera"
          multiple
          style="display:none"
          @change="handleFileChange"
        />
      </label>

      <!-- 从相册选择 -->
      <label class="upload-btn album-btn">
        <el-icon><Picture /></el-icon>
        从相册选择
        <input
          type="file"
          accept="image/*"
          multiple
          style="display:none"
          @change="handleFileChange"
        />
      </label>
    </div>

    <!-- 上传进度 -->
    <el-progress
      v-if="uploading"
      :percentage="uploadProgress"
      style="margin-top: 8px;"
    />

    <!-- 图片预览 -->
    <el-dialog v-model="previewVisible" width="90%" :title="'图片预览'" center>
      <img :src="previewUrl" style="width:100%; max-height:80vh; object-fit:contain;" />
    </el-dialog>
  </div>
</template>

<style scoped>
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}
.photo-item {
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  background: #fafafa;
}
.photo-thumb {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
  cursor: pointer;
  transition: opacity 0.2s;
}
.photo-thumb:hover { opacity: 0.85; }
.photo-actions {
  position: absolute;
  top: 4px;
  right: 4px;
}
.photo-name {
  padding: 4px 6px;
  font-size: 11px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  border: 1px solid;
  user-select: none;
  transition: opacity 0.2s;
}
.upload-btn:hover { opacity: 0.8; }
.camera-btn { background: #ecf5ff; color: #409eff; border-color: #b3d8ff; }
.album-btn  { background: #f0f9eb; color: #67c23a; border-color: #c2e7b0; }
</style>
