<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Minhas Empresas</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando empresas...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div v-if="empresas.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="empresa in empresas"
        :key="empresa.id"
        @click="selectEmpresa(empresa.id)"
        class="p-4 border rounded-lg cursor-pointer transition-all duration-200"
        :class="{
          'border-ancora-gold/50 bg-ancora-navy/50 hover:bg-ancora-navy shadow-md': empresa.id === empresaStore.activeEmpresa?.id,
          'border-ancora-gold/20 bg-ancora-black/50 hover:bg-ancora-navy/70': empresa.id !== empresaStore.activeEmpresa?.id
        }"
      >
        <div class="flex justify-between items-start mb-1">
          <h3 class="font-body font-bold text-lg" :class="{'text-ancora-gold': empresa.id === empresaStore.activeEmpresa?.id}">
            {{ empresa.nome_fantasia || empresa.razao_social }}
          </h3>
          <router-link :to="`/empresas/${empresa.id}/configuracoes`" @click.stop
                       class="p-1 text-gray-400 hover:text-ancora-gold transition-colors" title="Configurações Fiscais">
            ⚙️
          </router-link>
        </div>
        <p class="text-sm text-gray-400">CNPJ: {{ formatCnpj(empresa.cnpj) }}</p>
        <p class="text-xs text-gray-500">Regime: {{ empresa.regime_tributario_display }}</p>
        <span
          v-if="empresa.id === empresaStore.activeEmpresa?.id"
          class="mt-2 inline-block bg-ancora-gold text-ancora-black text-xs font-bold px-2 py-1 rounded-full"
        >
          Empresa Ativa
        </span>
      </div>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400">
      Nenhuma empresa encontrada.
    </div>

    <div class="mt-8">
      <h2 class="text-2xl font-display text-ancora-gold mb-4">Adicionar Nova Empresa</h2>
      <form @submit.prevent="submitNewEmpresa" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="razao_social" class="block text-sm font-body text-gray-300">Razão Social</label>
          <input type="text" id="razao_social" v-model="newEmpresa.razao_social" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="nome_fantasia" class="block text-sm font-body text-gray-300">Nome Fantasia</label>
          <input type="text" id="nome_fantasia" v-model="newEmpresa.nome_fantasia"
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="cnpj" class="block text-sm font-body text-gray-300">CNPJ</label>
          <input type="text" id="cnpj" v-model="newEmpresa.cnpj" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="regime_tributario" class="block text-sm font-body text-gray-300">Regime Tributário</label>
          <select id="regime_tributario" v-model="newEmpresa.regime_tributario" required
                  class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
            <option value="SN">Simples Nacional</option>
            <option value="LP">Lucro Presumido</option>
            <option value="LR">Lucro Real</option>
          </select>
        </div>
        <div>
          <label for="cep" class="block text-sm font-body text-gray-300">CEP</label>
          <div class="flex">
            <input type="text" id="cep" v-model="newEmpresa.cep" @blur="fetchAddress"
                   placeholder="00000-000"
                   class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            <button type="button" @click="fetchAddress" :disabled="cepLoading"
                    class="ml-2 px-4 py-2 bg-ancora-navy rounded-md text-ancora-gold hover:bg-ancora-navy/80 disabled:opacity-50 min-w-[80px]">
              <span v-if="cepLoading">...</span>
              <span v-else>Buscar</span>
            </button>
          </div>
        </div>
        <div>
          <label for="logradouro" class="block text-sm font-body text-gray-300">Logradouro</label>
          <input type="text" id="logradouro" v-model="newEmpresa.logradouro" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="numero" class="block text-sm font-body text-gray-300">Número</label>
          <input type="text" id="numero" v-model="newEmpresa.numero" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="bairro" class="block text-sm font-body text-gray-300">Bairro</label>
          <input type="text" id="bairro" v-model="newEmpresa.bairro" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="municipio" class="block text-sm font-body text-gray-300">Município</label>
          <input type="text" id="municipio" v-model="newEmpresa.municipio" required
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div>
          <label for="uf" class="block text-sm font-body text-gray-300">UF</label>
          <input type="text" id="uf" v-model="newEmpresa.uf" required maxlength="2"
                 class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
        </div>
        <div class="md:col-span-2">
          <button type="submit" :disabled="uiStore.isLoading"
                  class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-bold text-ancora-black bg-ancora-gold hover:bg-ancora-gold/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ancora-gold disabled:opacity-50">
            <span v-if="uiStore.isLoading">Adicionando...</span>
            <span v-else>Adicionar Empresa</span>
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

const empresaStore = useEmpresaStore()
const uiStore = useUiStore()

const empresas = ref([])
const loading = ref(false)
const error = ref(null)

const cepLoading = ref(false)
const newEmpresa = ref({
  razao_social: '',
  nome_fantasia: '',
  cnpj: '',
  regime_tributario: 'SN',
  cnae_principal: '0000000', // Default
  cep: '',
  logradouro: '',
  numero: '',
  bairro: '',
  municipio: '',
  uf: '',
})

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
    error.value = 'Falha ao carregar empresas.'
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
    // Redireciona para o dashboard após selecionar
    // router.push('/') // Adicione o router import se for usar
  } catch (err) {
    uiStore.showNotification('Falha ao selecionar empresa.', 'error')
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
        // Formata o CEP no campo
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
    const createdEmpresa = await EmpresasService.createEmpresa(newEmpresa.value)
    uiStore.showNotification('Empresa adicionada com sucesso!', 'success')
    empresas.value.push({
      ...createdEmpresa,
      regime_tributario_display: getRegimeTributarioDisplay(createdEmpresa.regime_tributario)
    })
    // Limpar formulário
    newEmpresa.value = {
      razao_social: '',
      nome_fantasia: '',
      cnpj: '',
      regime_tributario: 'SN',
      cnae_principal: '0000000',
      cep: '', logradouro: '', numero: '', bairro: '', municipio: '', uf: '',
    }
  } catch (err) {
    uiStore.showNotification('Erro ao adicionar empresa.', 'error')
    console.error('Erro ao adicionar empresa:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  // Implementar formatação de CNPJ se necessário (já existe no backend, pode ser reusado)
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function getRegimeTributarioDisplay(regime) {
  const choices = {
    'SN': 'Simples Nacional',
    'LP': 'Lucro Presumido',
    'LR': 'Lucro Real',
    // Adicionar outros regimes conforme modelos do Django
  }
  return choices[regime] || regime
}
</script>