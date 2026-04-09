import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '@/router'
export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')))
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isAuthenticated = ref(!!accessToken.value)

  async function login(credentials) {
    const AuthService = (await import('@/services/auth.service')).default
    try {
      const response = await AuthService.login(credentials.email, credentials.password)
      accessToken.value = response.access
      refreshToken.value = response.refresh
      user.value = response.user
      isAuthenticated.value = true

      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('refresh_token', refreshToken.value)
      localStorage.setItem('user', JSON.stringify(user.value))

      const { useEmpresaStore } = await import('@/stores/empresa')
      const empresaStore = useEmpresaStore()
      await empresaStore.syncActiveEmpresa(true)

      router.push('/') // Redireciona para o dashboard após login
    } catch (error) {
      console.error('Login failed:', error)
      throw error // Lança o erro para ser tratado no componente
    }
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    isAuthenticated.value = false

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('active_empresa')

    router.push('/login') // Redireciona para a página de login
  }

  async function refreshAccessToken() {
    const AuthService = (await import('@/services/auth.service')).default
    try {
      const response = await AuthService.refreshToken(refreshToken.value)
      accessToken.value = response.access
      localStorage.setItem('access_token', accessToken.value)
      return accessToken.value
    } catch (error) {
      console.error('Failed to refresh token:', error)
      logout() // Força logout se o refresh token for inválido/expirado
      throw error
    }
  }

  if (isAuthenticated.value) {
    fetchProfile()
  }

  async function fetchProfile() {
    const AuthService = (await import('@/services/auth.service')).default
    try {
      const userData = await AuthService.getProfile()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(user.value))

      const { useEmpresaStore } = await import('@/stores/empresa')
      const empresaStore = useEmpresaStore()
      await empresaStore.syncActiveEmpresa(true)
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      if (error.response && error.response.status === 401) {
        logout()
      }
    }
  }

  return { user, accessToken, refreshToken, isAuthenticated, login, logout, refreshAccessToken, fetchProfile }
})
