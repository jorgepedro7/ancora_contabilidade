<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Contas a Receber</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando contas a receber...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchContasAReceber" placeholder="Buscar conta por descrição ou cliente..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Nova Conta a Receber
      </button>
    </div>

    <div v-if="contasAReceber.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Descrição</th>
          <th class="py-3 px-6 text-left">Cliente</th>
          <th class="py-3 px-6 text-left">Vencimento</th>
          <th class="py-3 px-6 text-right">Valor Total</th>
          <th class="py-3 px-6 text-right">Valor Recebido</th>
          <th class="py-3 px-6 text-right">Saldo</th>
          <th class="py-3 px-6 text-left">Status</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="conta in contasAReceber" :key="conta.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ conta.descricao }}</td>
          <td class="py-3 px-6 text-left">{{ conta.cliente_detail?.nome_razao_social }}</td>
          <td class="py-3 px-6 text-left">{{ formatDate(conta.data_vencimento) }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(conta.valor_total) }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(conta.valor_recebido) }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(conta.valor_saldo) }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="getStatusClass(conta.status)" class="px-2 py-1 rounded-full text-xs text-white">
              {{ conta.status_display }}
            </span>
          </td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <button @click="openModalForEdit(conta)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="openReceberModal(conta)" v-if="conta.status !== 'PAGA_RECEBIDA'" class="text-green-500 hover:text-green-400 font-bold mr-3">Receber</button>
            <button @click="deleteConta(conta.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhuma conta a receber encontrada.
    </div>

    <!-- Modal para Adicionar/Editar Conta a Receber -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-lg overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingConta ? 'Editar Conta a Receber' : 'Nova Conta a Receber' }}</h2>
        <form @submit.prevent="saveContaAReceber" class="space-y-4">
          <div>
            <label for="modal_descricao" class="block text-sm font-body text-gray-300">Descrição</label>
            <input type="text" id="modal_descricao" v-model="currentConta.descricao" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_valor_total" class="block text-sm font-body text-gray-300">Valor Total</label>
            <input type="number" step="0.01" id="modal_valor_total" v-model="currentConta.valor_total" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_data_vencimento" class="block text-sm font-body text-gray-300">Data de Vencimento</label>
            <input type="date" id="modal_data_vencimento" v-model="currentConta.data_vencimento" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
          </div>
          <div>
            <label for="modal_cliente" class="block text-sm font-body text-gray-300">Cliente</label>
            <select id="modal_cliente" v-model="currentConta.cliente" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option v-for="cli in clientesList" :key="cli.id" :value="cli.id">{{ cli.nome_razao_social }}</option>
            </select>
          </div>
          <div>
            <label for="modal_conta_contabil" class="block text-sm font-body text-gray-300">Conta Contábil (Receita)</label>
            <select id="modal_conta_contabil" v-model="currentConta.conta_contabil" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option v-for="pc in planoContasList" :key="pc.id" :value="pc.id">{{ pc.codigo }} - {{ pc.descricao }}</option>
            </select>
          </div>
          
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Conta</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal para Receber Conta -->
    <div v-if="isReceberModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-md overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">Receber Conta: {{ contaToReceber.descricao }}</h2>
        <form @submit.prevent="submitReceber" class="space-y-4">
          <div>
            <label for="receber_valor" class="block text-sm font-body text-gray-300">Valor a Receber</label>
            <input type="number" step="0.01" id="receber_valor" v-model="valorReceber" :max="contaToReceber.valor_saldo" required
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            <p class="text-xs text-gray-400">Saldo restante: {{ formatCurrency(contaToReceber.valor_saldo) }}</p>
          </div>
          <div>
            <label for="receber_conta_bancaria" class="block text-sm font-body text-gray-300">Conta Bancária</label>
            <select id="receber_conta_bancaria" v-model="contaBancariaReceberId" required
                    class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
              <option v-for="contaB in contasBancariasList" :key="contaB.id" :value="contaB.id">{{ contaB.descricao }} (Saldo: {{ formatCurrency(contaB.saldo_atual) }})</option>
            </select>
          </div>
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeReceberModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-green-500 text-white font-bold rounded-md hover:bg-green-600 transition-colors">
              <span v-if="uiStore.isLoading">Processando...</span>
              <span v-else>Confirmar Recebimento</span>
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
import FinanceiroService from '@/services/financeiro.service'
import CadastrosService from '@/services/cadastros.service' // Para buscar clientes

const uiStore = useUiStore()

const contasAReceber = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingConta = ref(false)
const currentConta = ref({
  id: null,
  descricao: '',
  valor_total: 0,
  data_vencimento: '',
  cliente: null,
  conta_contabil: null,
})

const clientesList = ref([])
const planoContasList = ref([])
const contasBancariasList = ref([])

// Receber Modal
const isReceberModalOpen = ref(false)
const contaToReceber = ref({})
const valorReceber = ref(0)
const contaBancariaReceberId = ref(null)


onMounted(() => {
  fetchContasAReceber()
  fetchClientesList()
  fetchPlanoContasList()
  fetchContasBancariasList()
})

async function fetchContasAReceber() {
  loading.value = true
  error.value = null
  try {
    const response = await FinanceiroService.getContasAReceber({ search: searchQuery.value })
    contasAReceber.value = response.results.map(conta => ({
      ...conta,
      status_display: getStatusDisplay(conta.status),
      data_vencimento: conta.data_vencimento,
    }))
  } catch (err) {
    error.value = 'Falha ao carregar contas a receber.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar contas a receber:', err)
  } finally {
    loading.value = false
  }
}

async function fetchClientesList() {
  try {
    const response = await CadastrosService.getClientes({ page_size: 1000, ativo: true })
    clientesList.value = response.results
  } catch (err) {
    console.error('Erro ao carregar lista de clientes:', err)
  }
}

async function fetchPlanoContasList() {
  try {
    const response = await FinanceiroService.getPlanosContas({ page_size: 1000, tipo_conta: 'RC', ativo: true }) // Busca apenas contas de receita
    planoContasList.value = response.results
  } catch (err) {
    console.error('Erro ao carregar plano de contas:', err)
  }
}

async function fetchContasBancariasList() {
  try {
    const response = await FinanceiroService.getContasBancarias({ page_size: 1000, ativo: true })
    contasBancariasList.value = response.results
  } catch (err) {
    console.error('Erro ao carregar contas bancárias:', err)
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'ABERTA': return 'bg-blue-500';
    case 'PARCIAL': return 'bg-yellow-500';
    case 'PAGA_RECEBIDA': return 'bg-green-500';
    case 'CANCELADA': return 'bg-gray-500';
    default: return 'bg-gray-500';
  }
}

function getStatusDisplay(status) {
  const choices = {
    'ABERTA': 'Aberta',
    'PARCIAL': 'Recebida Parcialmente',
    'PAGA_RECEBIDA': 'Recebida',
    'CANCELADA': 'Cancelada',
  }
  return choices[status] || status
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function formatDate(dateString) {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

function openModalForCreate() {
  editingConta.value = false
  currentConta.value = {
    id: null,
    descricao: '',
    valor_total: 0,
    data_vencimento: '',
    cliente: null,
    conta_contabil: null,
  }
  isModalOpen.value = true
}

function openModalForEdit(conta) {
  editingConta.value = true
  currentConta.value = { ...conta }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveContaAReceber() {
  uiStore.setLoading(true)
  try {
    const payload = {
      ...currentConta.value,
      cliente: currentConta.value.cliente,
      conta_contabil: currentConta.value.conta_contabil,
    }
    if (editingConta.value) {
      await FinanceiroService.updateContaAReceber(currentConta.value.id, payload)
      uiStore.showNotification('Conta a Receber atualizada com sucesso!', 'success')
    } else {
      await FinanceiroService.createContaAReceber(payload)
      uiStore.showNotification('Conta a Receber criada com sucesso!', 'success')
    }
    closeModal()
    fetchContasAReceber() // Recarregar a lista
  } catch (err) {
    uiStore.showNotification('Erro ao salvar conta a receber.', 'error')
    console.error('Erro ao salvar conta a receber:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteConta(id) {
  if (confirm('Tem certeza que deseja excluir esta conta a receber? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await FinanceiroService.deleteContaAReceber(id)
      uiStore.showNotification('Conta a Receber excluída com sucesso!', 'success')
      fetchContasAReceber()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir conta a receber.', 'error')
      console.error('Erro ao excluir conta a receber:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

function openReceberModal(conta) {
  contaToReceber.value = { ...conta }
  valorReceber.value = conta.valor_saldo
  contaBancariaReceberId.value = contasBancariasList.value.length > 0 ? contasBancariasList.value[0].id : null; // Seleciona a primeira por padrão
  isReceberModalOpen.value = true
}

function closeReceberModal() {
  isReceberModalOpen.value = false
}

async function submitReceber() {
  uiStore.setLoading(true)
  try {
    await FinanceiroService.receberContaAReceber(contaToReceber.value.id, {
      valor: valorReceber.value,
      conta_bancaria_id: contaBancariaReceberId.value
    })
    uiStore.showNotification('Recebimento registrado com sucesso!', 'success')
    closeReceberModal()
    fetchContasAReceber() // Recarregar a lista
  } catch (err) {
    uiStore.showNotification('Erro ao registrar recebimento.', 'error')
    console.error('Erro ao registrar recebimento.', err)
  } finally {
    uiStore.setLoading(false)
  }
}
</script>
