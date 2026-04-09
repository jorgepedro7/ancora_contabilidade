<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Lançamentos Contábeis</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando lançamentos...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchLancamentos" placeholder="Buscar lançamento por histórico..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Novo Lançamento
      </button>
    </div>

    <div v-if="lancamentos.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Data</th>
          <th class="py-3 px-6 text-left">Histórico</th>
          <th class="py-3 px-6 text-left">Tipo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="lancamento in lancamentos" :key="lancamento.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ formatDate(lancamento.data_lancamento) }}</td>
          <td class="py-3 px-6 text-left">{{ lancamento.historico }}</td>
          <td class="py-3 px-6 text-left">{{ lancamento.tipo_lancamento }}</td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <button @click="openModalForEdit(lancamento)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="deleteLancamento(lancamento.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum lançamento contábil encontrado.
    </div>

    <!-- Modal para Adicionar/Editar Lançamento Contábil -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingLancamento ? 'Editar Lançamento' : 'Novo Lançamento Contábil' }}</h2>
        <form @submit.prevent="saveLancamento" class="space-y-4">
          <div>
            <label for="modal_data_lancamento" class="block text-sm font-body text-gray-300">Data do Lançamento</label>
            <input type="date" id="modal_data_lancamento" v-model="currentLancamento.data_lancamento" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_historico" class="block text-sm font-body text-gray-300">Histórico</label>
            <textarea id="modal_historico" v-model="currentLancamento.historico" required rows="3"
                      class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"></textarea>
          </div>
          <div>
            <label for="modal_tipo_lancamento" class="block text-sm font-body text-gray-300">Tipo de Lançamento</label>
            <select id="modal_tipo_lancamento" v-model="currentLancamento.tipo_lancamento" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option value="SIMPLES">Simples</option>
              <option value="COMPOSTO">Composto</option>
            </select>
          </div>

          <!-- Partidas do Lançamento -->
          <h3 class="text-lg font-body text-ancora-gold mt-4 mb-2">Partidas Contábeis</h3>
          <div v-for="(partida, index) in currentLancamento.partidas" :key="index"
               class="grid grid-cols-4 gap-2 bg-ancora-black/70 p-3 rounded-md border border-ancora-gold/10">
            <div>
              <label :for="'conta_contabil_' + index" class="block text-xs font-body text-gray-400">Conta Contábil</label>
              <select :id="'conta_contabil_' + index" v-model="partida.conta_contabil" required
                      class="mt-1 block w-full px-2 py-1 bg-ancora-black/80 border border-ancora-gold/10 rounded-md sm:text-xs text-white">
                <option v-for="pc in planoContasList" :key="pc.id" :value="pc.id">{{ pc.codigo }} - {{ pc.descricao }}</option>
              </select>
            </div>
            <div>
              <label :for="'tipo_partida_' + index" class="block text-xs font-body text-gray-400">Tipo</label>
              <select :id="'tipo_partida_' + index" v-model="partida.tipo_partida" required
                      class="mt-1 block w-full px-2 py-1 bg-ancora-black/80 border border-ancora-gold/10 rounded-md sm:text-xs text-white">
                <option value="D">Débito</option>
                <option value="C">Crédito</option>
              </select>
            </div>
            <div>
              <label :for="'valor_' + index" class="block text-xs font-body text-gray-400">Valor</label>
              <input type="number" step="0.01" :id="'valor_' + index" v-model="partida.valor" required
                     class="mt-1 block w-full px-2 py-1 bg-ancora-black/80 border border-ancora-gold/10 rounded-md sm:text-xs text-white"/>
            </div>
            <div class="flex items-end justify-center">
              <button type="button" @click="removePartida(index)" class="text-red-500 hover:text-red-400">Remover</button>
            </div>
          </div>
          <button type="button" @click="addPartida"
                  class="mt-2 px-3 py-1 bg-ancora-navy text-ancora-gold text-sm rounded-md hover:bg-ancora-navy/80">
            Adicionar Partida
          </button>
          
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Lançamento</span>
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
import ContabilService from '@/services/contabil.service' // Precisamos criar este serviço
import FinanceiroService from '@/services/financeiro.service' // Para buscar Plano de Contas

const uiStore = useUiStore()

const lancamentos = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingLancamento = ref(false)
const currentLancamento = ref({
  id: null,
  data_lancamento: '',
  historico: '',
  tipo_lancamento: 'SIMPLES',
  partidas: [],
})

const planoContasList = ref([])

onMounted(() => {
  fetchLancamentos()
  fetchPlanoContasList()
})

async function fetchLancamentos() {
  loading.value = true
  error.value = null
  try {
    const response = await ContabilService.getLancamentos({ search: searchQuery.value })
    lancamentos.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar lançamentos contábeis.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar lançamentos contábeis:', err)
  } finally {
    loading.value = false
  }
}

async function fetchPlanoContasList() {
  try {
    const response = await FinanceiroService.getPlanosContas({ page_size: 1000, ativo: true })
    planoContasList.value = response.results
  } catch (err) {
    console.error('Erro ao carregar plano de contas:', err)
  }
}

function formatDate(dateString) {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

function openModalForCreate() {
  editingLancamento.value = false
  currentLancamento.value = {
    id: null,
    data_lancamento: new Date().toISOString().split('T')[0],
    historico: '',
    tipo_lancamento: 'SIMPLES',
    partidas: [{ conta_contabil: null, tipo_partida: 'D', valor: 0 }, { conta_contabil: null, tipo_partida: 'C', valor: 0 }],
  }
  isModalOpen.value = true
}

function openModalForEdit(lancamento) {
  editingLancamento.value = true
  currentLancamento.value = { ...lancamento }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

function addPartida() {
  currentLancamento.value.partidas.push({ conta_contabil: null, tipo_partida: 'D', valor: 0 })
}

function removePartida(index) {
  currentLancamento.value.partidas.splice(index, 1)
}

async function saveLancamento() {
  uiStore.setLoading(true)
  try {
    if (editingLancamento.value) {
      await ContabilService.updateLancamento(currentLancamento.value.id, currentLancamento.value)
      uiStore.showNotification('Lançamento contábil atualizado com sucesso!', 'success')
    } else {
      await ContabilService.createLancamento(currentLancamento.value)
      uiStore.showNotification('Lançamento contábil criado com sucesso!', 'success')
    }
    closeModal()
    fetchLancamentos()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar lançamento contábil.', 'error')
    console.error('Erro ao salvar lançamento contábil:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteLancamento(id) {
  if (confirm('Tem certeza que deseja excluir este lançamento contábil? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await ContabilService.deleteLancamento(id)
      uiStore.showNotification('Lançamento contábil excluído com sucesso!', 'success')
      fetchLancamentos()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir lançamento contábil.', 'error')
      console.error('Erro ao excluir lançamento contábil:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>
