<template>
  <div class="p-4">
    <div class="mb-6">
      <h1 class="text-3xl font-display text-ancora-gold mb-2">Produtos</h1>
      <p class="text-gray-400">Catálogo de produtos da empresa-cliente ativa.</p>
    </div>

    <div v-if="loading" class="text-center text-gray-400">Carregando produtos...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div class="mb-6 flex justify-between items-center">
      <input type="text" v-model="searchQuery" @input="fetchProdutos" placeholder="Buscar produto por descrição ou código..."
             class="flex-1 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
      <button @click="openModalForCreate"
              class="ml-4 px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        Novo Produto
      </button>
    </div>

    <div v-if="produtos.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
        <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
          <th class="py-3 px-6 text-left">Descrição</th>
          <th class="py-3 px-6 text-left">Cód. Interno</th>
          <th class="py-3 px-6 text-left">NCM</th>
          <th class="py-3 px-6 text-left">Origem</th>
          <th class="py-3 px-6 text-right">Preço Venda</th>
          <th class="py-3 px-6 text-right">Estoque</th>
          <th class="py-3 px-6 text-left">Ativo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="produto in produtos" :key="produto.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ produto.descricao }}</td>
          <td class="py-3 px-6 text-left">{{ produto.codigo_interno || '-' }}</td>
          <td class="py-3 px-6 text-left">{{ produto.ncm }}</td>
          <td class="py-3 px-6 text-left">{{ origemLabel(produto.origem) }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(produto.preco_venda) }}</td>
          <td class="py-3 px-6 text-right">{{ produto.estoque_atual }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="produto.ativo ? 'bg-green-500' : 'bg-red-500'" class="px-2 py-1 rounded-full text-xs text-white">
              {{ produto.ativo ? 'Sim' : 'Não' }}
            </span>
          </td>
          <td class="py-3 px-6 text-center">
            <button @click="openModalForEdit(produto)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="openDeleteModal(produto)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum produto encontrado.
    </div>

    <!-- Modal Criar/Editar Produto -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-6">{{ editingProduto ? 'Editar Produto' : 'Novo Produto' }}</h2>
        <form @submit.prevent="saveProduto" class="space-y-5">

          <!-- Identificação -->
          <p class="text-xs uppercase tracking-wide text-gray-500">Identificação</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Descrição *</label>
              <input type="text" v-model="form.descricao" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Código Interno</label>
              <input type="text" v-model="form.codigo_interno"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">EAN / GTIN</label>
              <input type="text" v-model="form.ean" maxlength="14"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <!-- Fiscal -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Dados Fiscais</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">NCM *</label>
              <input type="text" v-model="form.ncm" required maxlength="8"
                     placeholder="00000000"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CEST</label>
              <input type="text" v-model="form.cest" maxlength="7"
                     placeholder="0000000"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CFOP Padrão</label>
              <input type="text" v-model="form.cfop_padrao" maxlength="4"
                     placeholder="5102"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Origem</label>
              <select v-model="form.origem"
                      class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
                <option value="0">0 - Nacional</option>
                <option value="1">1 - Estrangeira (Importação Direta)</option>
                <option value="2">2 - Estrangeira (Mercado Interno)</option>
                <option value="3">3 - Nacional, Importação 40–70%</option>
                <option value="4">4 - Nacional, Processos Produtivos Básicos</option>
                <option value="5">5 - Nacional, Importação ≤ 40%</option>
                <option value="6">6 - Estrangeira (Importação Direta, sem similar)</option>
                <option value="7">7 - Estrangeira (Mercado Interno, sem similar)</option>
                <option value="8">8 - Nacional, Importação > 70%</option>
              </select>
            </div>
          </div>

          <!-- Preços -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Preços</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Preço Venda (R$) *</label>
              <input type="number" step="0.01" min="0" v-model="form.preco_venda" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Preço Custo (R$)</label>
              <input type="number" step="0.01" min="0" v-model="form.preco_custo"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <!-- Estoque -->
          <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Estoque</p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="md:col-span-3 flex items-center gap-3">
              <input type="checkbox" id="chk_controla_estoque" v-model="form.controla_estoque"
                     class="h-4 w-4 rounded border-ancora-gold/20 bg-ancora-black/70 text-ancora-gold"/>
              <label for="chk_controla_estoque" class="text-sm text-gray-300">Controla Estoque</label>
            </div>
            <div v-if="form.controla_estoque">
              <label class="block text-sm text-gray-300 mb-1">Estoque Mínimo</label>
              <input type="number" step="0.001" min="0" v-model="form.estoque_minimo"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div v-if="form.controla_estoque">
              <label class="block text-sm text-gray-300 mb-1">Estoque Máximo</label>
              <input type="number" step="0.001" min="0" v-model="form.estoque_maximo"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <div class="flex items-center gap-3 pt-1">
            <input type="checkbox" id="chk_ativo_prod" v-model="form.ativo"
                   class="h-4 w-4 rounded border-ancora-gold/20 bg-ancora-black/70 text-ancora-gold"/>
            <label for="chk_ativo_prod" class="text-sm text-gray-300">Ativo</label>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors disabled:opacity-50">
              {{ saving ? 'Salvando...' : 'Salvar Produto' }}
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
          Tem certeza que deseja excluir o produto <span class="font-bold text-white">{{ deleteModal.descricao }}</span>?
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
import CadastrosService from '@/services/cadastros.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()

const produtos = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingProduto = ref(false)

const emptyForm = () => ({
  id: null,
  descricao: '',
  codigo_interno: '',
  ean: '',
  ncm: '',
  cest: '',
  cfop_padrao: '',
  origem: '0',
  preco_venda: 0,
  preco_custo: 0,
  controla_estoque: true,
  estoque_minimo: 0,
  estoque_maximo: 0,
  ativo: true,
})

const form = reactive(emptyForm())

const deleteModal = reactive({ open: false, id: null, descricao: '' })

const ORIGENS = {
  '0': 'Nacional',
  '1': 'Estrangeira (Import. Direta)',
  '2': 'Estrangeira (Merc. Interno)',
  '3': 'Nacional (Import. 40-70%)',
  '4': 'Nacional (PPB)',
  '5': 'Nacional (Import. ≤40%)',
  '6': 'Estrang. Direta s/ similar',
  '7': 'Estrang. Interna s/ similar',
  '8': 'Nacional (Import. >70%)',
}

function origemLabel(valor) {
  return ORIGENS[valor] || valor || '-'
}

onMounted(() => {
  fetchProdutos()
})

async function fetchProdutos() {
  loading.value = true
  error.value = null
  try {
    const response = await CadastrosService.getProdutos({ search: searchQuery.value })
    produtos.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar produtos.'
    uiStore.showNotification(error.value, 'error')
  } finally {
    loading.value = false
  }
}

function openModalForCreate() {
  editingProduto.value = false
  Object.assign(form, emptyForm())
  isModalOpen.value = true
}

function openModalForEdit(produto) {
  editingProduto.value = true
  Object.assign(form, emptyForm(), produto)
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveProduto() {
  saving.value = true
  try {
    if (editingProduto.value) {
      await CadastrosService.updateProduto(form.id, { ...form })
      uiStore.showNotification('Produto atualizado com sucesso!', 'success')
    } else {
      await CadastrosService.createProduto({ ...form })
      uiStore.showNotification('Produto criado com sucesso!', 'success')
    }
    closeModal()
    await fetchProdutos()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar produto.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

function openDeleteModal(produto) {
  deleteModal.open = true
  deleteModal.id = produto.id
  deleteModal.descricao = produto.descricao
}

async function confirmDelete() {
  saving.value = true
  try {
    await CadastrosService.deleteProduto(deleteModal.id)
    uiStore.showNotification('Produto excluído com sucesso!', 'success')
    deleteModal.open = false
    await fetchProdutos()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao excluir produto.'), 'error')
  } finally {
    saving.value = false
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0)
}
</script>
