import api from './api'

class EmpresasService {
  async getEmpresas(params = {}) {
    const response = await api.get('/empresas/', { params })
    return response.data
  }

  async getEmpresa(id) {
    const response = await api.get(`/empresas/${id}/`)
    return response.data
  }

  async createEmpresa(data) {
    const response = await api.post('/empresas/', data)
    return response.data
  }

  async updateEmpresa(id, data) {
    const config = data instanceof FormData ? {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    } : {}
    const response = await api.patch(`/empresas/${id}/`, data, config)
    return response.data
  }

  async deleteEmpresa(id) {
    const response = await api.delete(`/empresas/${id}/`)
    return response.data
  }

  async selectEmpresa(id) {
    const response = await api.post(`/empresas/${id}/selecionar/`)
    return response.data
  }

  async clearEmpresaSelection() {
    const response = await api.post('/empresas/desselecionar/')
    return response.data
  }

  async buscarCep(cep) {
    const response = await api.post('/empresas/buscar-cep/', { cep })
    return response.data
  }

  async getResumoFiscal(id) {
    const response = await api.get(`/empresas/${id}/resumo-fiscal/`)
    return response.data
  }
}

export default new EmpresasService()
