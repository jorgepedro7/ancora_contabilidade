<template>
  <div class="p-4">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Movimentações de Estoque</h1>
        <p class="text-sm text-gray-400">Entradas, saídas e ajustes de produtos.</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button @click="openModal('ENTRADA')"
                class="px-4 py-2 bg-green-700 text-white text-sm font-semibold rounded-md hover:bg-green-600 transition-colors">
          Nova Entrada
        </button>
        <button @click="openModal('SAIDA')"
                class="px-4 py-2 bg-red-700 text-white text-sm font-semibold rounded-md hover:bg-red-600 transition-colors">
          Nova Saída
        </button>
        <button @click="openModal('AJUSTE')"
                class="px-4 py-2 bg-ancora-gold text-ancora-black text-sm font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
          Ajuste
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="mb-4 flex flex-wrap gap-3">
      <select v-model="filterTipo" @change="fetchMovimentacoes"
              class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm">
        <option value="">Todos os tipos</option>
        <option value="ENTRADA">Entrada</option>
        <option value="SAIDA">Saída</option>
        <option value="AJUSTE">Ajuste</option>
        <option value="TRANSFERENCIA">Transferência</option>
        <option value="INVENTARIO">Inventário</option>
      </select>
      <input v-model="search" @input="fetchMovimentacoes" type="text"
             placeholder="Buscar produto..."
             class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:border-ancora-gold/60" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-400 text-sm py-8 text-center">Carregando...</div>

    <!-- Tabela -->
    <div v-else class="overflow-x-auto rounded-xl border border-ancora-gold/20">
      <table class="min-w-full divide-y divide-ancora-gold/10">
        <thead class="bg-ancora-navy">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Data</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Tipo</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Produto</th>
            <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Quantidade</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Origem</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Destino</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Observações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-ancora-gold/10">
          <tr v-for="mov in movimentacoes" :key="mov.id" class="hover:bg-ancora-navy/30 transition-colors">
            <td class="px-4 py-3 text-sm text-gray-300 whitespace-nowrap">{{ formatDate(mov.data_movimentacao) }}</td>
            <td class="px-4 py-3">
              <span :class="tipoBadgeClass(mov.tipo_movimentacao)"
                    class="px-2 py-0.5 text-xs rounded-full font-medium">
                {{ mov.tipo_movimentacao }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-white">{{ mov.produto_detail?.descricao ?? mov.produto }}</td>
            <td class="px-4 py-3 text-sm text-right font-mono text-gray-200">{{ formatQtd(mov.quantidade) }}</td>
            <td class="px-4 py-3 text-sm text-gray-400">{{ mov.local_origem_detail?.nome ?? '—' }}</td>
            <td class="px-4 py-3 text-sm text-gray-400">{{ mov.local_destino_detail?.nome ?? '—' }}</td>
            <td class="px-4 py-3 text-sm text-gray-400 max-w-xs truncate">{{ mov.observacoes ?? '—' }}</td>
          </tr>
          <tr v-if="movimentacoes.length === 0">
            <td colspan="7" class="px-4 py-8 text-center text-gray-500 text-sm">Nenhuma movimentação encontrada.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between text-sm text-gray-400">
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
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

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div class="bg-ancora-navy border border-ancora-gold/30 rounded-2xl p-6 w-full max-w-md shadow-xl">
        <h2 class="text-xl font-display text-ancora-gold mb-5">
          {{ modalTipo === 'ENTRADA' ? 'Nova Entrada' : modalTipo === 'SAIDA' ? 'Nova Saída' : 'Ajuste de Estoque' }}
        </h2>

        <div class="space-y-4">
          <!-- Produto -->
          <div>
            <label class="block text-sm text-gray-300 mb-1">Produto</label>
            <select v-model="form.produto"
                    class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60">
              <option value="">Selecione um produto</option>
              <option v-for="p in produtos" :key="p.id" :value="p.id">
                {{ p.codigo_interno }} — {{ p.descricao }}
              </option>
            </select>
          </div>

          <!-- Quantidade / Delta -->
          <div>
            <label class="block text-sm text-gray-300 mb-1">
              {{ modalTipo === 'AJUSTE' ? 'Delta (positivo = acréscimo, negativo = decréscimo)' : 'Quantidade' }}
            </label>
            <input v-model="form.quantidade" type="number" step="0.001"
                   :placeholder="modalTipo === 'AJUSTE' ? 'Ex: -5 ou 10' : 'Ex: 50'"
                   class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60" />
          </div>

          <!-- Local Destino (Entrada) -->
          <div v-if="modalTipo === 'ENTRADA'">
            <label class="block text-sm text-gray-300 mb-1">Local de Destino</label>
            <select v-model="form.local_destino"
                    class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60">
              <option value="">Selecione o local</option>
              <option v-for="l in locais" :key="l.id" :value="l.id">{{ l.nome }}</option>
            </select>
          </div>

          <!-- Local Origem (Saída) -->
          <div v-if="modalTipo === 'SAIDA'">
            <label class="block text-sm text-gray-300 mb-1">Local de Origem</label>
            <select v-model="form.local_origem"
                    class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60">
              <option value="">Selecione o local</option>
              <option v-for="l in locais" :key="l.id" :value="l.id">{{ l.nome }}</option>
            </select>
          </div>

          <!-- Observações -->
          <div>
            <label class="block text-sm text-gray-300 mb-1">Observações</label>
            <textarea v-model="form.observacoes" rows="2"
                      class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm focus:outline-none focus:border-ancora-gold/60 resize-none"
                      placeholder="Opcional..."></textarea>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button @click="closeModal"
                  class="px-4 py-2 text-sm border border-ancora-gold/30 text-gray-300 rounded-md hover:border-ancora-gold/60 transition-colors">
            Cancelar
          </button>
          <button @click="submitForm" :disabled="submitting"
                  class="px-4 py-2 text-sm bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors disabled:opacity-50">
            {{ submitting ? 'Salvando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import estoqueService from '@/services/estoque.service'
import cadastrosService from '@/services/cadastros.service'

const uiStore = useUiStore()

const movimentacoes = ref([])
const produtos = ref([])
const locais = ref([])
const loading = ref(false)
const submitting = ref(false)
const filterTipo = ref('')
const search = ref('')
const currentPage = ref(1)
const totalPages = ref(1)

const showModal = ref(false)
const modalTipo = ref('ENTRADA')
const form = ref({ produto: '', quantidade: '', local_destino: '', local_origem: '', observacoes: '' })

async function fetchMovimentacoes() {
  loading.value = true
  currentPage.value = 1
  try {
    const params = {}
    if (filterTipo.value) params.tipo_movimentacao = filterTipo.value
    if (search.value) params.search = search.value
    const data = await estoqueService.listarMovimentacoes(params)
    movimentacoes.value = data.results ?? data
    totalPages.value = data.total_pages ?? 1
  } catch (e) {
    uiStore.showNotification('Erro ao carregar movimentações.', 'error')
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
    if (filterTipo.value) params.tipo_movimentacao = filterTipo.value
    if (search.value) params.search = search.value
    const data = await estoqueService.listarMovimentacoes(params)
    movimentacoes.value = data.results ?? data
    totalPages.value = data.total_pages ?? totalPages.value
  } catch (e) {
    uiStore.showNotification('Erro ao carregar página.', 'error')
  } finally {
    loading.value = false
  }
}

async function fetchSupport() {
  try {
    const [prod, loc] = await Promise.all([
      cadastrosService.getProdutos(),
      estoqueService.listarLocais(),
    ])
    produtos.value = prod.results ?? prod
    locais.value = loc.results ?? loc
  } catch (e) {
    // silencioso — campos opcionais do modal
  }
}

function openModal(tipo) {
  modalTipo.value = tipo
  form.value = { produto: '', quantidade: '', local_destino: '', local_origem: '', observacoes: '' }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function submitForm() {
  if (!form.value.produto || !form.value.quantidade) {
    uiStore.showNotification('Produto e quantidade são obrigatórios.', 'error')
    return
  }
  if (modalTipo.value === 'ENTRADA' && !form.value.local_destino) {
    uiStore.showNotification('Local de destino é obrigatório para entrada.', 'error')
    return
  }
  if (modalTipo.value === 'SAIDA' && !form.value.local_origem) {
    uiStore.showNotification('Local de origem é obrigatório para saída.', 'error')
    return
  }
  submitting.value = true
  try {
    const payload = {
      produto: form.value.produto,
      quantidade: form.value.quantidade,
      observacoes: form.value.observacoes || null,
    }
    if (modalTipo.value === 'ENTRADA') {
      payload.local_destino = form.value.local_destino
      await estoqueService.registrarEntrada(payload)
    } else if (modalTipo.value === 'SAIDA') {
      payload.local_origem = form.value.local_origem
      await estoqueService.registrarSaida(payload)
    } else {
      await estoqueService.registrarAjuste(payload)
    }
    uiStore.showNotification('Movimentação registrada com sucesso!', 'success')
    closeModal()
    fetchMovimentacoes()
  } catch (e) {
    const msg = e.response?.data?.error || e.response?.data?.message || 'Erro ao registrar movimentação.'
    uiStore.showNotification(msg, 'error')
  } finally {
    submitting.value = false
  }
}

function tipoBadgeClass(tipo) {
  const map = {
    ENTRADA: 'bg-green-900/60 text-green-300',
    SAIDA: 'bg-red-900/60 text-red-300',
    AJUSTE: 'bg-yellow-900/60 text-yellow-300',
    TRANSFERENCIA: 'bg-blue-900/60 text-blue-300',
    INVENTARIO: 'bg-gray-700/60 text-gray-300',
  }
  return map[tipo] ?? 'bg-gray-700/60 text-gray-300'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatQtd(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })
}

onMounted(() => {
  fetchMovimentacoes()
  fetchSupport()
})
</script>
