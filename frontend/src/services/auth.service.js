import api from './api'

class AuthService {
  async login(email, password) {
    const response = await api.post('/auth/login/', { email, password })
    return response.data
  }

  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh/', { refresh: refreshToken })
    return response.data
  }

  async getProfile() {
    const response = await api.get('/core/perfil/')
    return response.data
  }

  // Você pode adicionar outros métodos como register, forgot password, etc.
}

export default new AuthService()
