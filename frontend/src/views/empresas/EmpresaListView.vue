<template>
  <div class="p-4">
    <div class="mb-6">
      <h1 class="text-3xl font-display text-ancora-gold mb-2">Empresas da Carteira</h1>
      <p style="color: rgb(var(--color-text-muted))">
        Um único escritório, várias empresas atendidas. Escolha abaixo qual empresa ficará ativa no contexto operacional.
      </p>
    </div>

    <div v-if="loading" class="text-center" style="color: rgb(var(--color-text-muted))">
      Carregando empresas da carteira...
    </div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <template v-if="empresas.length > 0">
      <!-- Barra de controle da listagem -->
      <div class="flex items-center justify-between mb-4">
        <p class="text-sm" style="color: rgb(var(--color-text-muted))">
          {{ empresas.length }} empresa{{ empresas.length !== 1 ? 's' : '' }} na carteira
        </p>
        <div class="flex gap-1 border border-ancora-navy/60 rounded-lg p-1">
          <button
            @click="viewMode = 'card'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="viewMode === 'card'
              ? 'bg-ancora-gold text-ancora-black'
              : 'text-ancora-gold hover:bg-ancora-navy/40'"
            title="Visualização em cards"
          >
            ⊞ Cards
          </button>
          <button
            @click="viewMode = 'list'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="viewMode === 'list'
              ? 'bg-ancora-gold text-ancora-black'
              : 'text-ancora-gold hover:bg-ancora-navy/40'"
            title="Visualização em lista"
          >
            ☰ Lista
          </button>
        </div>
      </div>

      <!-- Visualização em Cards -->
      <div v-if="viewMode === 'card'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="empresa in empresas"
          :key="empresa.id"
          @click="selectEmpresa(empresa.id)"
          class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
          :class="{
            'border-ancora-gold/50 bg-ancora-navy/50 shadow-md': empresa.id === empresaStore.activeEmpresa?.id,
            'border-ancora-gold/20 bg-ancora-black/50 hover:bg-ancora-navy/30': empresa.id !== empresaStore.activeEmpresa?.id
          }"
        >
          <div class="flex justify-between items-start mb-1">
            <h3 class="font-bold text-lg"
              :class="empresa.id === empresaStore.activeEmpresa?.id ? 'text-ancora-gold' : ''"
              style="color: rgb(var(--color-text))">
              {{ empresa.nome_fantasia || empresa.razao_social }}
            </h3>
            <router-link
              :to="`/empresas/${empresa.id}/configuracoes`"
              @click.stop
              class="p-1 hover:text-ancora-gold transition-colors"
              style="color: rgb(var(--color-text-muted))"
              title="Configurações da empresa"
            >⚙️</router-link>
          </div>
          <p class="text-sm" style="color: rgb(var(--color-text-muted))">CNPJ: {{ formatCnpj(empresa.cnpj) }}</p>
          <p class="text-xs mt-1" style="color: rgb(var(--color-text-subtle))">{{ empresa.regime_tributario_display }}</p>
          <span
            v-if="empresa.id === empresaStore.activeEmpresa?.id"
            class="mt-2 inline-block bg-ancora-gold text-ancora-black text-xs font-bold px-2 py-1 rounded-full"
          >
            Empresa ativa
          </span>
        </div>
      </div>

      <!-- Visualização em Lista -->
      <div v-else class="border border-ancora-gold/20 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-ancora-navy/60">
            <tr>
              <th class="px-4 py-3 text-left text-ancora-gold font-semibold">Empresa</th>
              <th class="px-4 py-3 text-left text-ancora-gold font-semibold hidden md:table-cell">CNPJ</th>
              <th class="px-4 py-3 text-left text-ancora-gold font-semibold hidden lg:table-cell">Regime</th>
              <th class="px-4 py-3 text-center text-ancora-gold font-semibold">Status</th>
              <th class="px-4 py-3 text-center text-ancora-gold font-semibold">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="empresa in empresas"
              :key="empresa.id"
              @click="selectEmpresa(empresa.id)"
              class="border-t border-ancora-gold/10 cursor-pointer transition-colors"
              :class="{
                'bg-ancora-navy/40': empresa.id === empresaStore.activeEmpresa?.id,
                'hover:bg-ancora-navy/20': empresa.id !== empresaStore.activeEmpresa?.id
              }"
            >
              <td class="px-4 py-3">
                <span class="font-semibold" style="color: rgb(var(--color-text))">
                  {{ empresa.nome_fantasia || empresa.razao_social }}
                </span>
                <span v-if="empresa.razao_social && empresa.nome_fantasia" class="block text-xs" style="color: rgb(var(--color-text-muted))">
                  {{ empresa.razao_social }}
                </span>
              </td>
              <td class="px-4 py-3 hidden md:table-cell font-mono text-xs" style="color: rgb(var(--color-text-muted))">
                {{ formatCnpj(empresa.cnpj) }}
              </td>
              <td class="px-4 py-3 hidden lg:table-cell text-xs" style="color: rgb(var(--color-text-muted))">
                {{ empresa.regime_tributario_display }}
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  v-if="empresa.id === empresaStore.activeEmpresa?.id"
                  class="inline-block bg-ancora-gold text-ancora-black text-xs font-bold px-2 py-1 rounded-full"
                >
                  Ativa
                </span>
              </td>
              <td class="px-4 py-3 text-center" @click.stop>
                <router-link
                  :to="`/empresas/${empresa.id}/configuracoes`"
                  class="px-3 py-1 border border-ancora-gold/30 rounded text-ancora-gold hover:bg-ancora-gold/10 text-xs transition-colors"
                >
                  ⚙️ Config
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="text-center" style="color: rgb(var(--color-text-muted))">
      Nenhuma empresa da carteira encontrada.
    </div>

    <!-- Formulário de cadastro -->
    <div class="mt-8">
      <h2 class="text-2xl font-display text-ancora-gold mb-2">Adicionar Empresa-Cliente</h2>
      <p class="text-sm mb-4" style="color: rgb(var(--color-text-muted))">
        Cadastre uma nova empresa atendida pelo escritório para ativá-la depois no restante do sistema.
      </p>
      <form @submit.prevent="submitNewEmpresa" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="razao_social" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Razão Social</label>
          <input type="text" id="razao_social" v-model="newEmpresa.razao_social" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="nome_fantasia" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Nome Fantasia</label>
          <input type="text" id="nome_fantasia" v-model="newEmpresa.nome_fantasia"
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="cnpj" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">CNPJ</label>
          <input type="text" id="cnpj" v-model="newEmpresa.cnpj" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="regime_tributario" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Regime Tributário</label>
          <select id="regime_tributario" v-model="newEmpresa.regime_tributario" required
                  class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                  style="color: rgb(var(--color-text))">
            <option value="SN">Simples Nacional</option>
            <option value="LP">Lucro Presumido</option>
            <option value="LR">Lucro Real</option>
          </select>
        </div>
        <div>
          <label for="cep" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">CEP</label>
          <div class="flex">
            <input type="text" id="cep" v-model="newEmpresa.cep" @blur="fetchAddress"
                   placeholder="00000-000"
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                   style="color: rgb(var(--color-text))"/>
            <button type="button" @click="fetchAddress" :disabled="cepLoading"
                    class="ml-2 px-4 py-2 bg-ancora-navy rounded-md text-ancora-gold hover:bg-ancora-navy/80 disabled:opacity-50 min-w-[80px]">
              <span v-if="cepLoading">...</span>
              <span v-else>Buscar</span>
            </button>
          </div>
        </div>
        <div>
          <label for="logradouro" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Logradouro</label>
          <input type="text" id="logradouro" v-model="newEmpresa.logradouro" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="numero" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Número</label>
          <input type="text" id="numero" v-model="newEmpresa.numero" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="bairro" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Bairro</label>
          <input type="text" id="bairro" v-model="newEmpresa.bairro" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="municipio" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">Município</label>
          <input type="text" id="municipio" v-model="newEmpresa.municipio" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div>
          <label for="uf" class="block text-sm font-body" style="color: rgb(var(--color-text-muted))">UF</label>
          <input type="text" id="uf" v-model="newEmpresa.uf" required maxlength="2"
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm"
                 style="color: rgb(var(--color-text))"/>
        </div>
        <div class="md:col-span-2">
          <button type="submit" :disabled="uiStore.isLoading"
                  class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md text-sm font-bold text-ancora-black bg-ancora-gold hover:bg-ancora-gold/90 focus:outline-none focus:ring-2 focus:ring-ancora-gold disabled:opacity-50">
            <span v-if="uiStore.isLoading">Adicionando...</span>
            <span v-else>Adicionar empresa-cliente</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEmpresaStore } from '@/stores/empresa'
import { useUiStore } from '@/stores/ui'
import EmpresasService from '@/services/empresas.service'
import { extractApiErrorMessage } from '@/utils/api'

const empresaStore = useEmpresaStore()
const uiStore = useUiStore()

const empresas = ref([])
const loading = ref(false)
const error = ref(null)
const viewMode = ref(localStorage.getItem('empresas-view-mode') || 'card')
const cepLoading = ref(false)

const newEmpresa = ref({
  razao_social: '',
  nome_fantasia: '',
  cnpj: '',
  regime_tributario: 'SN',
  cnae_principal: '0000000',
  cep: '',
  logradouro: '',
  numero: '',
  bairro: '',
  municipio: '',
  uf: '',
})

import { watch } from 'vue'
watch(viewMode, (val) => localStorage.setItem('empresas-view-mode', val))

onMounted(() => {
  fetchEmpresas()
})

async function fetchEmpresas() {
  loading.value = true
  error.value = null
  try {
    const response = await EmpresasService.getEmpresas()
    empresas.value = response.results.map(emp => ({
      ...emp,
      regime_tributario_display: getRegimeTributarioDisplay(emp.regime_tributario)
    }))
  } catch (err) {
    error.value = 'Falha ao carregar as empresas da carteira.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar empresas:', err)
  } finally {
    loading.value = false
  }
}

async function selectEmpresa(empresaId) {
  try {
    await empresaStore.selectEmpresa(empresaId)
    uiStore.showNotification('Empresa ativa selecionada!', 'success')
    await fetchEmpresas()
  } catch (err) {
    uiStore.showNotification('Falha ao selecionar a empresa ativa.', 'error')
    console.error('Erro ao selecionar empresa:', err)
  }
}

async function fetchAddress() {
  const cep = newEmpresa.value.cep.replace(/\D/g, '')
  if (cep.length === 8) {
    try {
      cepLoading.value = true
      const address = await EmpresasService.buscarCep(cep)
      if (address) {
        newEmpresa.value.logradouro = address.logradouro
        newEmpresa.value.bairro = address.bairro
        newEmpresa.value.municipio = address.localidade
        newEmpresa.value.uf = address.uf
        newEmpresa.value.cep = address.cep
        uiStore.showNotification('Endereço preenchido automaticamente!', 'success')
      } else {
        uiStore.showNotification('CEP não encontrado.', 'warning')
      }
    } catch (err) {
      uiStore.showNotification('Erro ao buscar CEP.', 'error')
      console.error('Erro ao buscar CEP:', err)
    } finally {
      cepLoading.value = false
    }
  }
}

async function submitNewEmpresa() {
  uiStore.setLoading(true)
  try {
    await EmpresasService.createEmpresa({
      ...newEmpresa.value,
      cnpj: normalizeDigits(newEmpresa.value.cnpj),
      cep: normalizeDigits(newEmpresa.value.cep),
      uf: (newEmpresa.value.uf || '').toUpperCase(),
    })
    uiStore.showNotification('Empresa-cliente adicionada com sucesso!', 'success')
    newEmpresa.value = {
      razao_social: '', nome_fantasia: '', cnpj: '',
      regime_tributario: 'SN', cnae_principal: '0000000',
      cep: '', logradouro: '', numero: '', bairro: '', municipio: '', uf: '',
    }
    await fetchEmpresas()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao adicionar empresa-cliente.'), 'error', 6000)
    console.error('Erro ao adicionar empresa:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function getRegimeTributarioDisplay(regime) {
  const choices = {
    SN: 'Simples Nacional', SNEI: 'Simples Nacional — Excesso', LP: 'Lucro Presumido',
    LR: 'Lucro Real', LA: 'Lucro Arbitrado', MEI: 'MEI', ENTE: 'Órgão Público',
  }
  return choices[regime] || regime
}

function normalizeDigits(value) {
  return (value || '').replace(/\D/g, '')
}
</script>
