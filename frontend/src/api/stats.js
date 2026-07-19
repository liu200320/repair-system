import http from './http'

export const getLocations  = (keyword) => http.get('/locations', { params: keyword ? { keyword } : {} })
export const createLocation = (data)  => http.post('/locations', data)
export const updateLocation = (id, data) => http.put(`/locations/${id}`, data)
export const deleteLocation = (id)   => http.delete(`/locations/${id}`)

export const getStatsSummary   = () => http.get('/stats/summary')
export const getStatsTrend     = () => http.get('/stats/trend')
export const getStatsLocations = () => http.get('/stats/locations')
