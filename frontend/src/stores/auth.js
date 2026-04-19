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

      // CLIENTE vai direto para o portal, sem passar pelo sistema interno
      if (response.user?.perfil_empresa === 'CLIENTE') {
        try {
          const IntakeService = (await import('@/services/intake.service')).default
          const data = await IntakeService.listClientePortais()
          const portais = data.results || data || []
          const slug = portais[0]?.slug
          if (slug) {
            router.push(`/area_cliente/${slug}`)
          } else {
            router.push('/area_cliente/portal')
          }
        } catch {
          router.push('/area_cliente/portal')
        }
      } else {
        router.push('/')
      }
    } catch (error) {
      console.error('Login failed:', error)
      throw error // Lança o erro para ser tratado no componente
    }
  }

  function logout() {
    const currentUser = user.value
    const perfil = currentUser?.perfil_empresa
    const portalSlug = currentUser?.portal_cliente_slug

    user.value = null
    accessToken.value = null
    refreshToken.value = null
    isAuthenticated.value = false

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('active_empresa')

    if (perfil === 'CLIENTE' && portalSlug) {
      router.push(`/portal/${portalSlug}/login`)
    } else {
      router.push('/login')
    }
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
