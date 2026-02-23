import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api', // Usa VITE_API_URL se definida, senão /api
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }

    // Adiciona o cabeçalho X-Empresa-Id se houver uma empresa ativa selecionada
    if (authStore.user && authStore.user.empresa_ativa_id) {
      config.headers['X-Empresa-Id'] = authStore.user.empresa_ativa_id;
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()

    // Se for um erro 401 (Unauthorized) e não for uma tentativa de refresh token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true // Marca a requisição original para evitar loops

      if (authStore.refreshToken) {
        try {
          await authStore.refreshAccessToken() // Tenta renovar o token
          // Se o refresh for bem-sucedido, reenvia a requisição original
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`
          return api(originalRequest)
        } catch (refreshError) {
          // Se o refresh falhar, o refreshAccessToken já terá chamado logout()
          return Promise.reject(refreshError)
        }
      } else {
        // Se não houver refresh token, ou se o refresh falhar, redireciona para o login
        authStore.logout()
        router.push('/login')
      }
    }

    // Se for um erro 403 (Forbidden), as permissões podem ter mudado
    if (error.response && error.response.status === 403) {
      console.warn('Access denied (403). Refreshing profile permissions...');
      authStore.fetchProfile();
    }

    return Promise.reject(error)
  }
)

export default api
