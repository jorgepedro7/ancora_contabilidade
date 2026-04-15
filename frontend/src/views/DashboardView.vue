<template>
  <div class="p-4 space-y-6">
    <section>
      <h1 class="text-3xl font-display text-ancora-gold mb-2">Dashboard</h1>
      <p class="text-gray-400">
        Escritório único, operação segmentada por empresa-cliente. Tudo abaixo reflete a empresa ativa no momento.
      </p>
    </section>

    <section v-if="authStore.user" class="space-y-6">
      <div class="bg-ancora-navy/40 border border-ancora-gold/20 rounded-lg p-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Empresa-cliente ativa</p>
          <h2 class="text-2xl font-display text-white">
            {{ empresaStore.activeEmpresa?.nome_fantasia || empresaStore.activeEmpresa?.razao_social || 'Nenhuma empresa selecionada' }}
          </h2>
          <p v-if="empresaStore.activeEmpresa" class="text-sm text-gray-400 mt-2">
            CNPJ: {{ formatCnpj(empresaStore.activeEmpresa.cnpj) }}
          </p>
          <p class="text-sm text-gray-400 mt-3">
            Bem-vindo, <span class="font-semibold text-white">{{ authStore.user.nome }}</span>.
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <router-link
            v-if="authStore.user.perfil_empresa !== 'CLIENTE'"
            to="/empresas"
            class="px-4 py-2 border border-ancora-gold/40 rounded-md text-ancora-gold hover:bg-ancora-gold/10 transition-colors"
          >
            Ver carteira de empresas
          </router-link>
          <router-link
            v-if="empresaStore.activeEmpresa && authStore.user.perfil_empresa !== 'CLIENTE'"
            to="/empresa/configuracoes"
            class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80"
          >
            Configurar empresa ativa
          </router-link>
          <router-link
            v-if="empresaStore.activeEmpresa && authStore.user.perfil_empresa === 'CLIENTE' && portalSlug"
            :to="`/area_cliente/${portalSlug}`"
            class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80"
          >
            Acessar Portal de Envios
          </router-link>
          <p
            v-else-if="empresaStore.activeEmpresa && authStore.user.perfil_empresa === 'CLIENTE' && !portalSlug"
            class="text-sm text-gray-400"
          >
            Nenhum portal de envios configurado. Contate o escritório.
          </p>
        </div>
      </div>

      <div v-if="empresaStore.activeEmpresa">
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20 shadow-md">
            <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">NF-e no mês</p>
            <p class="text-3xl font-bold text-white">{{ dashboardData.nfe_emitidas_mes || 0 }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20 shadow-md">
            <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Contas a pagar</p>
            <p class="text-3xl font-bold text-red-300">{{ formatCurrency(dashboardData.contas_pagar_5d) }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20 shadow-md">
            <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Contas a receber</p>
            <p class="text-3xl font-bold text-green-300">{{ formatCurrency(dashboardData.contas_receber_5d) }}</p>
          </div>
          <div class="bg-ancora-black/50 p-4 rounded-lg border border-ancora-gold/20 shadow-md">
            <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Saldo bancário</p>
            <p class="text-3xl font-bold text-white">{{ formatCurrency(dashboardData.saldo_total_contas) }}</p>
          </div>
        </div>

        <div v-if="error" class="mt-4 p-4 border border-red-500/30 rounded-lg bg-red-500/10 text-red-200">
          {{ error }}
        </div>
      </div>

      <div v-else class="p-4 border border-red-500/30 rounded-lg bg-red-500/10 text-red-200">
        Nenhuma empresa ativa foi encontrada para este usuário.
      </div>

      <section
        v-if="authStore.user.perfil_empresa !== 'CLIENTE' && availableEmpresas.length"
        class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-xl font-display text-ancora-gold">Empresas da carteira</h3>
            <p class="text-sm text-gray-400">Troque o contexto operacional sem sair do sistema.</p>
          </div>
          <router-link to="/empresas" class="text-sm text-gray-400 hover:text-ancora-gold">
            Gerenciar empresas
          </router-link>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <button
            v-for="empresa in availableEmpresas"
            :key="empresa.id"
            type="button"
            @click="handleSelectEmpresa(empresa.id)"
            :disabled="switchingCompany"
            class="text-left p-4 rounded-lg border transition-colors disabled:opacity-60"
            :class="empresa.id === empresaStore.activeEmpresa?.id
              ? 'border-ancora-gold bg-ancora-navy/50'
              : 'border-ancora-gold/20 bg-ancora-black/30 hover:bg-ancora-navy/30'"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="font-semibold text-white">{{ empresa.nome_fantasia || empresa.razao_social }}</p>
                <p class="text-sm text-gray-400 mt-1">{{ formatCnpj(empresa.cnpj) }}</p>
                <p class="text-xs uppercase tracking-wide text-gray-500 mt-2">{{ empresa.regime_tributario }}</p>
              </div>
              <span
                v-if="empresa.id === empresaStore.activeEmpresa?.id"
                class="text-[11px] font-bold px-2 py-1 rounded bg-ancora-gold text-ancora-black uppercase"
              >
                Ativo
              </span>
            </div>
          </button>
        </div>
      </section>
    </section>

    <section v-else class="text-gray-400">
      Faça login para ver o dashboard.
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

import EmpresasService from '@/services/empresas.service'
import FinanceiroService from '@/services/financeiro.service'
import FiscalService from '@/services/fiscal.service'
import IntakeService from '@/services/intake.service'
import { useAuthStore } from '@/stores/auth'
import { useEmpresaStore } from '@/stores/empresa'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const empresaStore = useEmpresaStore()
const uiStore = useUiStore()

const switchingCompany = ref(false)
const availableEmpresas = ref([])
const portalSlug = ref(null)
const error = ref(null)
const dashboardData = ref({
  nfe_emitidas_mes: 0,
  contas_pagar_5d: 0,
  contas_receber_5d: 0,
  saldo_total_contas: 0,
})

onMounted(async () => {
  await initializeDashboard()
})

watch(() => empresaStore.activeEmpresa?.id, async (empresaId) => {
  if (empresaId) {
    await fetchDashboardData()
    return
  }

  Object.keys(dashboardData.value).forEach((key) => {
    dashboardData.value[key] = 0
  })
})

async function initializeDashboard() {
  if (authStore.user?.perfil_empresa !== 'CLIENTE') {
    await loadEmpresas()
  } else {
    await loadPortalSlug()
  }

  if (empresaStore.activeEmpresa) {
    await fetchDashboardData()
  }
}

async function loadPortalSlug() {
  try {
    const data = await IntakeService.listClientePortais()
    const portais = data.results || data || []
    portalSlug.value = portais[0]?.slug || null
  } catch {
    portalSlug.value = null
  }
}

async function loadEmpresas() {
  try {
    const response = await EmpresasService.getEmpresas()
    availableEmpresas.value = response.results || []
  } catch (loadError) {
    console.error('Erro ao carregar carteira de clientes:', loadError)
  }
}

async function handleSelectEmpresa(empresaId) {
  switchingCompany.value = true
  try {
    await empresaStore.selectEmpresa(empresaId)
    await loadEmpresas()
    uiStore.showNotification('Empresa ativa atualizada.', 'success')
  } catch (selectError) {
    uiStore.showNotification('Falha ao trocar a empresa ativa.', 'error')
    console.error(selectError)
  } finally {
    switchingCompany.value = false
  }
}

async function fetchDashboardData() {
  if (!empresaStore.activeEmpresa) {
    return
  }

  error.value = null

  try {
    const today = new Date()
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]
    const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().split('T')[0]

    const nfeResponse = await FiscalService.getNotasFiscais({
      data_emissao_after: firstDayOfMonth,
      data_emissao_before: lastDayOfMonth,
    })
    dashboardData.value.nfe_emitidas_mes = nfeResponse.count

    const contasPagarResponse = await FinanceiroService.getContasVencendoHoje()
    const contasPagar = contasPagarResponse?.contas_a_pagar_hoje || []
    dashboardData.value.contas_pagar_5d = contasPagar
      .reduce((sum, conta) => sum + parseFloat(conta.valor_saldo || 0), 0)

    const contasReceberResponse = await FinanceiroService.getContasVencendoHoje()
    const contasReceber = contasReceberResponse?.contas_a_receber_hoje || []
    dashboardData.value.contas_receber_5d = contasReceber
      .reduce((sum, conta) => sum + parseFloat(conta.valor_saldo || 0), 0)

    const contasBancariasResponse = await FinanceiroService.getContasBancarias()
    const contasBancarias = contasBancariasResponse?.results || []
    dashboardData.value.saldo_total_contas = contasBancarias
      .reduce((sum, conta) => sum + parseFloat(conta.saldo_atual || 0), 0)
  } catch (fetchError) {
    error.value = 'Falha ao carregar os indicadores da empresa ativa.'
    console.error('Erro ao carregar dashboard:', fetchError)
  }
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value || 0)
}
</script>
