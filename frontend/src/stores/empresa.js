import { defineStore } from 'pinia'
import { ref } from 'vue'
export const useEmpresaStore = defineStore('empresa', () => {
  const activeEmpresa = ref(JSON.parse(localStorage.getItem('active_empresa')))

  async function selectEmpresa(empresaId) {
    const EmpresaService = (await import('@/services/empresas.service')).default
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()

    try {
      const response = await EmpresaService.selectEmpresa(empresaId)
      const user = JSON.parse(localStorage.getItem('user'))
      if (user) {
        user.empresa_ativa_id = response.empresa_id
        localStorage.setItem('user', JSON.stringify(user))
        if (authStore.user) {
          authStore.user.empresa_ativa_id = response.empresa_id
        }
        // Sincroniza o perfil completo (incluindo permissões do token novo no backend)
        await authStore.fetchProfile()
      }
      const empresaData = await EmpresaService.getEmpresa(empresaId) // Buscar dados completos da empresa
      activeEmpresa.value = empresaData
      localStorage.setItem('active_empresa', JSON.stringify(activeEmpresa.value))
      return response
    } catch (error) {
      console.error('Failed to select company:', error)
      throw error
    }
  }

  function clearActiveEmpresa() {
    activeEmpresa.value = null
    localStorage.removeItem('active_empresa')
    const user = JSON.parse(localStorage.getItem('user'))
    if (user) {
      user.empresa_ativa_id = null
      user.empresa_ativa_nome = null
      localStorage.setItem('user', JSON.stringify(user))
    }
  }

  return { activeEmpresa, selectEmpresa, clearActiveEmpresa }
})
