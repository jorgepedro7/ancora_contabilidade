import api from './api'

const UsuariosService = {
  listEquipe() {
    return api.get('/core/usuarios/?tipo=equipe').then(r => r.data)
  },

  listClientes() {
    return api.get('/core/usuarios/?tipo=cliente').then(r => r.data)
  },

  createUsuario(data) {
    return api.post('/core/usuarios/', data).then(r => r.data)
  },

  updateUsuario(id, data) {
    return api.patch(`/core/usuarios/${id}/`, data).then(r => r.data)
  },

  deleteUsuario(id) {
    return api.delete(`/core/usuarios/${id}/`).then(r => r.data)
  },
}

export default UsuariosService
