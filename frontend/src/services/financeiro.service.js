import api from './api'

class FinanceiroService {
  // Contas Bancárias
  async getContasBancarias(params = {}) {
    const response = await api.get('/financeiro/contas-bancarias/', { params })
    return response.data
  }

  async getContaBancaria(id) {
    const response = await api.get(`/financeiro/contas-bancarias/${id}/`)
    return response.data
  }

  async createContaBancaria(data) {
    const response = await api.post('/financeiro/contas-bancarias/', data)
    return response.data
  }

  async updateContaBancaria(id, data) {
    const response = await api.patch(`/financeiro/contas-bancarias/${id}/`, data)
    return response.data
  }

  async deleteContaBancaria(id) {
    const response = await api.delete(`/financeiro/contas-bancarias/${id}/`)
    return response.data
  }

  // Plano de Contas
  async getPlanosContas(params = {}) {
    const response = await api.get('/financeiro/planos-contas/', { params })
    return response.data
  }

  async getPlanoContas(id) {
    const response = await api.get(`/financeiro/planos-contas/${id}/`)
    return response.data
  }

  async createPlanoContas(data) {
    const response = await api.post('/financeiro/planos-contas/', data)
    return response.data
  }

  async updatePlanoContas(id, data) {
    const response = await api.patch(`/financeiro/planos-contas/${id}/`, data)
    return response.data
  }

  async deletePlanoContas(id) {
    const response = await api.delete(`/financeiro/planos-contas/${id}/`)
    return response.data
  }

  // Contas a Pagar
  async getContasAPagar(params = {}) {
    const response = await api.get('/financeiro/contas-pagar/', { params })
    return response.data
  }

  async getContaAPagar(id) {
    const response = await api.get(`/financeiro/contas-pagar/${id}/`)
    return response.data
  }

  async createContaAPagar(data) {
    const response = await api.post('/financeiro/contas-pagar/', data)
    return response.data
  }

  async updateContaAPagar(id, data) {
    const response = await api.patch(`/financeiro/contas-pagar/${id}/`, data)
    return response.data
  }

  async deleteContaAPagar(id) {
    const response = await api.delete(`/financeiro/contas-pagar/${id}/`)
    return response.data
  }

  async pagarContaAPagar(id, data) {
    const response = await api.post(`/financeiro/contas-pagar/${id}/pagar/`, data)
    return response.data
  }

  // Contas a Receber
  async getContasAReceber(params = {}) {
    const response = await api.get('/financeiro/contas-receber/', { params })
    return response.data
  }

  async getContaAReceber(id) {
    const response = await api.get(`/financeiro/contas-receber/${id}/`)
    return response.data
  }

  async createContaAReceber(data) {
    const response = await api.post('/financeiro/contas-receber/', data)
    return response.data
  }

  async updateContaAReceber(id, data) {
    const response = await api.patch(`/financeiro/contas-receber/${id}/`, data)
    return response.data
  }

  async deleteContaAReceber(id) {
    const response = await api.delete(`/financeiro/contas-receber/${id}/`)
    return response.data
  }

  async receberContaAReceber(id, data) {
    const response = await api.post(`/financeiro/contas-receber/${id}/receber/`, data)
    return response.data
  }

  // Movimentações Financeiras
  async getMovimentacoesFinanceiras(params = {}) {
    const response = await api.get('/financeiro/movimentacoes/', { params })
    return response.data
  }

  async createMovimentacaoFinanceira(data) {
    const response = await api.post('/financeiro/movimentacoes/', data)
    return response.data
  }

  // Fluxo de Caixa
  async getFluxoCaixa(data_inicio, data_fim) {
    const response = await api.get('/financeiro/fluxo-caixa/', { params: { data_inicio, data_fim } })
    return response.data
  }

  // Contas Vencendo Hoje
  async getContasVencendoHoje() {
    const response = await api.get('/financeiro/vencendo-hoje/')
    return response.data
  }
}

export default new FinanceiroService()
