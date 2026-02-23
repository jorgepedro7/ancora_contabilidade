import api from './api'

class CadastrosService {
  // Clientes
  async getClientes(params = {}) {
    const response = await api.get('/cadastros/clientes/', { params })
    return response.data
  }

  async getCliente(id) {
    const response = await api.get(`/cadastros/clientes/${id}/`)
    return response.data
  }

  async createCliente(data) {
    const response = await api.post('/cadastros/clientes/', data)
    return response.data
  }

  async updateCliente(id, data) {
    const response = await api.patch(`/cadastros/clientes/${id}/`, data)
    return response.data
  }

  async deleteCliente(id) {
    const response = await api.delete(`/cadastros/clientes/${id}/`)
    return response.data
  }

  // Fornecedores
  async getFornecedores(params = {}) {
    const response = await api.get('/cadastros/fornecedores/', { params })
    return response.data
  }

  async getFornecedor(id) {
    const response = await api.get(`/cadastros/fornecedores/${id}/`)
    return response.data
  }

  async createFornecedor(data) {
    const response = await api.post('/cadastros/fornecedores/', data)
    return response.data
  }

  async updateFornecedor(id, data) {
    const response = await api.patch(`/cadastros/fornecedores/${id}/`, data)
    return response.data
  }

  async deleteFornecedor(id) {
    const response = await api.delete(`/cadastros/fornecedores/${id}/`)
    return response.data
  }

  // Produtos
  async getProdutos(params = {}) {
    const response = await api.get('/cadastros/produtos/', { params })
    return response.data
  }

  async getProduto(id) {
    const response = await api.get(`/cadastros/produtos/${id}/`)
    return response.data
  }

  async createProduto(data) {
    const response = await api.post('/cadastros/produtos/', data)
    return response.data
  }

  async updateProduto(id, data) {
    const response = await api.patch(`/cadastros/produtos/${id}/`, data)
    return response.data
  }

  async deleteProduto(id) {
    const response = await api.delete(`/cadastros/produtos/${id}/`)
    return response.data
  }
}

export default new CadastrosService()
