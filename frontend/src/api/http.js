import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器：自动附加 Bearer Token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('repair_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：统一错误处理 + 401 跳转登录
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('repair_token')
      localStorage.removeItem('repair_user')
      window.location.href = '/login'
      return Promise.reject(err)
    }
    const msg = err.response?.data?.detail || err.message || '请求失败'
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    return Promise.reject(err)
  }
)

export default http
