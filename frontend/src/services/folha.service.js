import api from './api'

class FolhaService {
  // Cargos
  async getCargos(params = {}) {
    const response = await api.get('/folha/cargos/', { params })
    return response.data
  }

  async getCargo(id) {
    const response = await api.get(`/folha/cargos/${id}/`)
    return response.data
  }

  async createCargo(data) {
    const response = await api.post('/folha/cargos/', data)
    return response.data
  }

  async updateCargo(id, data) {
    const response = await api.patch(`/folha/cargos/${id}/`, data)
    return response.data
  }

  async deleteCargo(id) {
    const response = await api.delete(`/folha/cargos/${id}/`)
    return response.data
  }

  // Departamentos
  async getDepartamentos(params = {}) {
    const response = await api.get('/folha/departamentos/', { params })
    return response.data
  }

  async getDepartamento(id) {
    const response = await api.get(`/folha/departamentos/${id}/`)
    return response.data
  }

  async createDepartamento(data) {
    const response = await api.post('/folha/departamentos/', data)
    return response.data
  }

  async updateDepartamento(id, data) {
    const response = await api.patch(`/folha/departamentos/${id}/`, data)
    return response.data
  }

  async deleteDepartamento(id) {
    const response = await api.delete(`/folha/departamentos/${id}/`)
    return response.data
  }

  // Funcionários
  async getFuncionarios(params = {}) {
    const response = await api.get('/folha/funcionarios/', { params })
    return response.data
  }

  async getFuncionario(id) {
    const response = await api.get(`/folha/funcionarios/${id}/`)
    return response.data
  }

  async createFuncionario(data) {
    const response = await api.post('/folha/funcionarios/', data)
    return response.data
  }

  async updateFuncionario(id, data) {
    const response = await api.patch(`/folha/funcionarios/${id}/`, data)
    return response.data
  }

  async deleteFuncionario(id) {
    const response = await api.delete(`/folha/funcionarios/${id}/`)
    return response.data
  }

  // Contratos de Trabalho
  async getContratos(params = {}) {
    const response = await api.get('/folha/contratos/', { params })
    return response.data
  }

  async getContrato(id) {
    const response = await api.get(`/folha/contratos/${id}/`)
    return response.data
  }

  async createContrato(data) {
    const response = await api.post('/folha/contratos/', data)
    return response.data
  }

  async updateContrato(id, data) {
    const response = await api.patch(`/folha/contratos/${id}/`, data)
    return response.data
  }

  async deleteContrato(id) {
    const response = await api.delete(`/folha/contratos/${id}/`)
    return response.data
  }

  // Folha de Pagamento
  async getFolhasPagamento(params = {}) {
    const response = await api.get('/folha/folha-pagamento/', { params })
    return response.data
  }

  async getFolhaPagamento(id) {
    const response = await api.get(`/folha/folha-pagamento/${id}/`)
    return response.data
  }

  async createFolhaPagamento(data) {
    const response = await api.post('/folha/folha-pagamento/', data)
    return response.data
  }

  async updateFolhaPagamento(id, data) {
    const response = await api.patch(`/folha/folha-pagamento/${id}/`, data)
    return response.data
  }

  async deleteFolhaPagamento(id) {
    const response = await api.delete(`/folha/folha-pagamento/${id}/`)
    return response.data
  }

  async calcularFolhaPagamento(id) {
    const response = await api.post(`/folha/folha-pagamento/${id}/calcular/`)
    return response.data
  }

  async fecharFolhaPagamento(id) {
    const response = await api.post(`/folha/folha-pagamento/${id}/fechar/`)
    return response.data
  }

  // Holerites
  async getHolerites(params = {}) {
    const response = await api.get('/folha/holerites/', { params })
    return response.data
  }

  async getHolerite(id) {
    const response = await api.get(`/folha/holerites/${id}/`)
    return response.data
  }

  async getHoleritePdf(id) {
    const response = await api.get(`/folha/holerites/${id}/pdf/`, { responseType: 'blob' })
    return response.data
  }

  // Ponto e Justificativas
  async getRegistrosPonto(params = {}) {
    const response = await api.get('/folha/pontos/', { params })
    return response.data
  }

  async createRegistroPonto(data) {
    const response = await api.post('/folha/pontos/', data)
    return response.data
  }

  async getJustificativas(params = {}) {
    const response = await api.get('/folha/justificativas/', { params })
    return response.data
  }

  async createJustificativa(data) {
    const response = await api.post('/folha/justificativas/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  // Documentos
  async getDocumentos(params = {}) {
    const response = await api.get('/folha/documentos/', { params })
    return response.data
  }

  async createDocumento(data) {
    const response = await api.post('/folha/documentos/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}

export default new FolhaService()
