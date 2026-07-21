import http from './http'

export const listAccessInspections = (params) =>
  http.get('/access-inspections', { params })

export const createAccessInspection = (data) =>
  http.post('/access-inspections', data)

export const getAccessInspection = (id) =>
  http.get(`/access-inspections/${id}`)

export const updateAccessInspection = (id, data) =>
  http.put(`/access-inspections/${id}`, data)

export const deleteAccessInspection = (id) =>
  http.delete(`/access-inspections/${id}`)

export const uploadAccessInspectionPhoto = (recordId, file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post(`/access-inspections/${recordId}/photos`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const deleteAccessInspectionPhoto = (recordId, photoId) =>
  http.delete(`/access-inspections/${recordId}/photos/${photoId}`)

export const getAccessLocations = () =>
  http.get('/access-inspections-locations')

export const exportAccessInspectionRange = async (startDate, endDate) => {
  const token = localStorage.getItem('repair_token')
  const res = await fetch(
    `/api/v1/access-inspections/export/range?start_date=${startDate}&end_date=${endDate}`,
    { method: 'GET', headers: token ? { Authorization: `Bearer ${token}` } : {} }
  )
  if (res.status === 401) throw new Error('登录已过期，请重新登录')
  if (res.status === 404) throw new Error('该时间段内没有门禁巡检记录')
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || '导出失败')
  }
  const blob = await res.blob()
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `门禁巡检汇总_${startDate}_至_${endDate}.docx`
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
