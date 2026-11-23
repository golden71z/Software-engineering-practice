import request from './request'

export const getDashboard = () => request.get('/api/v1/admin/dashboard')

/** params: { keyword, role, page, size } */
export const listUsers = (params) => request.get('/api/v1/admin/users', { params })

export const setUserStatus = (id, status) =>
  request.post(`/api/v1/admin/users/${id}/status`, { status })

export const resetUserPassword = (id) =>
  request.post(`/api/v1/admin/users/${id}/reset-password`)

/** params: { type, category_id, keyword, status, page, size } */
export const listAllItems = (params) => request.get('/api/v1/admin/items', { params })
