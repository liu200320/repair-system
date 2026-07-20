import http from './http'

/** 获取维修记录列表 */
export const getRepairs = (params) => http.get('/repairs', { params })

/** 获取单条维修记录 */
export const getRepair = (id) => http.get(`/repairs/${id}`)

/** 新建维修记录 */
export const createRepair = (data) => http.post('/repairs', data)

/** 更新维修记录 */
export const updateRepair = (id, data) => http.put(`/repairs/${id}`, data)

/** 删除维修记录 */
export const deleteRepair = (id) => http.delete(`/repairs/${id}`)

/**
 * 上传维修照片
 * @param {number} repairId - 维修记录 ID
 * @param {string} phase    - 'before' | 'during' | 'after'
 * @param {File}   file     - 图片文件
 * @param {Function} onProgress - 上传进度回调
 */
export const uploadPhoto = (repairId, phase, file, onProgress) => {
  const form = new FormData()
  form.append('phase', phase)
  form.append('file', file)
  return http.post(`/repairs/${repairId}/photos`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
}

/** 删除照片 */
export const deletePhoto = (repairId, photoId) =>
  http.delete(`/repairs/${repairId}/photos/${photoId}`)

/** 导出单条维修记录 Word */
export const exportWord = async (repairId, recordNo) => {
  const token = localStorage.getItem('repair_token')
  const res = await fetch(`/api/v1/repairs/${repairId}/export`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (res.status === 401) throw new Error('登录已过期，请重新登录')
  if (!res.ok) throw new Error('导出失败')
  const blob = await res.blob()
  _downloadBlob(blob, `维修记录_${recordNo}.docx`)
}

/**
 * 按日期范围批量导出 Word
 * @param {string} startDate - 'YYYY-MM-DD'
 * @param {string} endDate   - 'YYYY-MM-DD'
 */
export const exportWordRange = async (startDate, endDate) => {
  const token = localStorage.getItem('repair_token')
  const res = await fetch(
    `/api/v1/repairs/export/range?start_date=${startDate}&end_date=${endDate}`,
    {
      method: 'GET',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  )
  if (res.status === 401) throw new Error('登录已过期，请重新登录')
  if (res.status === 404) throw new Error('该时间段内没有维修记录')
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || '导出失败')
  }
  const blob = await res.blob()
  _downloadBlob(blob, `维修汇总_${startDate}_至_${endDate}.docx`)
}

function _downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
