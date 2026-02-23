import api from './api'

class FiscalService {
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

  async autorizarNotaFiscal(id) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/autorizar/`)
    return response.data
  }

  async cancelarNotaFiscal(id, justificativa) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/cancelar/`, { justificativa })
    return response.data
  }

  async getDanfePdf(id) {
    // Este endpoint provavelmente retornará um blob, não JSON
    const response = await api.get(`/fiscal/notas-fiscais/${id}/danfe/`, { responseType: 'blob' })
    return response.data
  }

  async sendNotaFiscalEmail(id, email) {
    const response = await api.post(`/fiscal/notas-fiscais/${id}/email/`, { email })
    return response.data
  }
}

export default new FiscalService()
