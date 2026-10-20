import request from './request'

export const login = (data) => request.post('/api/v1/auth/login', data)

export const register = (data) => request.post('/api/v1/auth/register', data)

export const getMe = () => request.get('/api/v1/auth/me')
