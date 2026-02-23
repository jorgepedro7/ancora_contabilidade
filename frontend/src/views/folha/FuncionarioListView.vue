<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Funcionários</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando funcionários...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchFuncionarios" placeholder="Buscar funcionário por nome ou CPF..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Novo Funcionário
      </button>
    </div>

    <div v-if="funcionarios.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Nome</th>
          <th class="py-3 px-6 text-left">CPF</th>
          <th class="py-3 px-6 text-left">Cargo</th>
          <th class="py-3 px-6 text-left">Departamento</th>
          <th class="py-3 px-6 text-left">Ativo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="func in funcionarios" :key="func.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ func.nome_completo }}</td>
          <td class="py-3 px-6 text-left">{{ formatCpf(func.cpf) }}</td>
          <td class="py-3 px-6 text-left">{{ func.contrato_ativo_detail?.cargo_detail?.nome || 'N/A' }}</td>
          <td class="py-3 px-6 text-left">{{ func.contrato_ativo_detail?.departamento_detail?.nome || 'N/A' }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="func.ativo ? 'bg-green-500' : 'bg-red-500'" class="px-2 py-1 rounded-full text-xs text-white">
              {{ func.ativo ? 'Sim' : 'Não' }}
            </span>
          </td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <router-link :to="{ name: 'funcionario-detail', params: { id: func.id } }" class="text-blue-400 hover:text-blue-300 font-bold mr-3">Visualizar</router-link>
            <button @click="openModalForEdit(func)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="deleteFuncionario(func.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum funcionário encontrado.
    </div>

    <!-- Modal para Adicionar/Editar Funcionário -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-ancora-black/70 flex items-center justify-center z-50">
      <div class="bg-ancora-black/90 p-8 rounded-lg shadow-xl border border-ancora-gold/30 w-full max-w-2xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingFuncionario ? 'Editar Funcionário' : 'Novo Funcionário' }}</h2>
        <form @submit.prevent="saveFuncionario" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="modal_nome_completo" class="block text-sm font-body text-gray-300">Nome Completo</label>
              <input type="text" id="modal_nome_completo" v-model="currentFuncionario.nome_completo" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_cpf" class="block text-sm font-body text-gray-300">CPF</label>
              <input type="text" id="modal_cpf" v-model="currentFuncionario.cpf" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_data_nascimento" class="block text-sm font-body text-gray-300">Data de Nascimento</label>
              <input type="date" id="modal_data_nascimento" v-model="currentFuncionario.data_nascimento" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_email" class="block text-sm font-body text-gray-300">E-mail</label>
              <input type="email" id="modal_email" v-model="currentFuncionario.email"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_dependentes" class="block text-sm font-body text-gray-300">Dependentes IRRF</label>
              <input type="number" id="modal_dependentes" v-model="currentFuncionario.dependentes"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <!-- Outros campos do funcionário, se necessário -->
          </div>
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Funcionário</span>
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
import FolhaService from '@/services/folha.service' // Precisamos criar este serviço

const uiStore = useUiStore()

const funcionarios = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingFuncionario = ref(false)
const currentFuncionario = ref({
  id: null,
  nome_completo: '',
  cpf: '',
  data_nascimento: '',
  email: '',
  dependentes: 0,
})

onMounted(() => {
  fetchFuncionarios()
})

async function fetchFuncionarios() {
  loading.value = true
  error.value = null
  try {
    const response = await FolhaService.getFuncionarios({ search: searchQuery.value, expand: 'contrato_ativo' }) // Assume que há um contrato ativo para exibir cargo/depto
    funcionarios.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar funcionários.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar funcionários:', err)
  } finally {
    loading.value = false
  }
}

function formatCpf(cpf) {
  if (!cpf) return ''
  return cpf.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
}

function openModalForCreate() {
  editingFuncionario.value = false
  currentFuncionario.value = {
    id: null,
    nome_completo: '',
    cpf: '',
    data_nascimento: '',
    email: '',
    dependentes: 0,
  }
  isModalOpen.value = true
}

function openModalForEdit(func) {
  editingFuncionario.value = true
  currentFuncionario.value = { ...func }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveFuncionario() {
  uiStore.setLoading(true)
  try {
    if (editingFuncionario.value) {
      await FolhaService.updateFuncionario(currentFuncionario.value.id, currentFuncionario.value)
      uiStore.showNotification('Funcionário atualizado com sucesso!', 'success')
    } else {
      await FolhaService.createFuncionario(currentFuncionario.value)
      uiStore.showNotification('Funcionário criado com sucesso!', 'success')
    }
    closeModal()
    fetchFuncionarios()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar funcionário.', 'error')
    console.error('Erro ao salvar funcionário:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteFuncionario(id) {
  if (confirm('Tem certeza que deseja excluir este funcionário? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await FolhaService.deleteFuncionario(id)
      uiStore.showNotification('Funcionário excluído com sucesso!', 'success')
      fetchFuncionarios()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir funcionário.', 'error')
      console.error('Erro ao excluir funcionário:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>