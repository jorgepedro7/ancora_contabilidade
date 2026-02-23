<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Dashboard</h1>
    
    <div v-if="authStore.user">
      <p class="text-lg mb-4">Bem-vindo, <span class="font-bold">{{ authStore.user.nome }}</span>!</p>
      
      <div v-if="!empresaStore.activeEmpresa" class="mb-6 p-4 border border-ancora-gold/30 rounded-lg bg-ancora-navy/50">
        <h2 class="text-xl font-body text-ancora-gold mb-2">Selecione uma Empresa para Continuar:</h2>
        <p v-if="loading">Carregando empresas...</p>
        <p v-if="error" class="text-red-500">{{ error }}</p>
        
        <div v-if="empresas.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="empresa in empresas"
            :key="empresa.id"
            @click="selectEmpresa(empresa.id)"
            class="p-4 border border-ancora-gold/30 rounded-lg bg-ancora-black/50 hover:bg-ancora-navy cursor-pointer transition-colors"
          >
            <h3 class="font-body font-bold text-ancora-gold">{{ empresa.nome_fantasia || empresa.razao_social }}</h3>
            <p class="text-sm text-gray-400">CNPJ: {{ empresa.cnpj }}</p>
            <p class="text-xs text-gray-500">Regime: {{ empresa.regime_tributario }}</p>
          </div>
        </div>
        <p v-else-if="!loading && !error" class="text-center text-gray-400">Nenhuma empresa disponível. Entre em contato com o administrador.</p>
      </div>

      <div v-else>
        <div class="mb-6 p-4 border border-ancora-gold/30 rounded-lg bg-ancora-navy/50 flex justify-between items-center">
          <div>
            <h2 class="text-xl font-body text-ancora-gold mb-2">Empresa Ativa:</h2>
            <p class="text-lg">{{ empresaStore.activeEmpresa.nome_fantasia || empresaStore.activeEmpresa.razao_social }}</p>
            <p class="text-sm text-gray-400">CNPJ: {{ formatCnpj(empresaStore.activeEmpresa.cnpj) }}</p>
          </div>
          <button @click="empresaStore.clearActiveEmpresa" class="px-4 py-2 bg-red-600 rounded-md hover:bg-red-700">Mudar Empresa</button>
        </div>

        <!-- Cards de Resumo -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">NF-e Mês</h3>
            <p class="text-2xl font-bold">{{ dashboardData.nfe_emitidas_mes || 0 }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">Contas a Pagar (5d)</h3>
            <p class="text-2xl font-bold text-red-400">{{ formatCurrency(dashboardData.contas_pagar_5d) }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">Contas a Receber (5d)</h3>
            <p class="text-2xl font-bold text-green-400">{{ formatCurrency(dashboardData.contas_receber_5d) }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">Saldo Total Contas</h3>
            <p class="text-2xl font-bold">{{ formatCurrency(dashboardData.saldo_total_contas) }}</p>
          </div>
        </div>

        <!-- Gráficos (Placeholder por enquanto) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">Faturamento (últimos 12 meses)</h3>
            <div class="h-64 flex items-center justify-center text-gray-400">Gráfico de Faturamento aqui (Chart.js/Recharts)</div>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/30 shadow-md">
            <h3 class="text-lg font-body text-ancora-gold mb-2">Despesas por Categoria</h3>
            <div class="h-64 flex items-center justify-center text-gray-400">Gráfico de Despesas aqui (Chart.js/Recharts)</div>
          </div>
        </div>

      </div>
    </div>
    <div v-else>
      <p>Faça login para ver o dashboard.</p>
    </div>
  </div>
</template>

<script setup>
import EmpresaService from '@/services/empresas.service'
import FiscalService from '@/services/fiscal.service'
import FinanceiroService from '@/services/financeiro.service'
import { useAuthStore } from '@/stores/auth'
import { useEmpresaStore } from '@/stores/empresa'
import { ref, onMounted, watch } from 'vue'

const authStore = useAuthStore()
const empresaStore = useEmpresaStore()

const empresas = ref([])
const loading = ref(false)
const error = ref(null)
const dashboardData = ref({
  nfe_emitidas_mes: 0,
  contas_pagar_5d: 0,
  contas_receber_5d: 0,
  saldo_total_contas: 0,
})

onMounted(async () => {
  if (!empresaStore.activeEmpresa) {
    await fetchEmpresas()
  } else {
    await fetchDashboardData()
  }
})

// Watch for changes in activeEmpresa to re-fetch dashboard data
watch(() => empresaStore.activeEmpresa, async (newVal, oldVal) => {
  if (newVal) {
    await fetchDashboardData()
  } else if (oldVal && !newVal) {
    // Optionally clear dashboard data if no company is selected
    Object.keys(dashboardData.value).forEach(key => dashboardData.value[key] = 0);
  }
})

async function fetchEmpresas() {
  loading.value = true
  error.value = null
  try {
    const response = await EmpresaService.getEmpresas()
    empresas.value = response.results.map(emp => ({
      ...emp,
      regime_tributario_display: getRegimeTributarioDisplay(emp.regime_tributario)
    }))
  } catch (err) {
    error.value = 'Falha ao carregar empresas.'
    console.error('Erro ao carregar empresas:', err)
  } finally {
    loading.value = false
  }
}

async function selectEmpresa(empresaId) {
  loading.value = true
  error.value = null
  try {
    await empresaStore.selectEmpresa(empresaId)
    // A interface (Sidebar, Dashboard) atualizará automaticamente via reatividade do Pinia
  } catch (err) {
    error.value = 'Erro ao selecionar empresa. Verifique suas permissões.'
    console.error('Erro detalhado na seleção:', err)
  } finally {
    loading.value = false
  }
}

async function fetchDashboardData() {
  if (!empresaStore.activeEmpresa) {
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    // Fetch NF-e count for the month
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
    const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().split('T')[0];
    const nfeResponse = await FiscalService.getNotasFiscais({ 
      data_emissao_after: firstDayOfMonth, 
      data_emissao_before: lastDayOfMonth 
    });
    dashboardData.value.nfe_emitidas_mes = nfeResponse.count;

    // Fetch accounts payable due in 5 days
    const contasPagarResponse = await FinanceiroService.getContasVencendoHoje();
    const contasPagar = contasPagarResponse?.contas_a_pagar_hoje || [];
    dashboardData.value.contas_pagar_5d = contasPagar
      .reduce((sum, conta) => sum + parseFloat(conta.valor_saldo || 0), 0);

    // Fetch accounts receivable due in 5 days
    const contasReceberResponse = await FinanceiroService.getContasVencendoHoje();
    const contasReceber = contasReceberResponse?.contas_a_receber_hoje || [];
    dashboardData.value.contas_receber_5d = contasReceber
      .reduce((sum, conta) => sum + parseFloat(conta.valor_saldo || 0), 0);
    
    // Fetch total balance across all bank accounts
    const contasBancariasResponse = await FinanceiroService.getContasBancarias();
    const contasBancarias = contasBancariasResponse?.results || [];
    dashboardData.value.saldo_total_contas = contasBancarias
      .reduce((sum, conta) => sum + parseFloat(conta.saldo_atual || 0), 0);

  } catch (err) {
    error.value = 'Falha ao carregar dados do dashboard.'
    console.error('Erro ao carregar dashboard:', err)
  } finally {
    loading.value = false;
  }
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function getRegimeTributarioDisplay(regime) {
  const choices = {
    'SN': 'Simples Nacional',
    'LP': 'Lucro Presumido',
    'LR': 'Lucro Real',
  }
  return choices[regime] || regime
}
</script>