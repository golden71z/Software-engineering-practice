import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * axios 实例
 * 统一处理：请求前缀、认证头注入、响应体解包、错误提示
 */
const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// ===== 请求拦截器 =====
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ===== 响应拦截器 =====
request.interceptors.response.use(
  (response) => {
    const res = response.data

    // 后端统一响应体：{ code, message, data, timestamp }
    if (res.code === 20000) {
      return res
    }

    // 认证失败，清理登录态
    if (res.code === 40100 || res.code === 40101 || res.code === 40102) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      ElMessage.error(res.message || '登录已过期，请重新登录')
      return Promise.reject(new Error(res.message))
    }

    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络异常'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
