import http from './http'

export const login  = (data) => http.post('/auth/login', data)
export const getMe  = ()     => http.get('/auth/me')
export const getUsers    = ()           => http.get('/auth/users')
export const createUser  = (data)       => http.post('/auth/users', data)
export const changePassword = (uid, pw) => http.put(`/auth/users/${uid}/password`, { password: pw })
