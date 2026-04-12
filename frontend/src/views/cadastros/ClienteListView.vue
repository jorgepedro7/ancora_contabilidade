<template>
  <div class="p-4">
    <div class="mb-6">
      <h1 class="text-3xl font-display text-ancora-gold mb-2">Clientes da Empresa Ativa</h1>
      <p class="text-gray-400">
        Cadastros comerciais da empresa-cliente
        <span class="font-semibold text-white">{{ empresaStore.activeEmpresa?.nome_fantasia || empresaStore.activeEmpresa?.razao_social || 'não selecionada' }}</span>.
      </p>
    </div>

    <div v-if="loading" class="text-center text-gray-400">Carregando clientes...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchClientes" placeholder="Buscar cliente por nome ou documento..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Novo Cliente
      </button>
    </div>

    <div v-if="clientes.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Nome/Razão Social</th>
          <th class="py-3 px-6 text-left">CPF/CNPJ</th>
          <th class="py-3 px-6 text-left">Telefone</th>
          <th class="py-3 px-6 text-left">Cidade/UF</th>
          <th class="py-3 px-6 text-left">Ativo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="cliente in clientes" :key="cliente.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">
            <div>{{ cliente.nome_razao_social }}</div>
            <div v-if="cliente.nome_fantasia_apelido" class="text-xs text-gray-500">{{ cliente.nome_fantasia_apelido }}</div>
          </td>
          <td class="py-3 px-6 text-left">{{ formatDocumento(cliente.documento, cliente.tipo_pessoa) }}</td>
          <td class="py-3 px-6 text-left">{{ cliente.telefone || '-' }}</td>
          <td class="py-3 px-6 text-left">{{ cliente.municipio ? `${cliente.municipio}/${cliente.uf}` : '-' }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="cliente.ativo ? 'bg-green-500' : 'bg-red-500'" class="px-2 py-1 rounded-full text-xs text-white">
              {{ cliente.ativo ? 'Sim' : 'Não' }}
            </span>
          </td>
          <td class="py-3 px-6 text-center">
            <button @click="openModalForEdit(cliente)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="openDeleteModal(cliente)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum cliente cadastrado para a empresa ativa.
    </div>

    <!-- Modal Criar/Editar Cliente -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-6">{{ editingCliente ? 'Editar Cliente' : 'Novo Cliente' }}</h2>
        <form @submit.prevent="saveCliente" class="space-y-5">

          <!-- Identificação -->
          <p class="text-xs uppercase tracking-wide text-gray-500">Identificação</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Nome / Razão Social *</label>
              <input type="text" v-model="form.nome_razao_social" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Nome Fantasia / Apelido</label>
              <input type="text" v-model="form.nome_fantasia_apelido"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Tipo de Pessoa *</label>
              <select v-model="form.tipo_pessoa" required
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option value="PF">Pessoa Física</option>
                <option value="PJ">Pessoa Jurídica</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CPF / CNPJ *</label>
              <input type="text" v-model="form.documento" required
                     :placeholder="form.tipo_pessoa === 'PF' ? '000.000.000-00' : '00.000.000/0000-00'"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Inscrição Estadual</label>
              <input type="text" v-model="form.inscricao_estadual"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Indicador IE</label>
              <select v-model="form.indicador_ie"
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option value="1">Contribuinte ICMS</option>
                <option value="2">Contribuinte Isento</option>
                <option value="9">Não Contribuinte</option>
              </select>
            </div>
          </div>

          <!-- Contato -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Contato</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">E-mail</label>
              <input type="email" v-model="form.email"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Telefone</label>
              <input type="text" v-model="form.telefone"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <!-- Endereço -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Endereço</p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">CEP</label>
              <div class="flex gap-2">
                <input type="text" v-model="form.cep" maxlength="9" placeholder="00000-000"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
                <button type="button" @click="buscarCep" :disabled="loadingCep"
                        class="px-3 py-2 bg-ancora-navy border border-ancora-gold/40 rounded-md text-ancora-gold text-sm hover:bg-ancora-gold/10 transition-colors whitespace-nowrap disabled:opacity-50">
                  {{ loadingCep ? '...' : 'Buscar' }}
                </button>
              </div>
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Logradouro</label>
              <input type="text" v-model="form.logradouro"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Número</label>
              <input type="text" v-model="form.numero"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Complemento</label>
              <input type="text" v-model="form.complemento"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Bairro</label>
              <input type="text" v-model="form.bairro"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Município</label>
              <input type="text" v-model="form.municipio"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">UF</label>
              <input type="text" v-model="form.uf" maxlength="2"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <!-- Comercial -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Comercial</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Limite de Crédito (R$)</label>
              <input type="number" step="0.01" min="0" v-model="form.limite_credito"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div class="flex items-center gap-3 mt-5">
              <input type="checkbox" id="chk_ativo" v-model="form.ativo"
                     class="h-4 w-4 rounded border-ancora-gold/20 bg-ancora-black/70 text-ancora-gold"/>
              <label for="chk_ativo" class="text-sm text-gray-300">Ativo</label>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors disabled:opacity-50">
              {{ saving ? 'Salvando...' : 'Salvar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Confirmar Exclusão -->
    <div v-if="deleteModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-red-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-red-400 mb-2">Confirmar Exclusão</h3>
        <p class="text-sm text-gray-300 mb-4">
          Tem certeza que deseja excluir o cliente <span class="font-bold text-white">{{ deleteModal.nome }}</span>?
          Esta operação é reversível (soft delete).
        </p>
        <div class="flex justify-end gap-3">
          <button type="button" @click="deleteModal.open = false"
                  class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
          <button type="button" @click="confirmDelete" :disabled="saving"
                  class="px-4 py-2 bg-red-600 text-white font-bold rounded-md hover:bg-red-700 transition-colors disabled:opacity-50">
            {{ saving ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useEmpresaStore } from '@/stores/empresa'
import CadastrosService from '@/services/cadastros.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()
const empresaStore = useEmpresaStore()

const clientes = ref([])
const loading = ref(false)
const saving = ref(false)
const loadingCep = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingCliente = ref(false)

const emptyForm = () => ({
  id: null,
  nome_razao_social: '',
  nome_fantasia_apelido: '',
  tipo_pessoa: 'PF',
  documento: '',
  inscricao_estadual: '',
  indicador_ie: '9',
  email: '',
  telefone: '',
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  municipio: '',
  uf: '',
  limite_credito: 0,
  ativo: true,
})

const form = reactive(emptyForm())

const deleteModal = reactive({ open: false, id: null, nome: '' })

onMounted(() => {
  fetchClientes()
})

async function fetchClientes() {
  loading.value = true
  error.value = null
  try {
    const response = await CadastrosService.getClientes({ search: searchQuery.value })
    clientes.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar clientes.'
    uiStore.showNotification(error.value, 'error')
  } finally {
    loading.value = false
  }
}

function formatDocumento(doc, tipo) {
  if (!doc) return ''
  if (tipo === 'PF') return doc.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  if (tipo === 'PJ') return doc.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
  return doc
}

function openModalForCreate() {
  editingCliente.value = false
  Object.assign(form, emptyForm())
  isModalOpen.value = true
}

function openModalForEdit(cliente) {
  editingCliente.value = true
  Object.assign(form, emptyForm(), cliente)
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function buscarCep() {
  const cep = (form.cep || '').replace(/\D/g, '')
  if (cep.length !== 8) {
    uiStore.showNotification('Informe um CEP com 8 dígitos.', 'warning')
    return
  }
  loadingCep.value = true
  try {
    const data = await CadastrosService.buscarCep(cep)
    form.logradouro = data.logradouro || form.logradouro
    form.bairro = data.bairro || form.bairro
    form.municipio = data.localidade || data.municipio || form.municipio
    form.uf = data.uf || form.uf
  } catch {
    uiStore.showNotification('CEP não encontrado.', 'warning')
  } finally {
    loadingCep.value = false
  }
}

async function saveCliente() {
  saving.value = true
  try {
    const payload = { ...form, documento: (form.documento || '').replace(/\D/g, '') }
    if (editingCliente.value) {
      await CadastrosService.updateCliente(form.id, payload)
      uiStore.showNotification('Cliente atualizado com sucesso!', 'success')
    } else {
      await CadastrosService.createCliente(payload)
      uiStore.showNotification('Cliente criado com sucesso!', 'success')
    }
    closeModal()
    await fetchClientes()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar cliente.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

function openDeleteModal(cliente) {
  deleteModal.open = true
  deleteModal.id = cliente.id
  deleteModal.nome = cliente.nome_razao_social
}

async function confirmDelete() {
  saving.value = true
  try {
    await CadastrosService.deleteCliente(deleteModal.id)
    uiStore.showNotification('Cliente excluído com sucesso!', 'success')
    deleteModal.open = false
    await fetchClientes()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao excluir cliente.'), 'error')
  } finally {
    saving.value = false
  }
}
</script>
