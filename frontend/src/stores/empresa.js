import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEmpresaStore = defineStore('empresa', () => {
  const cachedUser = JSON.parse(localStorage.getItem('user') || 'null')
  const cachedEmpresa = JSON.parse(localStorage.getItem('active_empresa') || 'null')
  const activeEmpresa = ref(cachedEmpresa || (cachedUser?.empresa_ativa_id ? {
    id: cachedUser.empresa_ativa_id,
    nome_fantasia: cachedUser.empresa_ativa_nome,
  } : null))

  function setActiveEmpresa(empresa) {
    activeEmpresa.value = empresa
    if (empresa) {
      localStorage.setItem('active_empresa', JSON.stringify(empresa))
    } else {
      localStorage.removeItem('active_empresa')
    }
  }

  async function syncActiveEmpresa(force = false) {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    const empresaId = authStore.user?.empresa_ativa_id

    if (!empresaId) {
      setActiveEmpresa(null)
      return null
    }

    if (!force && activeEmpresa.value?.id === empresaId) {
      return activeEmpresa.value
    }

    const EmpresaService = (await import('@/services/empresas.service')).default
    const empresaData = await EmpresaService.getEmpresa(empresaId)
    setActiveEmpresa(empresaData)
    return empresaData
  }

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
      }
      await authStore.fetchProfile()
      await syncActiveEmpresa(true)
      return response
    } catch (error) {
      console.error('Failed to select company:', error)
      throw error
    }
  }

  async function clearActiveEmpresa() {
    const EmpresaService = (await import('@/services/empresas.service')).default
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()

    await EmpresaService.clearEmpresaSelection()
    await authStore.fetchProfile()
    await syncActiveEmpresa(true)
  }

  return { activeEmpresa, selectEmpresa, clearActiveEmpresa, syncActiveEmpresa }
})
