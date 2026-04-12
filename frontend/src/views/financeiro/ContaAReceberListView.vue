<template>
  <div class="p-4">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Contas a Receber</h1>
        <p class="text-sm text-gray-400">Créditos a receber da empresa ativa.</p>
      </div>
      <button @click="openCreateModal"
              class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        + Nova Conta
      </button>
    </div>

    <!-- Filtros -->
    <div class="mb-4 flex flex-wrap gap-3">
      <input type="text" v-model="searchQuery" @input="fetchContas"
             placeholder="Buscar por descrição ou cliente..."
             class="flex-1 min-w-48 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
      <select v-model="filterStatus" @change="fetchContas"
              class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
        <option value="">Todos</option>
        <option value="ABERTA">Aberta</option>
        <option value="PARCIAL">Parcial</option>
        <option value="PAGA_RECEBIDA">Recebida</option>
        <option value="CANCELADA">Cancelada</option>
      </select>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-6">Carregando...</div>

    <div v-if="contas.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
          <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
            <th class="py-3 px-4 text-left">Descrição</th>
            <th class="py-3 px-4 text-left">Cliente</th>
            <th class="py-3 px-4 text-left">Vencimento</th>
            <th class="py-3 px-4 text-left">Parcela</th>
            <th class="py-3 px-4 text-right">Total</th>
            <th class="py-3 px-4 text-right">Recebido</th>
            <th class="py-3 px-4 text-right">Saldo</th>
            <th class="py-3 px-4 text-left">Status</th>
            <th class="py-3 px-4 text-center">Ações</th>
          </tr>
        </thead>
        <tbody class="text-sm font-body">
          <tr v-for="conta in contas" :key="conta.id"
              :class="conta.esta_vencida ? 'bg-red-900/20 border-b border-red-900/30' : 'border-b border-ancora-navy hover:bg-ancora-black/70'"
              class="text-gray-300">
            <td class="py-3 px-4 whitespace-nowrap">
              <div>{{ conta.descricao }}</div>
              <div v-if="conta.esta_vencida" class="text-xs text-red-400 font-semibold">VENCIDA</div>
            </td>
            <td class="py-3 px-4">{{ conta.cliente_detail?.nome_razao_social }}</td>
            <td class="py-3 px-4" :class="conta.esta_vencida ? 'text-red-400' : ''">{{ formatDate(conta.data_vencimento) }}</td>
            <td class="py-3 px-4 text-center text-xs">{{ conta.parcela_atual }}/{{ conta.total_parcelas }}</td>
            <td class="py-3 px-4 text-right font-mono">{{ formatCurrency(conta.valor_total) }}</td>
            <td class="py-3 px-4 text-right font-mono">{{ formatCurrency(conta.valor_recebido) }}</td>
            <td class="py-3 px-4 text-right font-mono font-bold">{{ formatCurrency(conta.valor_saldo) }}</td>
            <td class="py-3 px-4">
              <span :class="statusClass(conta.status)" class="px-2 py-0.5 rounded-full text-xs font-semibold text-white">
                {{ statusLabel(conta.status) }}
              </span>
            </td>
            <td class="py-3 px-4 text-center whitespace-nowrap">
              <button @click="openEditModal(conta)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-2">Editar</button>
              <button v-if="conta.status !== 'PAGA_RECEBIDA' && conta.status !== 'CANCELADA'"
                      @click="openReceberModal(conta)"
                      class="text-green-400 hover:text-green-300 font-bold mr-2">Receber</button>
              <button @click="openDeleteModal(conta)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading" class="text-center text-gray-400 mt-8">Nenhuma conta a receber encontrada.</div>

    <!-- Modal Criar/Editar -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-6 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-5">{{ editingConta ? 'Editar Conta a Receber' : 'Nova Conta a Receber' }}</h2>
        <form @submit.prevent="saveConta" class="space-y-4">

          <p class="text-xs uppercase tracking-wide text-gray-500">Dados Principais</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Descrição *</label>
              <input type="text" v-model="form.descricao" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Cliente *</label>
              <select v-model="form.cliente" required
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option :value="null" disabled>Selecione...</option>
                <option v-for="c in clientesList" :key="c.id" :value="c.id">{{ c.nome_razao_social }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Conta Contábil (Receita) *</label>
              <select v-model="form.conta_contabil" required
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option :value="null" disabled>Selecione...</option>
                <option v-for="pc in planoContasList" :key="pc.id" :value="pc.id">{{ pc.codigo }} - {{ pc.descricao }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Valor Total (R$) *</label>
              <input type="number" step="0.01" min="0.01" v-model="form.valor_total" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Data de Vencimento *</label>
              <input type="date" v-model="form.data_vencimento" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Parcelamento</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Parcela Atual</label>
              <input type="number" min="1" v-model="form.parcela_atual"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Total de Parcelas</label>
              <input type="number" min="1" v-model="form.total_parcelas"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Encargos</p>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Juros (R$)</label>
              <input type="number" step="0.01" min="0" v-model="form.juros"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Multa (R$)</label>
              <input type="number" step="0.01" min="0" v-model="form.multa"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Desconto (R$)</label>
              <input type="number" step="0.01" min="0" v-model="form.desconto"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <div>
            <label class="block text-sm text-gray-300 mb-1">Observações</label>
            <textarea v-model="form.observacoes" rows="2"
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm"></textarea>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="closeModal" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 disabled:opacity-50">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Receber -->
    <div v-if="receberModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-ancora-black/70 p-4">
      <div class="w-full max-w-md rounded-lg border border-green-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-green-400 mb-1">Registrar Recebimento</h3>
        <p class="text-sm text-gray-400 mb-4">{{ receberModal.descricao }}</p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Valor a Receber (R$) *</label>
            <input type="number" step="0.01" min="0.01" :max="receberModal.saldo" v-model="receberModal.valor"
                   class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            <p class="text-xs text-gray-500 mt-1">Saldo: {{ formatCurrency(receberModal.saldo) }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Conta Bancária *</label>
            <select v-model="receberModal.contaBancariaId"
                    class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
              <option :value="null" disabled>Selecione...</option>
              <option v-for="cb in contasBancariasList" :key="cb.id" :value="cb.id">
                {{ cb.descricao }} ({{ formatCurrency(cb.saldo_atual) }})
              </option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="receberModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarReceber" :disabled="saving || !receberModal.contaBancariaId"
                  class="px-4 py-2 bg-green-600 text-white font-bold rounded-md hover:bg-green-700 disabled:opacity-50">
            {{ saving ? 'Processando...' : 'Confirmar Recebimento' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Excluir -->
    <div v-if="deleteModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-red-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-red-400 mb-2">Confirmar Exclusão</h3>
        <p class="text-sm text-gray-300 mb-4">
          Excluir a conta <span class="font-bold text-white">{{ deleteModal.descricao }}</span>? (soft delete)
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deleteModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarDelete" :disabled="saving"
                  class="px-4 py-2 bg-red-600 text-white font-bold rounded-md hover:bg-red-700 disabled:opacity-50">
            {{ saving ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FinanceiroService from '@/services/financeiro.service'
import CadastrosService from '@/services/cadastros.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()

const contas = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')

const clientesList = ref([])
const planoContasList = ref([])
const contasBancariasList = ref([])

const isModalOpen = ref(false)
const editingConta = ref(false)

const emptyForm = () => ({
  id: null,
  descricao: '',
  valor_total: 0,
  data_vencimento: '',
  cliente: null,
  conta_contabil: null,
  parcela_atual: 1,
  total_parcelas: 1,
  juros: 0,
  multa: 0,
  desconto: 0,
  observacoes: '',
})

const form = reactive(emptyForm())

const receberModal = reactive({ open: false, id: null, descricao: '', saldo: 0, valor: 0, contaBancariaId: null })
const deleteModal = reactive({ open: false, id: null, descricao: '' })

onMounted(() => {
  fetchContas()
  loadClientes()
  loadPlanoContas()
  loadContasBancarias()
})

async function fetchContas() {
  loading.value = true
  try {
    const params = { search: searchQuery.value }
    if (filterStatus.value) params.status = filterStatus.value
    const response = await FinanceiroService.getContasAReceber(params)
    contas.value = response.results
  } catch {
    uiStore.showNotification('Falha ao carregar contas a receber.', 'error')
  } finally {
    loading.value = false
  }
}

async function loadClientes() {
  try {
    const r = await CadastrosService.getClientes({ page_size: 500 })
    clientesList.value = r.results
  } catch { /* silencioso */ }
}

async function loadPlanoContas() {
  try {
    const r = await FinanceiroService.getPlanosContas({ page_size: 500, tipo_conta: 'RC' })
    planoContasList.value = r.results
  } catch { /* silencioso */ }
}

async function loadContasBancarias() {
  try {
    const r = await FinanceiroService.getContasBancarias({ page_size: 100 })
    contasBancariasList.value = r.results
  } catch { /* silencioso */ }
}

function openCreateModal() {
  editingConta.value = false
  Object.assign(form, emptyForm())
  isModalOpen.value = true
}

function openEditModal(conta) {
  editingConta.value = true
  Object.assign(form, emptyForm(), {
    id: conta.id,
    descricao: conta.descricao,
    valor_total: conta.valor_total,
    data_vencimento: conta.data_vencimento,
    cliente: conta.cliente,
    conta_contabil: conta.conta_contabil,
    parcela_atual: conta.parcela_atual,
    total_parcelas: conta.total_parcelas,
    juros: conta.juros,
    multa: conta.multa,
    desconto: conta.desconto,
    observacoes: conta.observacoes || '',
  })
  isModalOpen.value = true
}

function closeModal() { isModalOpen.value = false }

async function saveConta() {
  saving.value = true
  try {
    if (editingConta.value) {
      await FinanceiroService.updateContaAReceber(form.id, { ...form })
      uiStore.showNotification('Conta atualizada!', 'success')
    } else {
      await FinanceiroService.createContaAReceber({ ...form })
      uiStore.showNotification('Conta criada!', 'success')
    }
    closeModal()
    await fetchContas()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar conta.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

function openReceberModal(conta) {
  receberModal.open = true
  receberModal.id = conta.id
  receberModal.descricao = conta.descricao
  receberModal.saldo = Number(conta.valor_saldo)
  receberModal.valor = Number(conta.valor_saldo)
  receberModal.contaBancariaId = contasBancariasList.value[0]?.id || null
}

async function confirmarReceber() {
  saving.value = true
  try {
    await FinanceiroService.receberContaAReceber(receberModal.id, {
      valor: receberModal.valor,
      conta_bancaria_id: receberModal.contaBancariaId,
    })
    uiStore.showNotification('Recebimento registrado!', 'success')
    receberModal.open = false
    await fetchContas()
    await loadContasBancarias()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao registrar recebimento.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

function openDeleteModal(conta) {
  deleteModal.open = true
  deleteModal.id = conta.id
  deleteModal.descricao = conta.descricao
}

async function confirmarDelete() {
  saving.value = true
  try {
    await FinanceiroService.deleteContaAReceber(deleteModal.id)
    uiStore.showNotification('Conta excluída!', 'success')
    deleteModal.open = false
    await fetchContas()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao excluir.'), 'error')
  } finally {
    saving.value = false
  }
}

function statusClass(s) {
  return { ABERTA: 'bg-blue-600', PARCIAL: 'bg-yellow-600', PAGA_RECEBIDA: 'bg-green-600', CANCELADA: 'bg-gray-500' }[s] || 'bg-gray-500'
}

function statusLabel(s) {
  return { ABERTA: 'Aberta', PARCIAL: 'Parcial', PAGA_RECEBIDA: 'Recebida', CANCELADA: 'Cancelada' }[s] || s
}

function formatCurrency(v) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0)
}

function formatDate(d) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}
</script>
