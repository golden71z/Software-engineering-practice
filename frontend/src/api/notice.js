import request from './request'

export const listNotices = (limit) =>
  request.get('/api/v1/notices', { params: limit ? { limit } : {} })

export const createNotice = (data) => request.post('/api/v1/notices', data)

export const removeNotice = (id) => request.delete(`/api/v1/notices/${id}`)
