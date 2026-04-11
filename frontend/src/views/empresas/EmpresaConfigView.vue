<template>
  <div class="p-4 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold">Empresa e Configurações Fiscais</h1>
        <p class="text-sm text-gray-400 mt-2">Gerencie certificado e numeração fiscal da empresa-cliente selecionada.</p>
      </div>
      <router-link to="/empresas" class="text-sm text-gray-400 hover:text-ancora-gold transition-colors">
        &larr; Voltar para a carteira
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-10">
      <p class="text-gray-400 animate-pulse">Carregando configurações...</p>
    </div>

    <div v-else-if="empresa" class="space-y-6">
      <!-- Card da Empresa -->
      <div class="bg-ancora-navy/30 border border-ancora-gold/20 p-6 rounded-lg shadow-xl">
        <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 class="text-xl font-display text-ancora-gold mb-4">Dados da Empresa</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500 block uppercase text-xs font-bold">Razão Social</span>
                <span class="text-white text-lg">{{ empresa.razao_social }}</span>
              </div>
              <div>
                <span class="text-gray-500 block uppercase text-xs font-bold">CNPJ</span>
                <span class="text-white text-lg">{{ formatCnpj(empresa.cnpj) }}</span>
              </div>
            </div>
          </div>

          <button
            v-if="empresa.id !== empresaStore.activeEmpresa?.id"
            type="button"
            @click="selecionarComoAtiva"
            class="px-4 py-2 border border-ancora-gold/40 rounded-md text-ancora-gold hover:bg-ancora-gold/10 transition-colors"
          >
            Definir como empresa ativa
          </button>
        </div>
      </div>

      <!-- Certificado Digital -->
      <div class="bg-ancora-navy/30 border border-ancora-gold/20 p-6 rounded-lg shadow-xl">
        <h3 class="text-xl font-display text-ancora-gold mb-4 flex items-center">
          <span class="mr-2">🔐</span> Certificado Digital (.A1 / .PFX)
        </h3>
        
        <div v-if="empresa.certificado_data_validade" class="mb-4 p-3 border rounded border-green-500/30 bg-green-500/10 flex items-center justify-between">
          <div>
            <p class="text-sm text-green-400">Certificado configurado.</p>
            <p class="text-xs text-gray-400">Validade: {{ formatDate(empresa.certificado_data_validade) }}</p>
          </div>
          <span v-if="empresa.certificado_vencido" class="bg-red-600 text-white text-[10px] px-2 py-0.5 rounded font-bold uppercase">Expirado</span>
        </div>
        <div v-else class="mb-4 p-3 border rounded border-yellow-500/30 bg-yellow-500/10">
          <p class="text-sm text-yellow-400">Certificado não configurado. Suba um arquivo .pfx para emitir notas fiscais.</p>
        </div>

        <form @submit.prevent="handleCertificateUpload" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-body text-gray-300 mb-1">Arquivo do Certificado (.pfx)</label>
              <input type="file" @change="onFileChange" accept=".pfx,.p12"
                     class="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-ancora-gold file:text-ancora-black hover:file:bg-ancora-gold/80"/>
            </div>
            <div>
              <label class="block text-sm font-body text-gray-300 mb-1">Senha do Certificado</label>
              <input type="password" v-model="certData.password" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:ring-ancora-gold focus:border-ancora-gold"/>
            </div>
            <div>
              <label class="block text-sm font-body text-gray-300 mb-1">Data de Validade do Certificado *</label>
              <input type="date" v-model="certData.data_validade" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm focus:ring-ancora-gold focus:border-ancora-gold"/>
            </div>
          </div>
          <button type="submit" :disabled="uploading"
                  class="bg-ancora-navy border border-ancora-gold text-ancora-gold px-6 py-2 rounded shadow-md hover:bg-ancora-gold hover:text-ancora-black transition-all disabled:opacity-50">
            {{ uploading ? 'Enviando...' : 'Salvar Certificado' }}
          </button>
        </form>
      </div>

      <!-- Configurações SEFAZ -->
      <div v-if="empresa.configuracao_fiscal" class="bg-ancora-navy/30 border border-ancora-gold/20 p-6 rounded-lg shadow-xl">
        <h3 class="text-xl font-display text-ancora-gold mb-4 flex items-center">
          <span class="mr-2">⚙️</span> Ambiente e Numeração (SEFAZ)
        </h3>
        <form @submit.prevent="handleFiscalConfigUpdate" class="space-y-4">
          <!-- Ambiente -->
          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="block text-sm font-body text-gray-300 mb-1">Ambiente</label>
              <select v-model="fiscalConfig.ambiente_sefaz" class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option value="1">Produção</option>
                <option value="2">Homologação (Testes)</option>
              </select>
            </div>
          </div>

          <!-- NF-e -->
          <div>
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-2">NF-e (Modelo 55)</p>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">Série</label>
                <input type="text" v-model="fiscalConfig.serie_nfe" maxlength="3"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Próximo número</label>
                <input type="number" v-model="fiscalConfig.proximo_numero_nfe" min="1"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
            </div>
          </div>

          <!-- NFC-e -->
          <div>
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-2">NFC-e (Modelo 65)</p>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">Série</label>
                <input type="text" v-model="fiscalConfig.serie_nfce" maxlength="3"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Próximo número</label>
                <input type="number" v-model="fiscalConfig.proximo_numero_nfce" min="1"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">CSC ID</label>
                <input type="text" v-model="fiscalConfig.csc_id_nfce"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">CSC Token</label>
                <input type="password" v-model="fiscalConfig.csc_token_nfce"
                       placeholder="Deixe em branco para manter o atual"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
            </div>
          </div>

          <!-- NFS-e -->
          <div>
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-2">NFS-e (Serviços)</p>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">Série</label>
                <input type="text" v-model="fiscalConfig.serie_nfse" maxlength="3"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Próximo número</label>
                <input type="number" v-model="fiscalConfig.proximo_numero_nfse" min="1"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
              </div>
            </div>
          </div>

          <div>
            <button type="submit" :disabled="savingConfig"
                    class="bg-ancora-gold text-ancora-black px-6 py-2 rounded font-bold hover:bg-ancora-gold/80 transition-all disabled:opacity-50">
              {{ savingConfig ? 'Salvando...' : 'Atualizar Configurações' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useEmpresaStore } from '@/stores/empresa'
import EmpresasService from '@/services/empresas.service'

const route = useRoute()
const uiStore = useUiStore()
const empresaStore = useEmpresaStore()

const loading = ref(true)
const uploading = ref(false)
const savingConfig = ref(false)
const empresa = ref(null)
const selectedFile = ref(null)

const certData = reactive({
  password: '',
  data_validade: '',
})

const fiscalConfig = reactive({
  ambiente_sefaz: '2',
  serie_nfe: '001',
  proximo_numero_nfe: 1,
  serie_nfce: '001',
  proximo_numero_nfce: 1,
  csc_id_nfce: '',
  csc_token_nfce: '',
  serie_nfse: '001',
  proximo_numero_nfse: 1,
})

onMounted(async () => {
  await loadEmpresaData()
})

watch(() => route.params.id, async () => {
  await loadEmpresaData()
})

async function loadEmpresaData() {
  loading.value = true
  try {
    const empresaId = route.params.id || empresaStore.activeEmpresa?.id || (await empresaStore.syncActiveEmpresa())?.id
    if (!empresaId) {
      throw new Error('Nenhuma empresa disponível para configuração.')
    }
    const response = await EmpresasService.getEmpresa(empresaId)
    empresa.value = response
    
    // Preenche o formulário de config fiscal
    if (empresa.value.configuracao_fiscal) {
      const c = empresa.value.configuracao_fiscal
      fiscalConfig.ambiente_sefaz   = c.ambiente_sefaz
      fiscalConfig.serie_nfe        = c.serie_nfe
      fiscalConfig.proximo_numero_nfe = c.proximo_numero_nfe
      fiscalConfig.serie_nfce       = c.serie_nfce
      fiscalConfig.proximo_numero_nfce = c.proximo_numero_nfce
      fiscalConfig.csc_id_nfce      = c.csc_id_nfce || ''
      fiscalConfig.csc_token_nfce   = '' // write-only: não exibir valor atual
      fiscalConfig.serie_nfse       = c.serie_nfse
      fiscalConfig.proximo_numero_nfse = c.proximo_numero_nfse
    }
  } catch (err) {
    uiStore.showNotification('Erro ao carregar dados da empresa.', 'error')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function selecionarComoAtiva() {
  try {
    await empresaStore.selectEmpresa(empresa.value.id)
    uiStore.showNotification('Empresa ativa atualizada.', 'success')
  } catch (err) {
    uiStore.showNotification('Erro ao atualizar a empresa ativa.', 'error')
    console.error(err)
  }
}

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

async function handleCertificateUpload() {
  if (!selectedFile.value) {
    uiStore.showNotification('Selecione um arquivo .pfx primeiro.', 'warning')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('certificado_digital_pfx', selectedFile.value)
    formData.append('certificado_senha', certData.password)
    if (certData.data_validade) {
      formData.append('certificado_data_validade', certData.data_validade)
    }

    await EmpresasService.updateEmpresa(empresa.value.id, formData)
    uiStore.showNotification('Certificado atualizado com sucesso!', 'success')
    await loadEmpresaData()
    certData.password = ''
    certData.data_validade = ''
    selectedFile.value = null
  } catch (err) {
    uiStore.showNotification('Erro ao subir certificado.', 'error')
    console.error(err)
  } finally {
    uploading.value = false
  }
}

async function handleFiscalConfigUpdate() {
  savingConfig.value = true
  try {
    const configPayload = { ...fiscalConfig }
    // csc_token_nfce é write-only: só enviar se o usuário digitou algo
    if (!configPayload.csc_token_nfce) {
      delete configPayload.csc_token_nfce
    }
    await EmpresasService.updateEmpresa(empresa.value.id, {
      configuracao_fiscal: configPayload,
    })
    uiStore.showNotification('Configurações SEFAZ atualizadas!', 'success')
    await loadEmpresaData()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar configurações.', 'error')
    console.error(err)
  } finally {
    savingConfig.value = false
  }
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('pt-BR')
}
</script>
