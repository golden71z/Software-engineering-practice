import request from './request'

export const listCategories = (onlyActive = true) =>
  request.get('/api/v1/categories', { params: { only_active: onlyActive } })

export const createCategory = (data) => request.post('/api/v1/categories', data)

export const updateCategory = (id, data) => request.put(`/api/v1/categories/${id}`, data)

export const removeCategory = (id) => request.delete(`/api/v1/categories/${id}`)
