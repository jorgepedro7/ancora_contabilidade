<template>
  <div class="p-4">
    <h1 class="text-3xl font-display text-ancora-gold mb-6">Produtos</h1>

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
          <th class="py-3 px-6 text-right">Preço Venda</th>
          <th class="py-3 px-6 text-right">Estoque</th>
          <th class="py-3 px-6 text-left">Ativo</th>
          <th class="py-3 px-6 text-center">Ações</th>
        </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
        <tr v-for="produto in produtos" :key="produto.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
          <td class="py-3 px-6 text-left whitespace-nowrap">{{ produto.descricao }}</td>
          <td class="py-3 px-6 text-left">{{ produto.codigo_interno }}</td>
          <td class="py-3 px-6 text-left">{{ produto.ncm }}</td>
          <td class="py-3 px-6 text-right">{{ formatCurrency(produto.preco_venda) }}</td>
          <td class="py-3 px-6 text-right">{{ produto.estoque_atual }}</td>
          <td class="py-3 px-6 text-left">
            <span :class="produto.ativo ? 'bg-green-500' : 'bg-red-500'" class="px-2 py-1 rounded-full text-xs text-white">
              {{ produto.ativo ? 'Sim' : 'Não' }}
            </span>
          </td>
          <td class="py-3 px-6 text-center">
            <button @click="openModalForEdit(produto)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-3">Editar</button>
            <button @click="deleteProduto(produto.id)" class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhum produto encontrado.
    </div>

    <!-- Modal para Adicionar/Editar Produto -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/70 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 p-8 shadow-xl">
        <h2 class="text-2xl font-display text-ancora-gold mb-4">{{ editingProduto ? 'Editar Produto' : 'Novo Produto' }}</h2>
        <form @submit.prevent="saveProduto" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="modal_descricao" class="block text-sm font-body text-gray-300">Descrição</label>
              <input type="text" id="modal_descricao" v-model="currentProduto.descricao" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_codigo_interno" class="block text-sm font-body text-gray-300">Cód. Interno</label>
              <input type="text" id="modal_codigo_interno" v-model="currentProduto.codigo_interno"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_ean" class="block text-sm font-body text-gray-300">EAN/GTIN</label>
              <input type="text" id="modal_ean" v-model="currentProduto.ean"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_ncm" class="block text-sm font-body text-gray-300">NCM</label>
              <input type="text" id="modal_ncm" v-model="currentProduto.ncm" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_preco_venda" class="block text-sm font-body text-gray-300">Preço Venda</label>
              <input type="number" step="0.01" id="modal_preco_venda" v-model="currentProduto.preco_venda" required
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div>
              <label for="modal_preco_custo" class="block text-sm font-body text-gray-300">Preço Custo</label>
              <input type="number" step="0.01" id="modal_preco_custo" v-model="currentProduto.preco_custo"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="modal_controla_estoque" v-model="currentProduto.controla_estoque"
                     class="form-checkbox h-4 w-4 text-ancora-gold transition duration-150 ease-in-out bg-ancora-black/70 border-ancora-gold/20 rounded"/>
              <label for="modal_controla_estoque" class="text-sm font-body text-gray-300">Controla Estoque</label>
            </div>
            <div v-if="currentProduto.controla_estoque">
              <label for="modal_estoque_minimo" class="block text-sm font-body text-gray-300">Estoque Mínimo</label>
              <input type="number" step="0.001" id="modal_estoque_minimo" v-model="currentProduto.estoque_minimo"
                     class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"/>
            </div>
          </div>
          
          <div class="flex justify-end space-x-4">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="uiStore.isLoading"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
              <span v-if="uiStore.isLoading">Salvando...</span>
              <span v-else>Salvar Produto</span>
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
import CadastrosService from '@/services/cadastros.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()

const produtos = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingProduto = ref(false)
const currentProduto = ref({
  id: null,
  descricao: '',
  codigo_interno: '',
  ean: '',
  ncm: '',
  origem: '0',
  preco_custo: 0,
  preco_venda: 0,
  estoque_minimo: 0,
  controla_estoque: true,
  // Outros campos fiscais e de peso/dimensões podem ser adicionados
})

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
    console.error('Erro ao carregar produtos:', err)
  } finally {
    loading.value = false
  }
}

function openModalForCreate() {
  editingProduto.value = false
  currentProduto.value = {
    id: null,
    descricao: '',
    codigo_interno: '',
    ean: '',
    ncm: '',
    origem: '0',
    preco_custo: 0,
    preco_venda: 0,
    estoque_minimo: 0,
    controla_estoque: true,
  }
  isModalOpen.value = true
}

function openModalForEdit(produto) {
  editingProduto.value = true
  currentProduto.value = { ...produto } // Cria uma cópia para edição
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveProduto() {
  uiStore.setLoading(true)
  try {
    if (editingProduto.value) {
      await CadastrosService.updateProduto(currentProduto.value.id, currentProduto.value)
      uiStore.showNotification('Produto atualizado com sucesso!', 'success')
    } else {
      await CadastrosService.createProduto(currentProduto.value)
      uiStore.showNotification('Produto criado com sucesso!', 'success')
    }
    closeModal()
    await fetchProdutos()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar produto.'), 'error', 6000)
    console.error('Erro ao salvar produto:', err)
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteProduto(id) {
  if (confirm('Tem certeza que deseja excluir este produto? (Soft delete)')) {
    uiStore.setLoading(true)
    try {
      await CadastrosService.deleteProduto(id)
      uiStore.showNotification('Produto excluído com sucesso!', 'success')
      await fetchProdutos()
    } catch (err) {
      uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao excluir produto.'), 'error')
      console.error('Erro ao excluir produto:', err)
    } finally {
      uiStore.setLoading(false)
    }
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}
</script>
