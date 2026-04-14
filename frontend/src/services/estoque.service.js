import api from './api'

class EstoqueService {
  // Locais de Estoque
  async listarLocais(params = {}) {
    const response = await api.get('/estoque/locais/', { params })
    return response.data
  }

  // Movimentações
  async listarMovimentacoes(params = {}) {
    const response = await api.get('/estoque/movimentacoes/', { params })
    return response.data
  }

  async registrarEntrada(data) {
    const response = await api.post('/estoque/movimentacoes/entrada/', data)
    return response.data
  }

  async registrarSaida(data) {
    const response = await api.post('/estoque/movimentacoes/saida/', data)
    return response.data
  }

  async registrarAjuste(data) {
    // data deve conter: produto, quantidade (delta), observacoes
    const response = await api.post('/estoque/movimentacoes/', {
      ...data,
      tipo_movimentacao: 'AJUSTE',
    })
    return response.data
  }

  // Posição de Estoque
  async getPosicao(params = {}) {
    const response = await api.get('/estoque/posicao/', { params })
    return response.data
  }

  // Inventários
  async listarInventarios(params = {}) {
    const response = await api.get('/estoque/inventarios/', { params })
    return response.data
  }

  async abrirInventario(data) {
    const response = await api.post('/estoque/inventarios/', data)
    return response.data
  }

  async finalizarInventario(id) {
    const response = await api.post(`/estoque/inventarios/${id}/finalizar_inventario/`)
    return response.data
  }

  async cancelarInventario(id) {
    const response = await api.post(`/estoque/inventarios/${id}/cancelar_inventario/`)
    return response.data
  }
}

export default new EstoqueService()
