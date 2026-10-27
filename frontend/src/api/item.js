import request from './request'

/** 公开列表。params: { type, category_id, keyword, page, size } */
export const listItems = (params) => request.get('/api/v1/items', { params })

/** 我发布的。params: { status, page, size } */
export const listMyItems = (params) => request.get('/api/v1/items/mine', { params })

export const getItem = (id) => request.get(`/api/v1/items/${id}`)

export const createItem = (data) => request.post('/api/v1/items', data)

export const updateItem = (id, data) => request.put(`/api/v1/items/${id}`, data)

export const offlineItem = (id) => request.post(`/api/v1/items/${id}/offline`)

export const restoreItem = (id) => request.post(`/api/v1/items/${id}/restore`)
