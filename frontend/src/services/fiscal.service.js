import api from './api'

class FiscalService {
  // Notas Fiscais
  async getNotasFiscais(params = {}) {
    const response = await api.get('/fiscal/notas-fiscais/', { params })
    return response.data
  }

  async getNotaFiscal(id) {
    const response = await api.get(`/fiscal/notas-fiscais/${id}/`)
    return response.data
  }

  async createNotaFiscal(data) {
    const response = await api.post('/fiscal/notas-fiscais/', data)
    return response.data
  }

  async updateNotaFiscal(id, data) {
    const response = await api.patch(`/fiscal/notas-fiscais/${id}/`, data)
    return response.data
  }

  async deleteNotaFiscal(id) {
    const response = await api.delete(`/fiscal/notas-fiscais/${id}/`)
    return response.data
  }

  async autorizarNotaFiscal(id) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/autorizar/`)
    return response.data
  }

  async cancelarNotaFiscal(id, justificativa) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/cancelar/`, { justificativa })
    return response.data
  }

  async getDanfePdf(id) {
    const response = await api.get(`/fiscal/notas-fiscais/${id}/danfe/`, { responseType: 'blob' })
    return response.data
  }

  async sendNotaFiscalEmail(id, email) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/email/`, { email })
    return response.data
  }

  // Itens da Nota Fiscal
  async getItens(notaFiscalId) {
    const response = await api.get(`/fiscal/notas-fiscais/${notaFiscalId}/itens/`)
    return response.data
  }

  async createItem(notaFiscalId, data) {
    const response = await api.post(`/fiscal/notas-fiscais/${notaFiscalId}/itens/`, {
      ...data,
      nota_fiscal: notaFiscalId,
    })
    return response.data
  }

  async updateItem(notaFiscalId, itemId, data) {
    const response = await api.patch(`/fiscal/notas-fiscais/${notaFiscalId}/itens/${itemId}/`, data)
    return response.data
  }

  async deleteItem(notaFiscalId, itemId) {
    const response = await api.delete(`/fiscal/notas-fiscais/${notaFiscalId}/itens/${itemId}/`)
    return response.data
  }
}

export default new FiscalService()
