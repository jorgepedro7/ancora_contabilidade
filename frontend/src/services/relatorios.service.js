import api from './api'

class RelatoriosService {
  async getDashboard() {
    const response = await api.get('/relatorios/dashboard/')
    return response.data
  }

  async getDRE(params = {}) {
    const response = await api.get('/relatorios/dre/', { params })
    return response.data
  }

  async getLivroFiscal(params = {}) {
    const response = await api.get('/relatorios/livro-fiscal/', { params })
    return response.data
  }

  async getPosicaoEstoque() {
    const response = await api.get('/relatorios/posicao-estoque/')
    return response.data
  }

  async getFolhaCompetencia(competencia) {
    const response = await api.get('/relatorios/folha-competencia/', {
      params: { competencia },
    })
    return response.data
  }
}

export default new RelatoriosService()
