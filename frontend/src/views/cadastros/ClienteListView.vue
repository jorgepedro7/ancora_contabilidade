<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Clientes</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando clientes...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchClientes" placeholder="Buscar cliente por nome ou documento..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Novo Cliente
      </button>
    </div>

    <div v-if="clientes.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Nome/Razão Social</th>
          <th class="py-3 px-6 text-left">CPF/CNPJ</th>
          <th class="py-3 px-6 text-left">Tipo</th>
          <th class="py-3 px-6 text-left">Ativo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="cliente in clientes" :key="cliente.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ cliente.nome_razao_social }}</td>
          <td class="py-3 px-6 text-left">{{ formatDocumento(cliente.documento, cliente.tipo_pessoa) }}</td>
          <td class="py-3 px-6 text-left">{{ cliente.tipo_pessoa }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="cliente.ativo ? 'bg-green-500' : 'bg-red-500'" class="px-2 py-1 rounded-full text-xs text-white">
              {{ cliente.ativo ? 'Sim' : 'Não' }}
            </span>
          </td>
          <td class="py-3 px-6 text-center">
            <button @click="openModalForEdit(cliente)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="deleteCliente(cliente.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum cliente encontrado.
    </div>

    <!-- Modal para Adicionar/Editar Cliente -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-ancora-black/70 flex items-center justify-center z-50">
      <div class="bg-ancora-black/90 p-8 rounded-lg shadow-xl border border-ancora-gold/30 w-full max-w-lg">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingCliente ? 'Editar Cliente' : 'Novo Cliente' }}</h2>
        <form @submit.prevent="saveCliente" class="space-y-4">
          <div>
            <label for="modal_nome_razao_social" class="block text-sm font-body text-gray-300">Nome/Razão Social</label>
            <input type="text" id="modal_nome_razao_social" v-model="currentCliente.nome_razao_social" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_tipo_pessoa" class="block text-sm font-body text-gray-300">Tipo de Pessoa</label>
            <select id="modal_tipo_pessoa" v-model="currentCliente.tipo_pessoa" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option value="PF">Pessoa Física</option>
              <option value="PJ">Pessoa Jurídica</option>
            </select>
          </div>
          <div>
            <label for="modal_documento" class="block text-sm font-body text-gray-300">CPF/CNPJ</label>
            <input type="text" id="modal_documento" v-model="currentCliente.documento" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_email" class="block text-sm font-body text-gray-300">E-mail</label>
            <input type="email" id="modal_email" v-model="currentCliente.email"
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Cliente</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import CadastrosService from '@/services/cadastros.service' // Precisamos criar este serviço

const uiStore = useUiStore()

const clientes = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingCliente = ref(false)
const currentCliente = ref({
  id: null,
  nome_razao_social: '',
  tipo_pessoa: 'PF',
  documento: '',
  email: '',
  // Adicionar outros campos conforme necessário
})

onMounted(() => {
  fetchClientes()
})

async function fetchClientes() {
  loading.value = true
  error.value = null
  try {
    const response = await CadastrosService.getClientes({ search: searchQuery.value })
    clientes.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar clientes.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar clientes:', err)
  } finally {
    loading.value = false
  }
}

function formatDocumento(doc, tipo) {
  if (!doc) return ''
  // Reutiliza função do backend se puder ou implementa no frontend
  if (tipo === 'PF') {
    return doc.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  } else if (tipo === 'PJ') {
    return doc.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
  }
  return doc
}

function openModalForCreate() {
  editingCliente.value = false
  currentCliente.value = {
    id: null,
    nome_razao_social: '',
    tipo_pessoa: 'PF',
    documento: '',
    email: '',
  }
  isModalOpen.value = true
}

function openModalForEdit(cliente) {
  editingCliente.value = true
  currentCliente.value = { ...cliente } // Cria uma cópia para edição
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveCliente() {
  uiStore.setLoading(true)
  try {
    if (editingCliente.value) {
      await CadastrosService.updateCliente(currentCliente.value.id, currentCliente.value)
      uiStore.showNotification('Cliente atualizado com sucesso!', 'success')
    } else {
      await CadastrosService.createCliente(currentCliente.value)
      uiStore.showNotification('Cliente criado com sucesso!', 'success')
    }
    closeModal()
    fetchClientes() // Recarregar a lista
  } catch (err) {
    uiStore.showNotification('Erro ao salvar cliente.', 'error')
    console.error('Erro ao salvar cliente:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteCliente(id) {
  if (confirm('Tem certeza que deseja excluir este cliente? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await CadastrosService.deleteCliente(id)
      uiStore.showNotification('Cliente excluído com sucesso!', 'success')
      fetchClientes()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir cliente.', 'error')
      console.error('Erro ao excluir cliente:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>