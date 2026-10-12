import request from '@/utils/request'

/**
 * 健康检查接口
 * 用于验证前后端链路是否打通
 */
export function checkHealth() {
  return request({
    url: '/health',
    method: 'get'
  })
}
