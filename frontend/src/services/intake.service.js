import api from './api'

class IntakeService {
  async getPortalClientes(params = {}) {
    const response = await api.get('/intake/portal/', { params })
    return response.data
  }

  async createPortalCliente(payload) {
    const response = await api.post('/intake/portal/', payload)
    return response.data
  }

  async updatePortalCliente(id, payload) {
    const response = await api.patch(`/intake/portal/${id}/`, payload)
    return response.data
  }

  async getRecebimentos(params = {}) {
    const response = await api.get('/intake/recebimentos/', { params })
    return response.data
  }

  async createRecebimento(formData) {
    const response = await api.post('/intake/recebimentos/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getPendencias(params = {}) {
    const response = await api.get('/intake/pendencias/', { params })
    return response.data
  }

  async getChecklists(params = {}) {
    const response = await api.get('/intake/checklists/', { params })
    return response.data
  }

  async getLotes(params = {}) {
    const response = await api.get('/intake/lotes/', { params })
    return response.data
  }

  async confirmarRecebimento(payload) {
    const response = await api.post('/intake/confirmar/', payload)
    return response.data
  }

  async exportarQuestor(payload) {
    const response = await api.post('/intake/exportar/questor/', payload)
    return response.data
  }

  // === Cliente Portal (área do cliente) ===
  // Usa endpoints dedicados /intake/cliente/* com permissão IsIntakeClientCompany

  // Lista portais disponíveis para o cliente logado (empresa ativa).
  async listClientePortais() {
    const response = await api.get('/intake/cliente/portal/')
    return response.data
  }

  async getClientPortalConfig(slug) {
    const response = await api.get(`/intake/cliente/portal/${slug}/`)
    return response.data
  }

  // Lista documentos enviados pelo cliente logado (backend filtra por empresa e usuário).
  async listMyDocuments(params = {}) {
    const response = await api.get('/intake/cliente/recebimentos/', { params })
    return response.data
  }

  // Upload de documento pelo cliente. Aceita FormData pronto.
  async uploadDocument(formData) {
    const response = await api.post('/intake/cliente/recebimentos/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }
}

export default new IntakeService()
