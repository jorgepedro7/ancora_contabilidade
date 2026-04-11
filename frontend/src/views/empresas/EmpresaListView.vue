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
          <button @click="viewMode = 'card'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="viewMode === 'card' ? 'bg-ancora-gold text-ancora-black' : 'text-ancora-gold hover:bg-ancora-navy/40'"
          >⊞ Cards</button>
          <button @click="viewMode = 'list'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="viewMode === 'list' ? 'bg-ancora-gold text-ancora-black' : 'text-ancora-gold hover:bg-ancora-navy/40'"
          >☰ Lista</button>
        </div>
      </div>

      <!-- Visualização em Cards -->
      <div v-if="viewMode === 'card'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="empresa in empresas" :key="empresa.id"
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
            <div class="flex gap-1" @click.stop>
              <button @click="abrirEdicao(empresa)" title="Editar dados"
                class="p-1 rounded hover:text-ancora-gold transition-colors"
                style="color: rgb(var(--color-text-muted))">✏️</button>
              <router-link :to="`/empresas/${empresa.id}/configuracoes`"
                class="p-1 rounded hover:text-ancora-gold transition-colors"
                style="color: rgb(var(--color-text-muted))" title="Configurações fiscais">⚙️</router-link>
              <button @click="confirmarExclusao(empresa)" title="Excluir empresa"
                class="p-1 rounded hover:text-red-400 transition-colors"
                style="color: rgb(var(--color-text-muted))">🗑️</button>
            </div>
          </div>
          <p class="text-sm" style="color: rgb(var(--color-text-muted))">CNPJ: {{ formatCnpj(empresa.cnpj) }}</p>
          <p class="text-xs mt-1" style="color: rgb(var(--color-text-subtle))">{{ empresa.regime_tributario_display }}</p>
          <span v-if="empresa.id === empresaStore.activeEmpresa?.id"
            class="mt-2 inline-block bg-ancora-gold text-ancora-black text-xs font-bold px-2 py-1 rounded-full">
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
            <tr v-for="empresa in empresas" :key="empresa.id"
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
                <span v-if="empresa.id === empresaStore.activeEmpresa?.id"
                  class="inline-block bg-ancora-gold text-ancora-black text-xs font-bold px-2 py-1 rounded-full">
                  Ativa
                </span>
              </td>
              <td class="px-4 py-3" @click.stop>
                <div class="flex items-center justify-center gap-2">
                  <button @click="abrirEdicao(empresa)"
                    class="px-2 py-1 border border-ancora-gold/30 rounded text-ancora-gold hover:bg-ancora-gold/10 text-xs transition-colors">
                    ✏️ Editar
                  </button>
                  <router-link :to="`/empresas/${empresa.id}/configuracoes`"
                    class="px-2 py-1 border border-ancora-gold/30 rounded text-ancora-gold hover:bg-ancora-gold/10 text-xs transition-colors">
                    ⚙️ Config
                  </router-link>
                  <button @click="confirmarExclusao(empresa)"
                    class="px-2 py-1 border border-red-500/30 rounded text-red-400 hover:bg-red-500/10 text-xs transition-colors">
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="text-center" style="color: rgb(var(--color-text-muted))">
      Nenhuma empresa da carteira encontrada.
    </div>

    <!-- Formulário de criação/edição (modal) -->
    <div v-if="showForm" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div class="bg-ancora-black border border-ancora-gold/30 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-display text-ancora-gold">
              {{ editingEmpresa ? 'Editar Empresa-Cliente' : 'Adicionar Empresa-Cliente' }}
            </h2>
            <button @click="fecharForm" class="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
          </div>

          <form @submit.prevent="submitEmpresa" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Razão Social *</label>
              <input type="text" v-model="form.razao_social" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Nome Fantasia</label>
              <input type="text" v-model="form.nome_fantasia"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CNPJ *</label>
              <input type="text" v-model="form.cnpj" required :disabled="!!editingEmpresa"
                placeholder="00.000.000/0000-00"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold disabled:opacity-50"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Regime Tributário *</label>
              <select v-model="form.regime_tributario" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold">
                <option value="SN">Simples Nacional</option>
                <option value="SNEI">Simples Nacional — Excesso</option>
                <option value="LP">Lucro Presumido</option>
                <option value="LR">Lucro Real</option>
                <option value="LA">Lucro Arbitrado</option>
                <option value="MEI">MEI</option>
                <option value="ENTE">Entidade Imune ou Isenta</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Porte</label>
              <select v-model="form.porte"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold">
                <option value="">— Selecione —</option>
                <option value="MEI">MEI</option>
                <option value="ME">Microempresa</option>
                <option value="EPP">Empresa de Pequeno Porte</option>
                <option value="MEDIO">Médio Porte</option>
                <option value="GRANDE">Grande Empresa</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CNAE Principal *</label>
              <input type="text" v-model="form.cnae_principal" required maxlength="7"
                placeholder="0000000"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>

            <!-- Endereço -->
            <div class="md:col-span-2 border-t border-ancora-gold/10 pt-4 mt-2">
              <p class="text-xs uppercase tracking-wide text-gray-500 mb-3">Endereço</p>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CEP *</label>
              <div class="flex gap-2">
                <input type="text" v-model="form.cep" @blur="fetchAddress"
                  placeholder="00000-000"
                  class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
                <button type="button" @click="fetchAddress" :disabled="cepLoading"
                  class="px-3 py-2 bg-ancora-navy rounded text-ancora-gold hover:bg-ancora-navy/80 disabled:opacity-50 text-sm whitespace-nowrap">
                  {{ cepLoading ? '...' : 'Buscar' }}
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Logradouro *</label>
              <input type="text" v-model="form.logradouro" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Número *</label>
              <input type="text" v-model="form.numero" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Complemento</label>
              <input type="text" v-model="form.complemento"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Bairro *</label>
              <input type="text" v-model="form.bairro" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Município *</label>
              <input type="text" v-model="form.municipio" required
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">UF *</label>
              <input type="text" v-model="form.uf" required maxlength="2" style="text-transform:uppercase"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Código IBGE</label>
              <input type="text" v-model="form.ibge" maxlength="7"
                class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:outline-none focus:border-ancora-gold"/>
            </div>

            <div class="md:col-span-2 flex gap-3 mt-2">
              <button type="submit" :disabled="uiStore.isLoading"
                class="flex-1 py-2 px-4 bg-ancora-gold text-ancora-black font-bold rounded hover:bg-ancora-gold/90 disabled:opacity-50">
                {{ uiStore.isLoading ? 'Salvando...' : (editingEmpresa ? 'Salvar alterações' : 'Adicionar empresa-cliente') }}
              </button>
              <button type="button" @click="fecharForm"
                class="px-4 py-2 border border-ancora-gold/30 text-ancora-gold rounded hover:bg-ancora-gold/10">
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de confirmação de exclusão -->
    <div v-if="empresaParaExcluir" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div class="bg-ancora-black border border-red-500/30 rounded-xl shadow-2xl w-full max-w-md p-6">
        <h3 class="text-xl font-display text-red-400 mb-3">Confirmar exclusão</h3>
        <p style="color: rgb(var(--color-text-muted))" class="mb-1">
          Deseja desativar a empresa-cliente abaixo? Esta ação pode ser revertida pelo administrador.
        </p>
        <p class="font-bold text-white mb-6">{{ empresaParaExcluir.nome_fantasia || empresaParaExcluir.razao_social }}</p>
        <div class="flex gap-3">
          <button @click="excluirEmpresa" :disabled="uiStore.isLoading"
            class="flex-1 py-2 bg-red-600 text-white font-bold rounded hover:bg-red-700 disabled:opacity-50">
            {{ uiStore.isLoading ? 'Excluindo...' : 'Sim, desativar' }}
          </button>
          <button @click="empresaParaExcluir = null"
            class="px-4 py-2 border border-ancora-gold/30 text-ancora-gold rounded hover:bg-ancora-gold/10">
            Cancelar
          </button>
        </div>
      </div>
    </div>

    <!-- Botão para abrir formulário de criação -->
    <div class="mt-8">
      <button @click="abrirCriacao"
        class="px-6 py-3 bg-ancora-gold text-ancora-black font-bold rounded-lg hover:bg-ancora-gold/90 transition-colors">
        + Adicionar Empresa-Cliente
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
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
const showForm = ref(false)
const editingEmpresa = ref(null)
const empresaParaExcluir = ref(null)

watch(viewMode, (val) => localStorage.setItem('empresas-view-mode', val))

const formDefault = () => ({
  razao_social: '',
  nome_fantasia: '',
  cnpj: '',
  regime_tributario: 'SN',
  porte: '',
  cnae_principal: '',
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  municipio: '',
  uf: '',
  ibge: '',
})

const form = reactive(formDefault())

onMounted(() => fetchEmpresas())

async function fetchEmpresas() {
  loading.value = true
  error.value = null
  try {
    const response = await EmpresasService.getEmpresas()
    empresas.value = response.results.map(emp => ({
      ...emp,
      regime_tributario_display: getRegimeTributarioDisplay(emp.regime_tributario),
    }))
  } catch {
    error.value = 'Falha ao carregar as empresas da carteira.'
    uiStore.showNotification(error.value, 'error')
  } finally {
    loading.value = false
  }
}

function abrirCriacao() {
  editingEmpresa.value = null
  Object.assign(form, formDefault())
  showForm.value = true
}

function abrirEdicao(empresa) {
  editingEmpresa.value = empresa
  Object.assign(form, {
    razao_social: empresa.razao_social || '',
    nome_fantasia: empresa.nome_fantasia || '',
    cnpj: empresa.cnpj || '',
    regime_tributario: empresa.regime_tributario || 'SN',
    porte: empresa.porte || '',
    cnae_principal: empresa.cnae_principal || '',
    cep: empresa.cep || '',
    logradouro: empresa.logradouro || '',
    numero: empresa.numero || '',
    complemento: empresa.complemento || '',
    bairro: empresa.bairro || '',
    municipio: empresa.municipio || '',
    uf: empresa.uf || '',
    ibge: empresa.ibge || '',
  })
  showForm.value = true
}

function fecharForm() {
  showForm.value = false
  editingEmpresa.value = null
}

async function submitEmpresa() {
  uiStore.setLoading(true)
  try {
    const payload = {
      ...form,
      cnpj: normalizeDigits(form.cnpj),
      cep: normalizeDigits(form.cep),
      uf: form.uf.toUpperCase(),
      porte: form.porte || null,
      ibge: form.ibge || null,
      complemento: form.complemento || null,
    }

    if (editingEmpresa.value) {
      delete payload.cnpj // CNPJ não pode ser alterado
      await EmpresasService.updateEmpresa(editingEmpresa.value.id, payload)
      uiStore.showNotification('Empresa atualizada com sucesso!', 'success')
    } else {
      await EmpresasService.createEmpresa(payload)
      uiStore.showNotification('Empresa-cliente adicionada com sucesso!', 'success')
    }

    fecharForm()
    await fetchEmpresas()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar empresa.'), 'error', 6000)
  } finally {
    uiStore.setLoading(false)
  }
}

function confirmarExclusao(empresa) {
  empresaParaExcluir.value = empresa
}

async function excluirEmpresa() {
  if (!empresaParaExcluir.value) return
  uiStore.setLoading(true)
  try {
    await EmpresasService.deleteEmpresa(empresaParaExcluir.value.id)
    uiStore.showNotification('Empresa desativada com sucesso.', 'success')
    empresaParaExcluir.value = null
    await fetchEmpresas()
  } catch {
    uiStore.showNotification('Erro ao excluir empresa.', 'error')
  } finally {
    uiStore.setLoading(false)
  }
}

async function selectEmpresa(empresaId) {
  try {
    await empresaStore.selectEmpresa(empresaId)
    uiStore.showNotification('Empresa ativa selecionada!', 'success')
    await fetchEmpresas()
  } catch {
    uiStore.showNotification('Falha ao selecionar a empresa ativa.', 'error')
  }
}

async function fetchAddress() {
  const cep = form.cep.replace(/\D/g, '')
  if (cep.length !== 8) return
  cepLoading.value = true
  try {
    const address = await EmpresasService.buscarCep(cep)
    if (address) {
      form.logradouro = address.logradouro || form.logradouro
      form.bairro = address.bairro || form.bairro
      form.municipio = address.localidade || form.municipio
      form.uf = address.uf || form.uf
      form.ibge = address.ibge || form.ibge
      form.cep = address.cep || form.cep
      uiStore.showNotification('Endereço preenchido automaticamente!', 'success')
    } else {
      uiStore.showNotification('CEP não encontrado.', 'warning')
    }
  } catch {
    uiStore.showNotification('Erro ao buscar CEP.', 'error')
  } finally {
    cepLoading.value = false
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
