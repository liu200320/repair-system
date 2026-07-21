import http from './http'

export const listNetworkInspections = (params) =>
  http.get('/network-inspections', { params })

export const createNetworkInspection = (data) =>
  http.post('/network-inspections', data)

export const getNetworkInspection = (id) =>
  http.get(`/network-inspections/${id}`)

export const updateNetworkInspection = (id, data) =>
  http.put(`/network-inspections/${id}`, data)

export const deleteNetworkInspection = (id) =>
  http.delete(`/network-inspections/${id}`)

export const uploadNetworkInspectionPhoto = (recordId, file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post(`/network-inspections/${recordId}/photos`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const deleteNetworkInspectionPhoto = (recordId, photoId) =>
  http.delete(`/network-inspections/${recordId}/photos/${photoId}`)

export const exportNetworkInspection = (recordId) =>
  http.post(`/network-inspections/${recordId}/export`, {}, { responseType: 'blob' })

export const getNetworkLocations = () =>
  http.get('/network-inspections-locations')

export const exportNetworkInspectionRange = async (startDate, endDate) => {
  const token = localStorage.getItem('repair_token')
  const res = await fetch(
    `/api/v1/network-inspections/export/range?start_date=${startDate}&end_date=${endDate}`,
    { method: 'GET', headers: token ? { Authorization: `Bearer ${token}` } : {} }
  )
  if (res.status === 401) throw new Error('登录已过期，请重新登录')
  if (res.status === 404) throw new Error('该时间段内没有巡检记录')
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || '导出失败')
  }
  const blob = await res.blob()
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `网络巡检汇总_${startDate}_至_${endDate}.docx`
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
