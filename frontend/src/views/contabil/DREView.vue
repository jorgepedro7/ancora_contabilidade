<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Demonstrativo de Resultado do Exercício (DRE)</h1>

    <div class="mb-6 flex space-x-4 items-center">
      <div>
        <label for="data_inicio" class="block text-sm font-body text-gray-300">Data Início</label>
        <input type="date" id="data_inicio" v-model="dataInicio" @change="fetchDRE"
               class="mt-1 block px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      </div>
      <div>
        <label for="data_fim" class="block text-sm font-body text-gray-300">Data Fim</label>
        <input type="date" id="data_fim" v-model="dataFim" @change="fetchDRE"
               class="mt-1 block px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      </div>
    </div>

    <div v-if="loading" class="text-center text-gray-400">Carregando DRE...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div v-if="dreData" class="bg-ancora-black/50 p-6 rounded-lg shadow-md border border-ancora-gold/30">
      <h2 class="text-2xl font-body text-ancora-gold mb-4">Período: {{ formatDate(dreData.periodo_inicio) }} a {{ formatDate(dreData.periodo_fim) }}</h2>
      
      <div class="grid grid-cols-1 gap-4 text-lg">
        <div class="flex justify-between items-center py-2 border-b border-ancora-navy">
          <span class="font-bold">Receita Operacional Bruta:</span>
          <span class="font-bold text-green-400">{{ formatCurrency(dreData.total_receitas) }}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-b border-ancora-navy">
          <span class="font-bold">Custos e Despesas Operacionais:</span>
          <span class="font-bold text-red-400">{{ formatCurrency(dreData.total_despesas) }}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-t border-ancora-gold mt-4">
          <span class="text-xl font-bold">Resultado Líquido:</span>
          <span class="text-2xl font-bold" :class="dreData.resultado_liquido >= 0 ? 'text-green-400' : 'text-red-400'">
            {{ formatCurrency(dreData.resultado_liquido) }}
          </span>
        </div>
      </div>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum dado de DRE para o período selecionado.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import ContabilService from '@/services/contabil.service'

const uiStore = useUiStore()

const dataInicio = ref('')
const dataFim = ref('')
const dreData = ref(null)
const loading = ref(false)
const error = ref(null)

onMounted(() => {
  const today = new Date()
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1) // Primeiro dia do ano
  dataInicio.value = firstDayOfYear.toISOString().split('T')[0]
  dataFim.value = today.toISOString().split('T')[0]
  
  fetchDRE()
})

async function fetchDRE() {
  if (!dataInicio.value || !dataFim.value) {
    uiStore.showNotification('Por favor, selecione as datas de início e fim.', 'warning')
    return
  }
  loading.value = true
  error.value = null
  dreData.value = null
  try {
    const response = await ContabilService.getDRE(dataInicio.value, dataFim.value)
    dreData.value = response
  } catch (err) {
    error.value = 'Falha ao carregar DRE.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar DRE:', err)
  } finally {
    loading.value = false
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
</script>