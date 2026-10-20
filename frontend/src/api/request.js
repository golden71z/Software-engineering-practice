import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/stores/user'

/**
 * 全局 axios 实例。
 *
 * 后端约定：HTTP 一律 200，业务结果放在响应体的 code 里。
 * 所以判断失败不能靠 catch(HTTP error)，必须在这里判断 code 并主动 reject，
 * 否则页面里的 .then() 会把"用户名已被占用"当成成功处理。
 */
const service = axios.create({
  baseURL: '',
  timeout: 15000,
})

service.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

service.interceptors.response.use(
  (response) => {
    // 文件下载没走统一响应体，直接返回原始 response
    if (response.config.responseType === 'blob') {
      return response
    }

    const body = response.data
    if (body.code === 20000) {
      // 页面拿到的就是裸数据，不用层层 .data.data
      return body.data
    }

    if (body.code === 40100) {
      const store = useUserStore()
      store.clear()
      const current = router.currentRoute.value
      if (current.path !== '/login') {
        router.replace({ path: '/login', query: { redirect: current.fullPath } })
      }
    }

    ElMessage.error(body.message || '请求失败')
    const err = new Error(body.message || '请求失败')
    err.code = body.code
    err.data = body.data // 校验失败时是字段明细数组，页面可自行处理
    return Promise.reject(err)
  },
  (error) => {
    // 只有网络断开、超时、真正的 500 才会走到这里
    const status = error.response?.status
    let message = '网络异常，请稍后重试'
    if (status === 500) message = '服务器开小差了，请稍后重试'
    else if (error.code === 'ECONNABORTED') message = '请求超时，请检查网络'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
