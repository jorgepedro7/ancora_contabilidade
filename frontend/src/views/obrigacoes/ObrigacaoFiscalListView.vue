<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Obrigações Fiscais</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando obrigações...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchObrigacoes" placeholder="Buscar obrigação por descrição..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Nova Obrigação
      </button>
    </div>

    <div v-if="obrigacoes.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Tipo</th>
          <th class="py-3 px-6 text-left">Descrição</th>
          <th class="py-3 px-6 text-left">Vencimento</th>
          <th class="py-3 px-6 text-right">Valor</th>
          <th class="py-3 px-6 text-left">Status</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="obrigacao in obrigacoes" :key="obrigacao.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ obrigacao.tipo_obrigacao_display }}</td>
          <td class="py-3 px-6 text-left">{{ obrigacao.descricao }}</td>
          <td class="py-3 px-6 text-left">{{ formatDate(obrigacao.data_vencimento) }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(obrigacao.valor) }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="getStatusClass(obrigacao.status)" class="px-2 py-1 rounded-full text-xs text-white">
              {{ obrigacao.status_display }}
            </span>
          </td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <button @click="openModalForEdit(obrigacao)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="deleteObrigacao(obrigacao.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhuma obrigação fiscal encontrada.
    </div>

    <!-- Modal para Adicionar/Editar Obrigação Fiscal -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-ancora-black/70 flex items-center justify-center z-50">
      <div class="bg-ancora-black/90 p-8 rounded-lg shadow-xl border border-ancora-gold/30 w-full max-w-lg">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingObrigacao ? 'Editar Obrigação' : 'Nova Obrigação Fiscal' }}</h2>
        <form @submit.prevent="saveObrigacao" class="space-y-4">
          <div>
            <label for="modal_tipo_obrigacao" class="block text-sm font-body text-gray-300">Tipo de Obrigação</label>
            <select id="modal_tipo_obrigacao" v-model="currentObrigacao.tipo_obrigacao" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option v-for="type in tipoObrigacaoChoices" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
          </div>
          <div>
            <label for="modal_descricao" class="block text-sm font-body text-gray-300">Descrição</label>
            <textarea id="modal_descricao" v-model="currentObrigacao.descricao" rows="3"
                      class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"></textarea>
          </div>
          <div>
            <label for="modal_data_vencimento" class="block text-sm font-body text-gray-300">Data de Vencimento</label>
            <input type="date" id="modal_data_vencimento" v-model="currentObrigacao.data_vencimento" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_valor" class="block text-sm font-body text-gray-300">Valor</label>
            <input type="number" step="0.01" id="modal_valor" v-model="currentObrigacao.valor"
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_status" class="block text-sm font-body text-gray-300">Status</label>
            <select id="modal_status" v-model="currentObrigacao.status" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option v-for="s in statusChoices" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
          </div>
          
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Obrigação</span>
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
import ObrigacoesService from '@/services/obrigacoes.service' // Precisamos criar este serviço

const uiStore = useUiStore()

const obrigacoes = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingObrigacao = ref(false)
const currentObrigacao = ref({
  id: null,
  tipo_obrigacao: '',
  descricao: '',
  data_vencimento: '',
  valor: 0,
  status: 'ABERTO',
})

const tipoObrigacaoChoices = ref([
  { value: 'DARF', label: 'DARF' },
  { value: 'PGDAS', label: 'PGDAS-D' },
  { value: 'DAE', label: 'DAE' },
  { value: 'DAS_MEI', label: 'DAS-MEI' },
  { value: 'DIRF', label: 'DIRF' },
  { value: 'DCTF', label: 'DCTF' },
  { value: 'DEFIS', label: 'DEFIS' },
  { value: 'GIA', label: 'GIA' },
  { value: 'DESTDA', label: 'DeSTDA' },
  { value: 'ESOCIAL', label: 'eSocial' },
  { value: 'EFD', label: 'EFD' },
  { value: 'OUTRO', label: 'Outro' },
])

const statusChoices = ref([
  { value: 'ABERTO', label: 'Aberto' },
  { value: 'ATRASADO', label: 'Atrasado' },
  { value: 'PAGO', label: 'Pago' },
  { value: 'ENVIADO', label: 'Enviado' },
  { value: 'CONCLUIDO', label: 'Concluído' },
  { value: 'CANCELADO', label: 'Cancelado' },
])

onMounted(() => {
  fetchObrigacoes()
})

async function fetchObrigacoes() {
  loading.value = true
  error.value = null
  try {
    const response = await ObrigacoesService.getObrigacoes({ search: searchQuery.value })
    obrigacoes.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar obrigações fiscais.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar obrigações fiscais:', err)
  } finally {
    loading.value = false
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'ABERTO': return 'bg-blue-500';
    case 'ATRASADO': return 'bg-red-500';
    case 'PAGO':
    case 'ENVIADO':
    case 'CONCLUIDO': return 'bg-green-500';
    case 'CANCELADO': return 'bg-gray-500';
    default: return 'bg-gray-500';
  }
}

function formatCurrency(value) {
  if (value === null || value === undefined) return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(0)
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function formatDate(dateString) {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

function openModalForCreate() {
  editingObrigacao.value = false
  currentObrigacao.value = {
    id: null,
    tipo_obrigacao: 'DARF',
    descricao: '',
    data_vencimento: new Date().toISOString().split('T')[0],
    valor: 0,
    status: 'ABERTO',
  }
  isModalOpen.value = true
}

function openModalForEdit(obrigacao) {
  editingObrigacao.value = true
  currentObrigacao.value = { ...obrigacao }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveObrigacao() {
  uiStore.setLoading(true)
  try {
    if (editingObrigacao.value) {
      await ObrigacoesService.updateObrigacao(currentObrigacao.value.id, currentObrigacao.value)
      uiStore.showNotification('Obrigação Fiscal atualizada com sucesso!', 'success')
    } else {
      await ObrigacoesService.createObrigacao(currentObrigacao.value)
      uiStore.showNotification('Obrigação Fiscal criada com sucesso!', 'success')
    }
    closeModal()
    fetchObrigacoes()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar obrigação fiscal.', 'error')
    console.error('Erro ao salvar obrigação fiscal:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteObrigacao(id) {
  if (confirm('Tem certeza que deseja excluir esta obrigação fiscal? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await ObrigacoesService.deleteObrigacao(id)
      uiStore.showNotification('Obrigação Fiscal excluída com sucesso!', 'success')
      fetchObrigacoes()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir obrigação fiscal.', 'error')
      console.error('Erro ao excluir obrigação fiscal:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>