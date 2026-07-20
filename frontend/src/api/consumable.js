import http from './http'

// ── 记录 CRUD ────────────────────────────────────────────────────
export const listConsumables = (params) =>
  http.get('/consumables', { params })

export const createConsumable = (data) =>
  http.post('/consumables', data)

export const getConsumable = (id) =>
  http.get(`/consumables/${id}`)

export const updateConsumable = (id, data) =>
  http.put(`/consumables/${id}`, data)

export const deleteConsumable = (id) =>
  http.delete(`/consumables/${id}`)

// ── 照片 ──────────────────────────────────────────────────────────
export const uploadConsumablePhoto = (recordId, file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return http.post(`/consumables/${recordId}/photos`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}

export const deleteConsumablePhoto = (recordId, photoId) =>
  http.delete(`/consumables/${recordId}/photos/${photoId}`)

// ── 导出 ──────────────────────────────────────────────────────────
export const exportConsumable = (recordId) =>
  http.post(`/consumables/${recordId}/export`, {}, { responseType: 'blob' })
