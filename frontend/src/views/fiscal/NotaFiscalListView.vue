<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Notas Fiscais</h1>

    <div v-if="loading" class="text-center text-gray-400">Carregando notas fiscais...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchNotasFiscais" placeholder="Buscar nota por número, chave ou destinatário..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Nova NF-e
      </button>
    </div>

    <div v-if="notasFiscais.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Número/Série</th>
          <th class="py-3 px-6 text-left">Destinatário</th>
          <th class="py-3 px-6 text-left">Status</th>
          <th class="py-3 px-6 text-right">Valor Total</th>
          <th class="py-3 px-6 text-left">Emissão</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="nf in notasFiscais" :key="nf.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ nf.numero }}/{{ nf.serie }}</td>
          <td class="py-3 px-6 text-left">{{ nf.destinatario_nome }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="getStatusClass(nf.status)" class="px-2 py-1 rounded-full text-xs text-white">
              {{ nf.status_display }}
            </span>
          </td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(nf.valor_total_nf) }}</td>
          <td class="py-3 px-6 text-left">{{ formatDate(nf.data_emissao) }}</td>
          <td class="py-3 px-6 text-center whitespace-nowrap">
            <button @click="openModalForEdit(nf)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="autorizarNota(nf.id)" v-if="nf.status === 'RASCUNHO' || nf.status === 'REJEITADA'" class="text-green-500 hover:text-green-400 font-bold mr-3">Autorizar</button>
            <button @click="cancelarNota(nf.id)" v-if="nf.status === 'AUTORIZADA'" class="text-red-500 hover:text-red-400 font-bold mr-3">Cancelar</button>
            <button @click="downloadDanfe(nf.id)" v-if="nf.status === 'AUTORIZADA'" class="text-blue-500 hover:text-blue-400 font-bold mr-3">DANFE</button>
            <button @click="deleteNota(nf.id)" class="text-gray-500 hover:text-gray-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhuma nota fiscal encontrada.
    </div>

    <!-- Modal para Adicionar/Editar Nota Fiscal -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-ancora-black/70 flex items-center justify-center z-50">
      <div class="bg-ancora-black/90 p-8 rounded-lg shadow-xl border border-ancora-gold/30 w-full max-w-4xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingNF ? 'Editar Nota Fiscal' : 'Nova Nota Fiscal' }}</h2>
        <form @submit.prevent="saveNotaFiscal" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="modal_tipo_nf" class="block text-sm font-body text-gray-300">Tipo de NF</label>
              <select id="modal_tipo_nf" v-model="currentNF.tipo_nf" required
                      class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
                <option value="1">NF-e (Modelo 55)</option>
                <option value="2">NFC-e (Modelo 65)</option>
              </select>
            </div>
            <div>
              <label for="modal_finalidade" class="block text-sm font-body text-gray-300">Finalidade</label>
              <select id="modal_finalidade" v-model="currentNF.finalidade" required
                      class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white">
                <option value="1">NF-e Normal</option>
                <option value="4">Devolução de Mercadoria</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label for="modal_destinatario_nome" class="block text-sm font-body text-gray-300">Destinatário Nome/Razão Social</label>
              <input type="text" id="modal_destinatario_nome" v-model="currentNF.destinatario_nome" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_destinatario_documento" class="block text-sm font-body text-gray-300">Destinatário CPF/CNPJ</label>
              <input type="text" id="modal_destinatario_documento" v-model="currentNF.destinatario_documento" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_destinatario_ie" class="block text-sm font-body text-gray-300">Destinatário IE</label>
              <input type="text" id="modal_destinatario_ie" v-model="currentNF.destinatario_ie"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <!-- Endereço Destinatário -->
            <div class="md:col-span-2">
              <h3 class="text-lg font-body text-ancora-gold mt-4 mb-2">Endereço do Destinatário</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="modal_destinatario_cep" class="block text-sm font-body text-gray-300">CEP</label>
                  <div class="flex">
                    <input type="text" id="modal_destinatario_cep" v-model="currentNF.destinatario_cep"
                           placeholder="00000-000"
                           class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                    <button type="button" @click="fetchRecipientAddress" :disabled="cepLoading"
                            class="ml-2 mt-1 px-3 py-2 bg-ancora-navy rounded-md text-ancora-gold hover:bg-ancora-navy/80 disabled:opacity-50">
                      {{ cepLoading ? '...' : '🔍' }}
                    </button>
                  </div>
                </div>
                <div>
                  <label for="modal_destinatario_logradouro" class="block text-sm font-body text-gray-300">Logradouro</label>
                  <input type="text" id="modal_destinatario_logradouro" v-model="currentNF.destinatario_logradouro"
                         class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                </div>
                <div>
                  <label for="modal_destinatario_numero" class="block text-sm font-body text-gray-300">Número</label>
                  <input type="text" id="modal_destinatario_numero" v-model="currentNF.destinatario_numero"
                         class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                </div>
                <div>
                  <label for="modal_destinatario_bairro" class="block text-sm font-body text-gray-300">Bairro</label>
                  <input type="text" id="modal_destinatario_bairro" v-model="currentNF.destinatario_bairro"
                         class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                </div>
                <div>
                  <label for="modal_destinatario_municipio" class="block text-sm font-body text-gray-300">Município</label>
                  <input type="text" id="modal_destinatario_municipio" v-model="currentNF.destinatario_municipio"
                         class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                </div>
                <div>
                  <label for="modal_destinatario_uf" class="block text-sm font-body text-gray-300">UF</label>
                  <input type="text" id="modal_destinatario_uf" v-model="currentNF.destinatario_uf" maxlength="2"
                         class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
                </div>
              </div>
            </div>
            <!-- Outros campos da NF, se necessário -->
          </div>
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar NF-e</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FiscalService from '@/services/fiscal.service'
import EmpresasService from '@/services/empresas.service'

const uiStore = useUiStore()

const notasFiscais = ref([])
const loading = ref(false)
const cepLoading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingNF = ref(false)
const currentNF = ref({
  id: null,
  tipo_nf: '1',
  finalidade: '1',
  destinatario_nome: '',
  destinatario_documento: '',
  destinatario_ie: '',
  destinatario_cep: '',
  destinatario_logradouro: '',
  destinatario_numero: '',
  destinatario_bairro: '',
  destinatario_municipio: '',
  destinatario_uf: '',
  // Outros campos importantes para criação
})

onMounted(() => {
  fetchNotasFiscais()
})

async function fetchNotasFiscais() {
  loading.value = true
  error.value = null
  try {
    const response = await FiscalService.getNotasFiscais({ search: searchQuery.value })
    notasFiscais.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar notas fiscais.'
    uiStore.showNotification(error.value, 'error')
    console.error('Erro ao carregar notas fiscais:', err)
  } finally {
    loading.value = false
  }
}

async function fetchRecipientAddress() {
  const cep = currentNF.value.destinatario_cep.replace(/\D/g, '')
  if (cep.length === 8) {
    try {
      cepLoading.value = true
      const address = await EmpresasService.buscarCep(cep)
      if (address) {
        currentNF.value.destinatario_logradouro = address.logradouro
        currentNF.value.destinatario_bairro = address.bairro
        currentNF.value.destinatario_municipio = address.localidade
        currentNF.value.destinatario_uf = address.uf
        currentNF.value.destinatario_cep = address.cep
        uiStore.showNotification('Endereço do destinatário preenchido!', 'success')
      } else {
        uiStore.showNotification('CEP não encontrado.', 'warning')
      }
    } catch (err) {
      uiStore.showNotification('Erro ao buscar CEP.', 'error')
      console.error(err)
    } finally {
      cepLoading.value = false
    }
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'AUTORIZADA': return 'bg-green-500';
    case 'REJEITADA': return 'bg-red-500';
    case 'PENDENTE':
    case 'PROCESSANDO': return 'bg-yellow-500';
    case 'CANCELADA':
    case 'DENEGADA': return 'bg-gray-500';
    default: return 'bg-blue-500'; // RASCUNHO
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function formatDate(dateString) {
  if (!dateString) return '';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

function openModalForCreate() {
  editingNF.value = false
  currentNF.value = {
    id: null,
    tipo_nf: '1',
    finalidade: '1',
    destinatario_nome: '',
    destinatario_documento: '',
    destinatario_ie: '',
    destinatario_cep: '',
    destinatario_logradouro: '',
    destinatario_numero: '',
    destinatario_bairro: '',
    destinatario_municipio: '',
    destinatario_uf: '',
  }
  isModalOpen.value = true
}

function openModalForEdit(nf) {
  editingNF.value = true
  currentNF.value = { ...nf }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveNotaFiscal() {
  uiStore.setLoading(true)
  try {
    if (editingNF.value) {
      await FiscalService.updateNotaFiscal(currentNF.value.id, currentNF.value)
      uiStore.showNotification('Nota Fiscal atualizada com sucesso!', 'success')
    } else {
      await FiscalService.createNotaFiscal(currentNF.value)
      uiStore.showNotification('Nota Fiscal criada com sucesso!', 'success')
    }
    closeModal()
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar Nota Fiscal.', 'error')
    console.error('Erro ao salvar Nota Fiscal:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function autorizarNota(id) {
  if (confirm('Tem certeza que deseja autorizar esta Nota Fiscal?')) {
    uiStore.setLoading(true)
    try {
      await FiscalService.autorizarNotaFiscal(id)
      uiStore.showNotification('Nota Fiscal enviada para autorização!', 'success')
      fetchNotasFiscais()
    } catch (err) {
      uiStore.showNotification('Erro ao autorizar Nota Fiscal.', 'error')
      console.error('Erro ao autorizar Nota Fiscal:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

async function cancelarNota(id) {
  const justificativa = prompt('Digite a justificativa para o cancelamento da Nota Fiscal:')
  if (justificativa) {
    uiStore.setLoading(true)
    try {
      await FiscalService.cancelarNotaFiscal(id, justificativa)
      uiStore.showNotification('Nota Fiscal cancelada!', 'success')
      fetchNotasFiscais()
    } catch (err) {
      uiStore.showNotification('Erro ao cancelar Nota Fiscal.', 'error')
      console.error('Erro ao cancelar Nota Fiscal:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

async function downloadDanfe(id) {
  uiStore.setLoading(true)
  try {
    const response = await FiscalService.getDanfePdf(id)
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    uiStore.showNotification('DANFE gerado com sucesso!', 'success')
  } catch (err) {
    uiStore.showNotification('Erro ao gerar DANFE.', 'error')
    console.error('Erro ao gerar DANFE:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteNota(id) {
  if (confirm('Tem certeza que deseja excluir esta Nota Fiscal? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await FiscalService.deleteNotaFiscal(id)
      uiStore.showNotification('Nota Fiscal excluída com sucesso!', 'success')
      fetchNotasFiscais()
    } catch (err) {
      uiStore.showNotification('Erro ao excluir Nota Fiscal.', 'error')
      console.error('Erro ao excluir Nota Fiscal:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}
</script>