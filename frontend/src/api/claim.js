import request from './request'

export const applyClaim = (data) => request.post('/api/v1/claims', data)

export const listMyClaims = () => request.get('/api/v1/claims/mine')

export const listReceivedClaims = (status) =>
  request.get('/api/v1/claims/received', { params: status ? { status } : {} })

export const getPendingCount = () => request.get('/api/v1/claims/pending-count')

export const approveClaim = (id, comment) =>
  request.post(`/api/v1/claims/${id}/approve`, { comment })

export const rejectClaim = (id, comment) =>
  request.post(`/api/v1/claims/${id}/reject`, { comment })

export const cancelClaim = (id) => request.post(`/api/v1/claims/${id}/cancel`)
