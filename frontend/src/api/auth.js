import request from './request'

export const login = (data) => request.post('/api/v1/auth/login', data)

export const register = (data) => request.post('/api/v1/auth/register', data)

export const getMe = () => request.get('/api/v1/auth/me')

export const updateMe = (data) => request.put('/api/v1/auth/me', data)

export const changePassword = (data) => request.post('/api/v1/auth/change-password', data)
