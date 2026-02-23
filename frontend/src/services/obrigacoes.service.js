import api from './api'

class ObrigacoesService {
  async getObrigacoes(params = {}) {
    const response = await api.get('/obrigacoes/obrigacoes/', { params })
    return response.data
  }

  async getObrigacao(id) {
    const response = await api.get(`/obrigacoes/obrigacoes/${id}/`)
    return response.data
  }

  async createObrigacao(data) {
    const response = await api.post('/obrigacoes/obrigacoes/', data)
    return response.data
  }

  async updateObrigacao(id, data) {
    const response = await api.patch(`/obrigacoes/obrigacoes/${id}/`, data)
    return response.data
  }

  async deleteObrigacao(id) {
    const response = await api.delete(`/obrigacoes/obrigacoes/${id}/`)
    return response.data
  }

  async getObrigacoesVencendoHoje() {
    const response = await api.get('/obrigacoes/obrigacoes/vencendo_hoje/')
    return response.data
  }

  async getObrigacoesVencendoProximosDias(dias) {
    const response = await api.get('/obrigacoes/obrigacoes/vencendo_proximos_dias/', { params: { dias } })
    return response.data
  }
}

export default new ObrigacoesService()
