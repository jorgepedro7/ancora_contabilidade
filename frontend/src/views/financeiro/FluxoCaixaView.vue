<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Fluxo de Caixa</h1>

    <div class="mb-6 flex space-x-4 items-center">
      <div>
        <label for="data_inicio" class="block text-sm font-body text-gray-300">Data Início</label>
        <input type="date" id="data_inicio" v-model="dataInicio" @change="fetchFluxoCaixa"
               class="mt-1 block px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      </div>
      <div>
        <label for="data_fim" class="block text-sm font-body text-gray-300">Data Fim</label>
        <input type="date" id="data_fim" v-model="dataFim" @change="fetchFluxoCaixa"
               class="mt-1 block px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      </div>
    </div>

    <div v-if="loading" class="text-center text-gray-400">Carregando fluxo de caixa...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div v-if="fluxoCaixaData" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
        <h3 class="text-lg font-body text-ancora-gold mb-2">Total de Entradas</h3>
        <p class="text-2xl font-bold text-green-400">{{ formatCurrency(fluxoCaixaData.total_entradas) }}</p>
      </div>
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
        <h3 class="text-lg font-body text-ancora-gold mb-2">Total de Saídas</h3>
        <p class="text-2xl font-bold text-red-400">{{ formatCurrency(fluxoCaixaData.total_saidas) }}</p>
      </div>
      <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
        <h3 class="text-lg font-body text-ancora-gold mb-2">Fluxo de Caixa Líquido</h3>
        <p class="text-2xl font-bold" :class="fluxoCaixaData.fluxo_caixa_liquido >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ formatCurrency(fluxoCaixaData.fluxo_caixa_liquido) }}
        </p>
      </div>
    </div>

    <div v-if="fluxoCaixaData" class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
      <h3 class="text-lg font-body text-ancora-gold mb-2">Saldo Atual das Contas</h3>
      <p class="text-xl font-bold">{{ formatCurrency(fluxoCaixaData.saldo_final_contas_atuais) }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FinanceiroService from '@/services/financeiro.service'

const uiStore = useUiStore()

const dataInicio = ref('')
const dataFim = ref('')
const fluxoCaixaData = ref(null)
const loading = ref(false)
const error = ref(null)

onMounted(() => {
  // Define datas padrão (ex: último mês ou ano atual)
  const today = new Date()
  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  dataInicio.value = firstDayOfMonth.toISOString().split('T')[0]
  dataFim.value = today.toISOString().split('T')[0]
  
  fetchFluxoCaixa()
})

async function fetchFluxoCaixa() {
  if (!dataInicio.value || !dataFim.value) {
    uiStore.showNotification('Por favor, selecione as datas de início e fim.', 'warning')
    return
  }
  loading.value = true
  error.value = null
  fluxoCaixaData.value = null
  try {
    const response = await FinanceiroService.getFluxoCaixa(dataInicio.value, dataFim.value)
    fluxoCaixaData.value = response
  } catch (err) {
    error.value = 'Falha ao carregar fluxo de caixa.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar fluxo de caixa:', err)
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  if (value === null || value === undefined) return formatCurrency(0) // Garante que 0 é formatado
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}
</script>