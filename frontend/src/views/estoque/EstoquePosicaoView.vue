<template>
  <div class="p-4">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Posição de Estoque</h1>
        <p class="text-sm text-gray-400">Saldo atual de produtos da empresa ativa.</p>
      </div>
    </div>

    <!-- Filtro -->
    <div class="mb-4">
      <input
        v-model="search"
        @input="fetchPosicao"
        type="text"
        placeholder="Buscar por código ou descrição..."
        class="w-full max-w-sm px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:border-ancora-gold/60"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-400 text-sm py-8 text-center">Carregando...</div>

    <!-- Tabela -->
    <div v-else class="overflow-x-auto rounded-xl border border-ancora-gold/20">
      <table class="min-w-full divide-y divide-ancora-gold/10">
        <thead class="bg-ancora-navy">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Código</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Descrição</th>
            <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Estoque Atual</th>
            <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Mínimo</th>
            <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Máximo</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-ancora-gold/10">
          <tr
            v-for="produto in produtos"
            :key="produto.id"
            :class="[
              'hover:bg-ancora-navy/30 transition-colors',
              produto.estoque_atual <= 0 ? 'bg-red-900/10' : produto.estoque_atual < produto.estoque_minimo ? 'bg-yellow-900/10' : ''
            ]"
          >
            <td class="px-4 py-3 text-sm text-gray-300">{{ produto.codigo_interno }}</td>
            <td class="px-4 py-3 text-sm text-white">{{ produto.descricao }}</td>
            <td class="px-4 py-3 text-sm text-right font-mono"
                :class="produto.estoque_atual <= 0 ? 'text-red-400' : produto.estoque_atual < produto.estoque_minimo ? 'text-yellow-400' : 'text-green-400'">
              {{ formatQtd(produto.estoque_atual) }}
            </td>
            <td class="px-4 py-3 text-sm text-right font-mono text-gray-400">{{ formatQtd(produto.estoque_minimo) }}</td>
            <td class="px-4 py-3 text-sm text-right font-mono text-gray-400">{{ formatQtd(produto.estoque_maximo) }}</td>
            <td class="px-4 py-3 text-center">
              <span v-if="produto.estoque_atual <= 0"
                    class="px-2 py-0.5 text-xs rounded-full bg-red-900/50 text-red-300">ZERADO</span>
              <span v-else-if="produto.estoque_atual < produto.estoque_minimo"
                    class="px-2 py-0.5 text-xs rounded-full bg-yellow-900/50 text-yellow-300">CRÍTICO</span>
              <span v-else
                    class="px-2 py-0.5 text-xs rounded-full bg-green-900/50 text-green-300">OK</span>
            </td>
          </tr>
          <tr v-if="produtos.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-500 text-sm">Nenhum produto encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação simples -->
    <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between text-sm text-gray-400">
      <span>Página {{ currentPage }} de {{ totalPages }} ({{ totalCount }} produtos)</span>
      <div class="flex gap-2">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
                class="px-3 py-1 rounded border border-ancora-gold/20 disabled:opacity-40 hover:border-ancora-gold/60 transition-colors">
          Anterior
        </button>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages"
                class="px-3 py-1 rounded border border-ancora-gold/20 disabled:opacity-40 hover:border-ancora-gold/60 transition-colors">
          Próxima
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import estoqueService from '@/services/estoque.service'

const uiStore = useUiStore()

const produtos = ref([])
const loading = ref(false)
const search = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

async function fetchPosicao() {
  loading.value = true
  currentPage.value = 1
  try {
    const params = {}
    if (search.value) params.search = search.value
    const data = await estoqueService.getPosicao(params)
    produtos.value = data.results ?? data
    totalCount.value = data.count ?? data.length
    totalPages.value = data.total_pages ?? 1
  } catch (e) {
    uiStore.showNotification('Erro ao carregar posição de estoque.', 'error')
  } finally {
    loading.value = false
  }
}

async function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loading.value = true
  try {
    const params = { page }
    if (search.value) params.search = search.value
    const data = await estoqueService.getPosicao(params)
    produtos.value = data.results ?? data
  } catch (e) {
    uiStore.showNotification('Erro ao carregar página.', 'error')
  } finally {
    loading.value = false
  }
}

function formatQtd(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })
}

onMounted(fetchPosicao)
</script>
