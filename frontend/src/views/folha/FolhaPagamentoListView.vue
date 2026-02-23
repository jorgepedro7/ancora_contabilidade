<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Folhas de Pagamento</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando folhas de pagamento...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchFolhasPagamento" placeholder="Buscar folha por competência..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Nova Folha
      </button>
    </div>

    <div v-if="folhasPagamento.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Competência</th>
          <th class="py-3 px-6 text-left">Tipo</th>
          <th class="py-3 px-6 text-left">Status</th>
          <th class="py-3 px-6 text-left">Processamento</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="folha in folhasPagamento" :key="folha.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ formatCompetencia(folha.competencia) }}</td>
          <td class="py-3 px-6 text-left">{{ folha.tipo_folha }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="getStatusClass(folha.status)" class="px-2 py-1 rounded-full text-xs text-white">
              {{ folha.status }}
            </span>
          </td>
          <td class="py-3 px-6 text-left">{{ formatDate(folha.data_processamento) }}</td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <button @click="verDetalhes(folha)" class="text-white hover:text-ancora-gold font-bold mr-3 bg-white/5 px-2 py-1 rounded">Ver Holerites</button>
            <button @click="openModalForEdit(folha)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="calcularFolha(folha.id)" v-if="folha.status === 'ABERTA'" class="text-blue-500 hover:text-blue-400 font-bold mr-3">Processar</button>
            <button @click="fecharFolha(folha.id)" v-if="folha.status === 'PROCESSADA'" class="text-green-500 hover:text-green-400 font-bold mr-3">Fechar</button>
            <button @click="deleteFolha(folha.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhuma folha de pagamento encontrada.
    </div>

    <!-- Modal para Adicionar/Editar Folha de Pagamento -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-ancora-black/70 flex items-center justify-center z-50">
      <div class="bg-ancora-black/90 p-8 rounded-lg shadow-xl border border-ancora-gold/30 w-full max-w-md">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingFolha ? 'Editar Folha' : 'Nova Folha de Pagamento' }}</h2>
        <form @submit.prevent="saveFolhaPagamento" class="space-y-4">
          <div>
            <label for="modal_competencia" class="block text-sm font-body text-gray-300">Competência (Mês/Ano)</label>
            <input type="month" id="modal_competencia" v-model="currentFolha.competencia" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_tipo_folha" class="block text-sm font-body text-gray-300">Tipo de Folha</label>
            <select id="modal_tipo_folha" v-model="currentFolha.tipo_folha" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option value="MENSAL">Mensal</option>
              <option value="DECIMO_TERCEIRO">Décimo Terceiro</option>
              <option value="FERIAS">Férias</option>
              <option value="RESCISAO">Rescisão</option>
            </select>
          </div>
          
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Folha</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal para Detalhes da Folha (Holerites) -->
    <div v-if="isDetailsOpen" class="fixed inset-0 bg-ancora-black/80 flex items-center justify-center z-[60] backdrop-blur-sm p-4">
      <div class="bg-ancora-black border border-ancora-gold/30 p-8 rounded-2xl w-full max-w-4xl shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-2xl font-display text-white">Holerites: {{ formatCompetencia(selectedFolha.competencia) }}</h2>
            <p class="text-xs text-gray-500">Listagem de pagamentos processados para este período.</p>
          </div>
          <button @click="isDetailsOpen = false" class="text-gray-500 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="overflow-x-auto">
           <table class="min-w-full bg-white/5 text-sm">
            <thead>
              <tr class="text-gray-400 text-left border-b border-white/10 uppercase text-[10px] font-bold">
                <th class="py-3 px-4">Funcionário</th>
                <th class="py-3 px-4 text-right">Proventos</th>
                <th class="py-3 px-4 text-right">Descontos</th>
                <th class="py-3 px-4 text-right text-ancora-gold">Líquido</th>
                <th class="py-3 px-4 text-center">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr v-for="h in holeritesFolha" :key="h.id" class="hover:bg-white/5">
                <td class="py-4 px-4 text-white font-bold">{{ h.funcionario_detail?.nome_completo }}</td>
                <td class="py-4 px-4 text-right text-green-400">{{ formatCurrency(h.total_proventos) }}</td>
                <td class="py-4 px-4 text-right text-red-400">{{ formatCurrency(h.total_descontos) }}</td>
                <td class="py-4 px-4 text-right text-white font-bold">{{ formatCurrency(h.liquido_receber) }}</td>
                <td class="py-4 px-4 text-center">
                   <button @click="downloadHolerite(h)" class="text-[10px] bg-ancora-gold text-ancora-black px-2 py-1 rounded font-bold hover:bg-white transition-colors">PDF</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FolhaService from '@/services/folha.service'

const uiStore = useUiStore()

const folhasPagamento = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingFolha = ref(false)
const currentFolha = ref({
  id: null,
  competencia: '',
  tipo_folha: 'MENSAL',
  status: 'ABERTA',
})

const isDetailsOpen = ref(false)
const selectedFolha = ref(null)
const holeritesFolha = ref([])

onMounted(() => {
  fetchFolhasPagamento()
})

async function verDetalhes(folha) {
  selectedFolha.value = folha
  loading.value = true
  try {
    const response = await FolhaService.getHolerites({ folha_pagamento: folha.id })
    holeritesFolha.value = response.results
    isDetailsOpen.value = true
  } catch (err) {
    uiStore.showNotification('Erro ao carregar holerites.', 'error')
  } finally {
    loading.value = false
  }
}

async function fetchFolhasPagamento() {
  loading.value = true
  error.value = null
  try {
    const response = await FolhaService.getFolhasPagamento({ search: searchQuery.value })
    folhasPagamento.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar folhas de pagamento.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar folhas de pagamento:', err)
  } finally {
    loading.value = false
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'ABERTA': return 'bg-blue-500';
    case 'PROCESSADA': return 'bg-yellow-500';
    case 'FECHADA': return 'bg-green-500';
    default: return 'bg-gray-500';
  }
}

function formatCompetencia(dateString) {
  if (!dateString) return '';
  const [year, month] = dateString.split('-');
  return `${month}/${year}`;
}

function formatDate(dateString) {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

const formatCurrency = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

async function downloadHolerite(h) {
  try {
    const blob = await FolhaService.getHoleritePdf(h.id)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `holerite_${h.funcionario_detail?.nome_completo || 'funcionario'}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    uiStore.showNotification('Erro ao baixar PDF.', 'error')
  }
}

function openModalForCreate() {
  editingFolha.value = false
  currentFolha.value = {
    id: null,
    competencia: new Date().toISOString().slice(0, 7), // Mês atual YYYY-MM
    tipo_folha: 'MENSAL',
    status: 'ABERTA',
  }
  isModalOpen.value = true
}

function openModalForEdit(folha) {
  editingFolha.value = true
  currentFolha.value = { ...folha }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveFolhaPagamento() {
  uiStore.setLoading(true)
  try {
    const payload = {
      ...currentFolha.value,
      // Se a competência for YYYY-MM, o backend espera um DateField, então pode precisar de ajuste
      competencia: currentFolha.value.competencia + '-01', // Adiciona o dia 01
    }
    if (editingFolha.value) {
      await FolhaService.updateFolhaPagamento(currentFolha.value.id, payload)
      uiStore.showNotification('Folha de Pagamento atualizada com sucesso!', 'success')
    } else {
      await FolhaService.createFolhaPagamento(payload)
      uiStore.showNotification('Folha de Pagamento criada com sucesso!', 'success')
    }
    closeModal()
    fetchFolhasPagamento()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar folha de pagamento.', 'error')
    console.error('Erro ao salvar folha de pagamento:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function calcularFolha(id) {
  if (confirm('Tem certeza que deseja calcular esta folha de pagamento?')) {
    uiStore.setLoading(true)
    try {
      await FolhaService.calcularFolhaPagamento(id)
      uiStore.showNotification('Folha de Pagamento calculada com sucesso!', 'success')
      fetchFolhasPagamento()
    } catch (err) {
      uiStore.showNotification('Erro ao calcular folha de pagamento.', 'error')
      console.error('Erro ao calcular folha de pagamento:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

async function fecharFolha(id) {
  if (confirm('Tem certeza que deseja fechar esta folha de pagamento?')) {
    uiStore.setLoading(true)
    try {
      await FolhaService.fecharFolhaPagamento(id)
      uiStore.showNotification('Folha de Pagamento fechada com sucesso!', 'success')
      fetchFolhasPagamento()
    } catch (err) {
      uiStore.showNotification('Erro ao fechar folha de pagamento.', 'error')
      console.error('Erro ao fechar folha de pagamento:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

async function deleteFolha(id) {
  if (confirm('Tem certeza que deseja excluir esta folha de pagamento? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await FolhaService.deleteFolhaPagamento(id)
      uiStore.showNotification('Folha de Pagamento excluída com sucesso!', 'success')
      fetchFolhasPagamento()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir folha de pagamento.', 'error')
      console.error('Erro ao excluir folha de pagamento:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>