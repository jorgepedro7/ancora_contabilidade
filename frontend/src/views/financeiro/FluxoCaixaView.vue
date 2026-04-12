<template>
  <div class="p-4">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Fluxo de Caixa</h1>
        <p class="text-sm text-gray-400">Movimentações financeiras da empresa ativa.</p>
      </div>
      <button @click="openLancamentoModal"
              class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        + Lançamento Manual
      </button>
    </div>

    <!-- Filtros de período -->
    <div class="mb-6 flex flex-wrap gap-4 items-end">
      <div>
        <label class="block text-sm text-gray-300 mb-1">Data Início</label>
        <input type="date" v-model="dataInicio" @change="fetchAll"
               class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
      </div>
      <div>
        <label class="block text-sm text-gray-300 mb-1">Data Fim</label>
        <input type="date" v-model="dataFim" @change="fetchAll"
               class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
      </div>
      <select v-model="filterTipo" @change="fetchMovimentacoes"
              class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm self-end">
        <option value="">Todos os tipos</option>
        <option value="E">Entradas</option>
        <option value="S">Saídas</option>
        <option value="T">Transferências</option>
      </select>
    </div>

    <!-- KPIs -->
    <div v-if="fluxo" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20">
        <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">Entradas no período</p>
        <p class="text-2xl font-bold text-green-400">{{ formatCurrency(fluxo.total_entradas) }}</p>
      </div>
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20">
        <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">Saídas no período</p>
        <p class="text-2xl font-bold text-red-400">{{ formatCurrency(fluxo.total_saidas) }}</p>
      </div>
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20">
        <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">Fluxo Líquido</p>
        <p class="text-2xl font-bold" :class="fluxo.fluxo_caixa_liquido >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ formatCurrency(fluxo.fluxo_caixa_liquido) }}
        </p>
      </div>
    </div>

    <!-- Saldos por conta bancária -->
    <div class="mb-6">
      <h2 class="text-lg font-display text-ancora-gold mb-3">Saldos das Contas</h2>
      <div v-if="loadingContas" class="text-gray-400 text-sm">Carregando...</div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div v-for="cb in contasBancarias" :key="cb.id"
             class="bg-ancora-navy/30 border border-ancora-gold/20 p-4 rounded-lg">
          <p class="text-xs uppercase tracking-wide text-gray-500">{{ tipoContaLabel(cb.tipo_conta) }}</p>
          <p class="font-semibold text-white mt-0.5">{{ cb.descricao }}</p>
          <p class="text-xl font-bold mt-1" :class="cb.saldo_atual >= 0 ? 'text-ancora-gold' : 'text-red-400'">
            {{ formatCurrency(cb.saldo_atual) }}
          </p>
        </div>
        <div v-if="contasBancarias.length > 1"
             class="bg-ancora-navy/10 border border-ancora-gold/10 p-4 rounded-lg">
          <p class="text-xs uppercase tracking-wide text-gray-500">Total Geral</p>
          <p class="font-semibold text-gray-300 mt-0.5">Todas as contas</p>
          <p class="text-xl font-bold mt-1" :class="saldoTotal >= 0 ? 'text-ancora-gold' : 'text-red-400'">
            {{ formatCurrency(saldoTotal) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Movimentações -->
    <div>
      <h2 class="text-lg font-display text-ancora-gold mb-3">Movimentações do Período</h2>
      <div v-if="loadingMov" class="text-gray-400 text-sm">Carregando movimentações...</div>
      <div v-else-if="movimentacoes.length > 0" class="overflow-x-auto rounded-lg shadow-md">
        <table class="min-w-full bg-ancora-black/50 text-white">
          <thead>
            <tr class="bg-ancora-navy text-ancora-gold uppercase text-xs leading-normal">
              <th class="py-2 px-4 text-left">Data</th>
              <th class="py-2 px-4 text-left">Tipo</th>
              <th class="py-2 px-4 text-left">Descrição</th>
              <th class="py-2 px-4 text-left">Conta Bancária</th>
              <th class="py-2 px-4 text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="text-sm text-gray-300">
            <tr v-for="mov in movimentacoes" :key="mov.id"
                class="border-b border-ancora-navy hover:bg-ancora-black/70">
              <td class="py-2 px-4">{{ formatDate(mov.data_movimentacao) }}</td>
              <td class="py-2 px-4">
                <span :class="tipoMovClass(mov.tipo_movimentacao)"
                      class="px-2 py-0.5 rounded text-xs font-semibold text-white">
                  {{ tipoMovLabel(mov.tipo_movimentacao) }}
                </span>
              </td>
              <td class="py-2 px-4">{{ mov.descricao || '-' }}</td>
              <td class="py-2 px-4">{{ mov.conta_bancaria_detail?.descricao }}</td>
              <td class="py-2 px-4 text-right font-mono font-bold"
                  :class="mov.tipo_movimentacao === 'E' ? 'text-green-400' : mov.tipo_movimentacao === 'S' ? 'text-red-400' : 'text-yellow-400'">
                {{ mov.tipo_movimentacao === 'S' ? '-' : '' }}{{ formatCurrency(mov.valor) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center text-gray-400 py-6 text-sm">
        Nenhuma movimentação no período selecionado.
      </div>
    </div>

    <!-- Modal Lançamento Manual -->
    <div v-if="lancamentoModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-ancora-gold/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-ancora-gold mb-4">Lançamento Manual</h3>
        <form @submit.prevent="salvarLancamento" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Tipo *</label>
            <select v-model="lancamentoForm.tipo_movimentacao" required
                    class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
              <option value="E">Entrada</option>
              <option value="S">Saída</option>
              <option value="T">Transferência</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Conta Bancária *</label>
            <select v-model="lancamentoForm.conta_bancaria" required
                    class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
              <option :value="null" disabled>Selecione...</option>
              <option v-for="cb in contasBancarias" :key="cb.id" :value="cb.id">
                {{ cb.descricao }} ({{ formatCurrency(cb.saldo_atual) }})
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Valor (R$) *</label>
            <input type="number" step="0.01" min="0.01" v-model="lancamentoForm.valor" required
                   class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Data *</label>
            <input type="date" v-model="lancamentoForm.data_movimentacao" required
                   class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Descrição</label>
            <input type="text" v-model="lancamentoForm.descricao"
                   class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="lancamentoModal.open = false"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 disabled:opacity-50">
              {{ saving ? 'Salvando...' : 'Lançar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FinanceiroService from '@/services/financeiro.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()

// Datas — padrão: mês atual
const today = new Date()
const dataInicio = ref(new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0])
const dataFim = ref(today.toISOString().split('T')[0])
const filterTipo = ref('')

const fluxo = ref(null)
const contasBancarias = ref([])
const movimentacoes = ref([])
const loadingContas = ref(false)
const loadingMov = ref(false)
const saving = ref(false)

const saldoTotal = computed(() => contasBancarias.value.reduce((acc, cb) => acc + Number(cb.saldo_atual), 0))

// Modal de lançamento manual
const lancamentoModal = reactive({ open: false })
const emptyLancamento = () => ({
  tipo_movimentacao: 'E',
  conta_bancaria: null,
  valor: 0,
  data_movimentacao: today.toISOString().split('T')[0],
  descricao: '',
})
const lancamentoForm = reactive(emptyLancamento())

onMounted(() => fetchAll())

async function fetchAll() {
  fetchFluxo()
  fetchContasBancarias()
  fetchMovimentacoes()
}

async function fetchFluxo() {
  if (!dataInicio.value || !dataFim.value) return
  try {
    fluxo.value = await FinanceiroService.getFluxoCaixa(dataInicio.value, dataFim.value)
  } catch { /* silencioso */ }
}

async function fetchContasBancarias() {
  loadingContas.value = true
  try {
    const r = await FinanceiroService.getContasBancarias({ page_size: 100 })
    contasBancarias.value = r.results
  } catch { /* silencioso */ }
  finally { loadingContas.value = false }
}

async function fetchMovimentacoes() {
  loadingMov.value = true
  try {
    const params = { page_size: 100 }
    if (dataInicio.value) params.data_movimentacao__gte = dataInicio.value
    if (dataFim.value) params.data_movimentacao__lte = dataFim.value
    if (filterTipo.value) params.tipo_movimentacao = filterTipo.value
    const r = await FinanceiroService.getMovimentacoesFinanceiras(params)
    movimentacoes.value = r.results
  } catch { /* silencioso */ }
  finally { loadingMov.value = false }
}

function openLancamentoModal() {
  Object.assign(lancamentoForm, emptyLancamento())
  if (contasBancarias.value.length > 0) lancamentoForm.conta_bancaria = contasBancarias.value[0].id
  lancamentoModal.open = true
}

async function salvarLancamento() {
  saving.value = true
  try {
    await FinanceiroService.createMovimentacaoFinanceira({ ...lancamentoForm })
    uiStore.showNotification('Lançamento registrado!', 'success')
    lancamentoModal.open = false
    await fetchAll()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao registrar lançamento.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

function tipoContaLabel(t) {
  return { CC: 'Conta Corrente', CP: 'Conta Poupança', APL: 'Aplicação', CX: 'Caixa' }[t] || t
}

function tipoMovLabel(t) {
  return { E: 'Entrada', S: 'Saída', T: 'Transferência' }[t] || t
}

function tipoMovClass(t) {
  return { E: 'bg-green-700', S: 'bg-red-700', T: 'bg-yellow-700' }[t] || 'bg-gray-600'
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
