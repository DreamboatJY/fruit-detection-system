import axios from 'axios'
import { ElMessage } from 'element-plus'
import { clearSession } from './session'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const status = error.response?.status
    const message = error.response?.data?.detail || error.response?.data?.message || '服务器错误'
    if (status === 401) {
      clearSession()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
    ElMessage.error('请求失败：' + message)
    return Promise.reject(error)
  }
)

export default service
