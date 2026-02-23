import api from './api'

class ContabilService {
  // Lançamentos Contábeis
  async getLancamentos(params = {}) {
    const response = await api.get('/contabil/lancamentos/', { params })
    return response.data
  }

  async getLancamento(id) {
    const response = await api.get(`/contabil/lancamentos/${id}/`)
    return response.data
  }

  async createLancamento(data) {
    const response = await api.post('/contabil/lancamentos/', data)
    return response.data
  }

  async updateLancamento(id, data) {
    const response = await api.patch(`/contabil/lancamentos/${id}/`, data)
    return response.data
  }

  async deleteLancamento(id) {
    const response = await api.delete(`/contabil/lancamentos/${id}/`)
    return response.data
  }

  // Partidas de Lançamento (Nested under LancamentoContabil)
  async getPartidasLancamento(lancamentoId, params = {}) {
    const response = await api.get(`/contabil/lancamentos/${lancamentoId}/partidas/`, { params })
    return response.data
  }

  // Relatórios
  async getDRE(data_inicio, data_fim) {
    const response = await api.get('/contabil/dre/', { params: { data_inicio, data_fim } })
    return response.data
  }

  async getBalancoPatrimonial(data_base) {
    const response = await api.get('/contabil/balanco-patrimonial/', { params: { data_base } })
    return response.data
  }
}

export default new ContabilService()
