import http from './http'

export const authApi = {
  login: (data: { username: string; password: string }) => http.post('/api/auth/login', data),
  register: (data: { username: string; password: string; phone?: string }) => http.post('/api/auth/register', data),
  me: () => http.get('/api/auth/me'),
}
