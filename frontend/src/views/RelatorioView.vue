<template>
  <div class="p-6 space-y-8">
    <h1 class="text-3xl font-display text-ancora-gold">Central de Relatórios</h1>

    <div v-if="!empresaStore.activeEmpresa" class="p-4 border border-red-500/30 rounded-lg bg-red-500/10 text-red-200">
      Selecione uma empresa-cliente para visualizar os relatórios.
    </div>

    <template v-else>
      <!-- Atalhos rápidos -->
      <section>
        <h2 class="text-lg font-semibold text-gray-300 mb-3">Relatórios disponíveis</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
          <button
            v-for="rel in relatorios"
            :key="rel.id"
            @click="abrirRelatorio(rel.id)"
            class="p-4 rounded-lg border border-ancora-gold/20 bg-ancora-black/40 hover:border-ancora-gold/60 hover:bg-ancora-navy/40 transition-colors text-left"
            :class="{ 'border-ancora-gold bg-ancora-navy/50': relatorioAtivo === rel.id }"
          >
            <div class="text-2xl mb-2">{{ rel.icone }}</div>
            <p class="text-sm font-semibold text-white">{{ rel.nome }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ rel.descricao }}</p>
          </button>
        </div>
      </section>

      <!-- DRE -->
      <section v-if="relatorioAtivo === 'dre'" class="bg-ancora-black/40 border border-ancora-gold/20 rounded-xl p-6 space-y-4">
        <div class="flex flex-wrap items-end gap-4">
          <div>
            <label class="block text-xs text-gray-400 mb-1">Data início</label>
            <input v-model="dre.dataInicio" type="date" class="bg-ancora-navy/60 border border-ancora-gold/30 text-white rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Data fim</label>
            <input v-model="dre.dataFim" type="date" class="bg-ancora-navy/60 border border-ancora-gold/30 text-white rounded px-3 py-2 text-sm" />
          </div>
          <button @click="carregarDRE" :disabled="loading" class="px-5 py-2 bg-ancora-gold text-ancora-black font-bold rounded hover:bg-ancora-gold/80 disabled:opacity-50">
            Gerar DRE
          </button>
        </div>

        <div v-if="dre.dados" class="space-y-4">
          <div class="grid grid-cols-3 gap-4">
            <div class="p-4 rounded-lg border border-green-500/30 bg-green-500/10">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Receita Bruta</p>
              <p class="text-xl font-bold text-green-300 mt-1">{{ formatCurrency(dre.dados.receita_bruta) }}</p>
            </div>
            <div class="p-4 rounded-lg border border-red-500/30 bg-red-500/10">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Total Despesas</p>
              <p class="text-xl font-bold text-red-300 mt-1">{{ formatCurrency(dre.dados.total_despesas) }}</p>
            </div>
            <div class="p-4 rounded-lg border"
              :class="parseFloat(dre.dados.resultado_liquido) >= 0 ? 'border-ancora-gold/40 bg-ancora-gold/10' : 'border-red-500/30 bg-red-500/10'">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Resultado Líquido</p>
              <p class="text-xl font-bold mt-1" :class="parseFloat(dre.dados.resultado_liquido) >= 0 ? 'text-ancora-gold' : 'text-red-300'">
                {{ formatCurrency(dre.dados.resultado_liquido) }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 class="text-sm font-semibold text-green-300 mb-2">Receitas por conta</h3>
              <table class="w-full text-sm">
                <tr v-for="r in dre.dados.receitas_por_conta" :key="r.conta" class="border-b border-ancora-gold/10">
                  <td class="py-1 text-gray-300">{{ r.conta }}</td>
                  <td class="py-1 text-right text-green-300">{{ formatCurrency(r.total) }}</td>
                </tr>
              </table>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-red-300 mb-2">Despesas por conta</h3>
              <table class="w-full text-sm">
                <tr v-for="r in dre.dados.despesas_por_conta" :key="r.conta" class="border-b border-ancora-gold/10">
                  <td class="py-1 text-gray-300">{{ r.conta }}</td>
                  <td class="py-1 text-right text-red-300">{{ formatCurrency(r.total) }}</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- Livro Fiscal -->
      <section v-if="relatorioAtivo === 'livro-fiscal'" class="bg-ancora-black/40 border border-ancora-gold/20 rounded-xl p-6 space-y-4">
        <div class="flex flex-wrap items-end gap-4">
          <div>
            <label class="block text-xs text-gray-400 mb-1">Data início</label>
            <input v-model="livro.dataInicio" type="date" class="bg-ancora-navy/60 border border-ancora-gold/30 text-white rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Data fim</label>
            <input v-model="livro.dataFim" type="date" class="bg-ancora-navy/60 border border-ancora-gold/30 text-white rounded px-3 py-2 text-sm" />
          </div>
          <button @click="carregarLivroFiscal" :disabled="loading" class="px-5 py-2 bg-ancora-gold text-ancora-black font-bold rounded hover:bg-ancora-gold/80 disabled:opacity-50">
            Consultar
          </button>
        </div>

        <div v-if="livro.dados">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Notas emitidas</p>
              <p class="text-xl font-bold text-white">{{ livro.dados.totais.quantidade }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Total produtos</p>
              <p class="text-lg font-bold text-white">{{ formatCurrency(livro.dados.totais.total_produtos) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Total ICMS</p>
              <p class="text-lg font-bold text-white">{{ formatCurrency(livro.dados.totais.total_icms) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Total NF</p>
              <p class="text-lg font-bold text-ancora-gold">{{ formatCurrency(livro.dados.totais.total_nf) }}</p>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-ancora-navy">
                <tr>
                  <th class="px-3 py-2 text-left text-gray-400">Nº/Série</th>
                  <th class="px-3 py-2 text-left text-gray-400">Emissão</th>
                  <th class="px-3 py-2 text-left text-gray-400">Destinatário</th>
                  <th class="px-3 py-2 text-right text-gray-400">Produtos</th>
                  <th class="px-3 py-2 text-right text-gray-400">ICMS</th>
                  <th class="px-3 py-2 text-right text-gray-400">Total NF</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="n in livro.dados.registros" :key="n.numero" class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20">
                  <td class="px-3 py-2 text-gray-300">{{ n.numero }}/{{ n.serie }}</td>
                  <td class="px-3 py-2 text-gray-300">{{ formatDate(n.data_emissao) }}</td>
                  <td class="px-3 py-2 text-gray-300">{{ n.destinatario_nome }}</td>
                  <td class="px-3 py-2 text-right text-gray-300">{{ formatCurrency(n.valor_produtos) }}</td>
                  <td class="px-3 py-2 text-right text-gray-300">{{ formatCurrency(n.valor_icms) }}</td>
                  <td class="px-3 py-2 text-right text-ancora-gold font-semibold">{{ formatCurrency(n.valor_total_nf) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Posição de Estoque -->
      <section v-if="relatorioAtivo === 'estoque'" class="bg-ancora-black/40 border border-ancora-gold/20 rounded-xl p-6 space-y-4">
        <button @click="carregarEstoque" :disabled="loading" class="px-5 py-2 bg-ancora-gold text-ancora-black font-bold rounded hover:bg-ancora-gold/80 disabled:opacity-50">
          Atualizar posição
        </button>

        <div v-if="estoque.dados">
          <div class="flex gap-4 mb-4">
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Total de produtos</p>
              <p class="text-xl font-bold text-white">{{ estoque.dados.total_produtos }}</p>
            </div>
            <div class="p-3 rounded-lg border border-red-500/30 bg-red-500/10">
              <p class="text-xs text-gray-400">Abaixo do mínimo</p>
              <p class="text-xl font-bold text-red-300">{{ estoque.dados.produtos_abaixo_minimo }}</p>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-ancora-navy">
                <tr>
                  <th class="px-3 py-2 text-left text-gray-400">Código</th>
                  <th class="px-3 py-2 text-left text-gray-400">Produto</th>
                  <th class="px-3 py-2 text-right text-gray-400">Atual</th>
                  <th class="px-3 py-2 text-right text-gray-400">Mínimo</th>
                  <th class="px-3 py-2 text-right text-gray-400">Custo</th>
                  <th class="px-3 py-2 text-right text-gray-400">Venda</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in estoque.dados.produtos" :key="p.id"
                  class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20"
                  :class="{ 'bg-red-500/5': p.alerta_minimo }">
                  <td class="px-3 py-2 text-gray-400 font-mono text-xs">{{ p.codigo_interno || '-' }}</td>
                  <td class="px-3 py-2 text-gray-200">
                    {{ p.descricao }}
                    <span v-if="p.alerta_minimo" class="ml-2 text-xs text-red-400">⚠ abaixo do mínimo</span>
                  </td>
                  <td class="px-3 py-2 text-right" :class="p.alerta_minimo ? 'text-red-300' : 'text-gray-300'">{{ p.estoque_atual }}</td>
                  <td class="px-3 py-2 text-right text-gray-400">{{ p.estoque_minimo }}</td>
                  <td class="px-3 py-2 text-right text-gray-300">{{ formatCurrency(p.preco_custo) }}</td>
                  <td class="px-3 py-2 text-right text-ancora-gold">{{ formatCurrency(p.preco_venda) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Folha por Competência -->
      <section v-if="relatorioAtivo === 'folha'" class="bg-ancora-black/40 border border-ancora-gold/20 rounded-xl p-6 space-y-4">
        <div class="flex flex-wrap items-end gap-4">
          <div>
            <label class="block text-xs text-gray-400 mb-1">Competência</label>
            <input v-model="folha.competencia" type="month" class="bg-ancora-navy/60 border border-ancora-gold/30 text-white rounded px-3 py-2 text-sm" />
          </div>
          <button @click="carregarFolha" :disabled="loading" class="px-5 py-2 bg-ancora-gold text-ancora-black font-bold rounded hover:bg-ancora-gold/80 disabled:opacity-50">
            Consultar
          </button>
        </div>

        <div v-if="folha.dados" class="space-y-3">
          <p class="text-sm text-gray-400">
            Competência: <span class="text-white font-semibold">{{ folha.dados.competencia }}</span>
            — {{ folha.dados.folhas_abertas }} folha(s) encontrada(s)
          </p>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Funcionários</p>
              <p class="text-xl font-bold text-white">{{ folha.dados.resumo.funcionarios }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/20 bg-ancora-navy/20">
              <p class="text-xs text-gray-400">Total bruto</p>
              <p class="text-lg font-bold text-white">{{ formatCurrency(folha.dados.resumo.total_bruto) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-red-500/30 bg-red-500/10">
              <p class="text-xs text-gray-400">Descontos</p>
              <p class="text-lg font-bold text-red-300">{{ formatCurrency(folha.dados.resumo.total_descontos) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-green-500/30 bg-green-500/10">
              <p class="text-xs text-gray-400">Líquido a pagar</p>
              <p class="text-lg font-bold text-green-300">{{ formatCurrency(folha.dados.resumo.total_liquido) }}</p>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 text-sm">
            <div class="p-3 rounded-lg border border-ancora-gold/10 bg-ancora-black/30">
              <p class="text-gray-400">INSS total</p>
              <p class="text-white font-semibold">{{ formatCurrency(folha.dados.resumo.total_inss) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/10 bg-ancora-black/30">
              <p class="text-gray-400">IRRF total</p>
              <p class="text-white font-semibold">{{ formatCurrency(folha.dados.resumo.total_irrf) }}</p>
            </div>
            <div class="p-3 rounded-lg border border-ancora-gold/10 bg-ancora-black/30">
              <p class="text-gray-400">FGTS total</p>
              <p class="text-white font-semibold">{{ formatCurrency(folha.dados.resumo.total_fgts) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Relatórios Contábeis (links para módulo existente) -->
      <section v-if="relatorioAtivo === 'contabil'" class="bg-ancora-black/40 border border-ancora-gold/20 rounded-xl p-6 space-y-3">
        <p class="text-sm text-gray-400">Os relatórios contábeis completos estão disponíveis no módulo Contábil:</p>
        <div class="flex flex-wrap gap-3">
          <router-link to="/contabil/dre" class="px-4 py-2 border border-ancora-gold/40 rounded text-ancora-gold hover:bg-ancora-gold/10 transition-colors text-sm">
            DRE Completo
          </router-link>
          <router-link to="/contabil/balanco" class="px-4 py-2 border border-ancora-gold/40 rounded text-ancora-gold hover:bg-ancora-gold/10 transition-colors text-sm">
            Balanço Patrimonial
          </router-link>
          <router-link to="/contabil/lancamentos" class="px-4 py-2 border border-ancora-gold/40 rounded text-ancora-gold hover:bg-ancora-gold/10 transition-colors text-sm">
            Lançamentos Contábeis
          </router-link>
        </div>
      </section>

      <div v-if="error" class="p-4 border border-red-500/30 rounded-lg bg-red-500/10 text-red-200 text-sm">{{ error }}</div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useEmpresaStore } from '@/stores/empresa'
import RelatoriosService from '@/services/relatorios.service'

const empresaStore = useEmpresaStore()

const loading = ref(false)
const error = ref(null)
const relatorioAtivo = ref(null)

const hoje = new Date()
const inicioMes = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-01`
const fimMes = hoje.toISOString().split('T')[0]
const competenciaAtual = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`

const dre = ref({ dataInicio: inicioMes, dataFim: fimMes, dados: null })
const livro = ref({ dataInicio: inicioMes, dataFim: fimMes, dados: null })
const estoque = ref({ dados: null })
const folha = ref({ competencia: competenciaAtual, dados: null })

const relatorios = [
  { id: 'dre', nome: 'DRE Simplificado', icone: '📊', descricao: 'Receitas e despesas por período' },
  { id: 'livro-fiscal', nome: 'Livro Fiscal', icone: '🧾', descricao: 'Entradas e saídas de NF-e' },
  { id: 'estoque', nome: 'Posição de Estoque', icone: '📦', descricao: 'Situação atual por produto' },
  { id: 'folha', nome: 'Folha por Competência', icone: '👷', descricao: 'Resumo de RH e encargos' },
  { id: 'contabil', nome: 'Relatórios Contábeis', icone: '📚', descricao: 'DRE, Balanço e Razão' },
]

function abrirRelatorio(id) {
  relatorioAtivo.value = relatorioAtivo.value === id ? null : id
  error.value = null
  if (id === 'estoque' && relatorioAtivo.value === 'estoque') {
    carregarEstoque()
  }
}

async function carregarDRE() {
  loading.value = true
  error.value = null
  try {
    dre.value.dados = await RelatoriosService.getDRE({
      data_inicio: dre.value.dataInicio,
      data_fim: dre.value.dataFim,
    })
  } catch {
    error.value = 'Erro ao carregar DRE.'
  } finally {
    loading.value = false
  }
}

async function carregarLivroFiscal() {
  loading.value = true
  error.value = null
  try {
    livro.value.dados = await RelatoriosService.getLivroFiscal({
      data_inicio: livro.value.dataInicio,
      data_fim: livro.value.dataFim,
    })
  } catch {
    error.value = 'Erro ao carregar livro fiscal.'
  } finally {
    loading.value = false
  }
}

async function carregarEstoque() {
  loading.value = true
  error.value = null
  try {
    estoque.value.dados = await RelatoriosService.getPosicaoEstoque()
  } catch {
    error.value = 'Erro ao carregar posição de estoque.'
  } finally {
    loading.value = false
  }
}

async function carregarFolha() {
  loading.value = true
  error.value = null
  try {
    folha.value.dados = await RelatoriosService.getFolhaCompetencia(folha.value.competencia)
  } catch {
    error.value = 'Erro ao carregar resumo da folha.'
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0)
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
