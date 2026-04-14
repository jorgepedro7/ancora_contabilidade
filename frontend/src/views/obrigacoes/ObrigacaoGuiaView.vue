<template>
  <div class="p-4">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Calendário de Guias</h1>
        <p class="text-sm text-gray-400">Obrigações fiscais organizadas por mês de vencimento.</p>
      </div>
    </div>

    <!-- Filtro de tipo -->
    <div class="mb-4">
      <select
        v-model="filtroTipo"
        class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60"
      >
        <option value="">Todos os tipos</option>
        <option v-for="tipo in tiposObrigacao" :key="tipo.value" :value="tipo.value">
          {{ tipo.label }}
        </option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-400 text-sm py-8 text-center">Carregando...</div>

    <!-- Grupos de mês -->
    <div v-else class="space-y-3">
      <div
        v-for="mes in mesesVisiveis"
        :key="mes.chave"
        class="rounded-xl border border-ancora-gold/20 overflow-hidden"
      >
        <!-- Cabeçalho colapsável -->
        <button
          @click="toggleMes(mes.chave)"
          class="w-full flex items-center justify-between px-5 py-3 bg-ancora-navy hover:bg-ancora-navy/70 transition-colors"
          :class="{ 'border-b border-ancora-gold/20': expandedMonths.has(mes.chave) }"
        >
          <div class="flex items-center gap-3">
            <span class="font-display text-ancora-gold text-lg capitalize">{{ mes.label }}</span>
            <span class="text-xs text-gray-400">
              {{ contadorMes(mes).total }} obrigação(ões)
              <template v-if="contadorMes(mes).abertas > 0">
                — {{ contadorMes(mes).abertas }} aberta(s)
                — {{ formatCurrency(contadorMes(mes).totalAPagar) }} a pagar
              </template>
            </span>
          </div>
          <svg
            class="w-5 h-5 text-gray-400 transition-transform duration-200"
            :class="{ 'rotate-180': expandedMonths.has(mes.chave) }"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Conteúdo -->
        <div v-show="expandedMonths.has(mes.chave)">
          <div
            v-if="obrigacoesPorMes(mes).length === 0"
            class="px-5 py-6 text-gray-500 text-sm text-center"
          >
            Nenhuma obrigação neste mês.
          </div>
          <table v-else class="min-w-full divide-y divide-ancora-gold/10">
            <thead class="bg-ancora-black/30">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Tipo</th>
                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Descrição</th>
                <th class="px-4 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Vencimento</th>
                <th class="px-4 py-2 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Valor</th>
                <th class="px-4 py-2 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th class="px-4 py-2 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-ancora-gold/10">
              <tr
                v-for="ob in obrigacoesPorMes(mes)"
                :key="ob.id"
                class="hover:bg-ancora-navy/20 transition-colors"
              >
                <td class="px-4 py-3 text-sm text-gray-200 font-semibold whitespace-nowrap">
                  {{ ob.tipo_obrigacao }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-300">
                  {{ ob.descricao || '—' }}
                </td>
                <td
                  class="px-4 py-3 text-sm whitespace-nowrap"
                  :class="estaVencida(ob) ? 'text-red-400 font-semibold' : 'text-gray-300'"
                >
                  {{ formatDate(ob.data_vencimento) }}
                  <span v-if="estaVencida(ob)" class="ml-1 text-xs">(vencida)</span>
                </td>
                <td class="px-4 py-3 text-sm text-right font-mono text-gray-300">
                  {{ ob.valor ? formatCurrency(ob.valor) : '—' }}
                </td>
                <td class="px-4 py-3 text-center">
                  <span
                    :class="badgeClass(ob.status)"
                    class="px-2 py-0.5 text-xs rounded-full text-white"
                  >
                    {{ ob.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <button
                    v-if="['ABERTO', 'ATRASADO'].includes(ob.status)"
                    @click="abrirModalPagamento(ob)"
                    class="text-xs px-2 py-1 rounded border border-ancora-gold/40 text-ancora-gold hover:bg-ancora-gold/10 transition-colors whitespace-nowrap"
                  >
                    Registrar Pagamento
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal de pagamento -->
    <div
      v-if="modalAberto"
      class="fixed inset-0 z-50 flex items-center justify-center bg-ancora-black/70 p-4"
    >
      <div class="w-full max-w-md rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-1">Registrar Pagamento</h2>
        <p class="text-sm text-gray-400 mb-4">
          {{ obrigacaoSelecionada?.tipo_obrigacao }} —
          {{ formatDate(obrigacaoSelecionada?.data_vencimento) }}
        </p>
        <form @submit.prevent="confirmarPagamento" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Data de Pagamento *</label>
            <input
              type="date"
              v-model="formPagamento.data_envio_pagamento"
              required
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Link do Comprovante</label>
            <input
              type="url"
              v-model="formPagamento.link_documento"
              placeholder="https://..."
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Observações</label>
            <textarea
              v-model="formPagamento.observacoes"
              rows="2"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60"
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="fecharModal"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors text-sm"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvando"
              class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors text-sm disabled:opacity-50"
            >
              {{ salvando ? 'Salvando...' : 'Confirmar Pagamento' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import obrigacoesService from '@/services/obrigacoes.service'

const uiStore = useUiStore()

// --- Estado ---
const obrigacoes = ref([])
const loading = ref(false)
const filtroTipo = ref('')
const expandedMonths = ref(new Set())
const modalAberto = ref(false)
const obrigacaoSelecionada = ref(null)
const salvando = ref(false)
const formPagamento = ref({
  data_envio_pagamento: '',
  link_documento: '',
  observacoes: '',
})

// --- Constantes ---
const tiposObrigacao = [
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
]

// --- Computeds ---
// 7 meses: 3 passados + atual + 3 futuros
const mesesVisiveis = computed(() => {
  const hoje = new Date()
  const meses = []
  for (let delta = -3; delta <= 3; delta++) {
    const d = new Date(hoje.getFullYear(), hoje.getMonth() + delta, 1)
    const chave = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
    meses.push({ chave, label, ano: d.getFullYear(), mes: d.getMonth() + 1 })
  }
  return meses
})

const obrigacoesFiltradas = computed(() => {
  if (!filtroTipo.value) return obrigacoes.value
  return obrigacoes.value.filter(ob => ob.tipo_obrigacao === filtroTipo.value)
})

// --- Funções auxiliares ---
function obrigacoesPorMes(mes) {
  return obrigacoesFiltradas.value.filter(ob => {
    if (!ob.data_vencimento) return false
    const [ano, m] = ob.data_vencimento.split('-').map(Number)
    return ano === mes.ano && m === mes.mes
  })
}

function contadorMes(mes) {
  const lista = obrigacoesPorMes(mes)
  const abertas = lista.filter(ob => ['ABERTO', 'ATRASADO'].includes(ob.status))
  const totalAPagar = abertas.reduce((acc, ob) => acc + (parseFloat(ob.valor) || 0), 0)
  return { total: lista.length, abertas: abertas.length, totalAPagar }
}

function estaVencida(ob) {
  if (!ob.data_vencimento) return false
  const hoje = new Date().toISOString().split('T')[0]
  return ob.data_vencimento < hoje && !['PAGO', 'ENVIADO', 'CONCLUIDO'].includes(ob.status)
}

function badgeClass(status) {
  switch (status) {
    case 'ABERTO': return 'bg-blue-500'
    case 'ATRASADO': return 'bg-red-500'
    case 'PAGO':
    case 'ENVIADO':
    case 'CONCLUIDO': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

function toggleMes(chave) {
  const next = new Set(expandedMonths.value)
  if (next.has(chave)) next.delete(chave)
  else next.add(chave)
  expandedMonths.value = next
}

function formatDate(dateString) {
  if (!dateString) return '—'
  const [ano, mes, dia] = dateString.split('-')
  return `${dia}/${mes}/${ano}`
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0)
}

// --- Modal ---
function abrirModalPagamento(ob) {
  obrigacaoSelecionada.value = ob
  formPagamento.value = {
    data_envio_pagamento: new Date().toISOString().split('T')[0],
    link_documento: ob.link_documento || '',
    observacoes: ob.observacoes || '',
  }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  obrigacaoSelecionada.value = null
}

async function confirmarPagamento() {
  salvando.value = true
  try {
    await obrigacoesService.updateObrigacao(obrigacaoSelecionada.value.id, {
      status: 'PAGO',
      data_envio_pagamento: formPagamento.value.data_envio_pagamento,
      link_documento: formPagamento.value.link_documento || null,
      observacoes: formPagamento.value.observacoes || null,
    })
    uiStore.showNotification('Pagamento registrado!', 'success')
    fecharModal()
    await fetchObrigacoes()
  } catch {
    uiStore.showNotification('Erro ao registrar pagamento.', 'error')
  } finally {
    salvando.value = false
  }
}

// --- Dados ---
async function fetchObrigacoes() {
  loading.value = true
  try {
    const data = await obrigacoesService.getObrigacoes()
    obrigacoes.value = data.results ?? data
  } catch {
    uiStore.showNotification('Erro ao carregar guias.', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchObrigacoes()
  // Abre o mês atual por padrão
  const hoje = new Date()
  const chaveAtual = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`
  expandedMonths.value = new Set([chaveAtual])
})
</script>
