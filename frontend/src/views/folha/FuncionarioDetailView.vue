<template>
  <div class="p-6 max-w-7xl mx-auto min-h-screen">
    <div v-if="loading" class="flex flex-col items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-ancora-gold"></div>
      <p class="mt-4 text-gray-400 font-body">Carregando detalhes do funcionário...</p>
    </div>

    <div v-else-if="error" class="bg-red-900/20 border border-red-500/50 p-4 rounded-lg text-red-400 text-center">
      {{ error }}
    </div>

    <div v-else-if="funcionario" class="space-y-6 animate-fade-in">
      <!-- Cabeçalho com Glassmorphism -->
      <div class="relative overflow-hidden bg-ancora-black/40 backdrop-blur-md border border-ancora-gold/20 p-8 rounded-2xl shadow-2xl">
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="flex items-center gap-6">
            <div class="h-20 w-20 rounded-full bg-gradient-to-br from-ancora-gold to-ancora-navy flex items-center justify-center text-3xl font-bold text-white shadow-lg">
              {{ funcionario.nome_completo.charAt(0) }}
            </div>
            <div>
              <h1 class="text-4xl font-display font-bold text-white tracking-tight">{{ funcionario.nome_completo }}</h1>
              <div class="flex flex-wrap gap-4 mt-2">
                <span class="flex items-center text-gray-400 text-sm">
                  <span class="bg-ancora-gold/20 text-ancora-gold px-2 py-0.5 rounded text-xs font-bold mr-2">CPF</span>
                  {{ formatCpf(funcionario.cpf) }}
                </span>
                <span class="flex items-center text-gray-400 text-sm">
                  <span class="bg-ancora-navy/40 text-blue-300 px-2 py-0.5 rounded text-xs font-bold mr-2">PIS</span>
                  {{ funcionario.pis || 'Não informado' }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex gap-3">
            <button @click="$router.push({ name: 'funcionarios-list' })" class="px-5 py-2.5 rounded-xl border border-white/10 text-gray-300 hover:bg-white/5 transition-all">
              Voltar
            </button>
            <button @click="openEditModal" class="px-5 py-2.5 rounded-xl bg-ancora-gold text-ancora-black font-bold hover:shadow-[0_0_20px_rgba(212,175,55,0.4)] transition-all">
              Editar Cadastro
            </button>
          </div>
        </div>
        <!-- Background decorative element -->
        <div class="absolute -top-24 -right-24 h-64 w-64 bg-ancora-gold/5 rounded-full blur-3xl"></div>
      </div>

      <!-- Navegação por Abas -->
      <div class="flex border-b border-white/10 gap-8">
        <button v-for="tab in tabs" :key="tab.id" 
                @click="activeTab = tab.id"
                :class="activeTab === tab.id ? 'text-ancora-gold border-b-2 border-ancora-gold' : 'text-gray-500 hover:text-gray-300'"
                class="pb-4 font-display font-bold transition-all text-lg relative">
          {{ tab.label }}
          <span v-if="tab.count !== undefined" class="ml-2 px-1.5 py-0.5 bg-white/10 rounded-full text-[10px]">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Conteúdo das Abas -->
      <div class="min-h-[400px]">
        <!-- Aba: Geral -->
        <div v-if="activeTab === 'geral'" class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-slide-up">
          <div class="lg:col-span-2 space-y-6">
            <div class="bg-ancora-black/30 border border-white/10 p-6 rounded-xl">
              <h3 class="text-xl font-display text-white mb-4 flex items-center">
                <span class="h-2 w-2 bg-ancora-gold rounded-full mr-3"></span>
                Informações de Contato e Endereço
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8 text-sm">
                <div><p class="text-gray-500 uppercase text-[10px] font-bold">E-mail</p><p class="text-white">{{ funcionario.email || '-' }}</p></div>
                <div><p class="text-gray-500 uppercase text-[10px] font-bold">Celular / WhatsApp</p><p class="text-white">{{ funcionario.telefone_celular || '-' }}</p></div>
                <div class="md:col-span-2 mt-2"><p class="text-gray-500 uppercase text-[10px] font-bold">Endereço</p><p class="text-white">{{ formatEndereco(funcionario) }}</p></div>
              </div>
            </div>

            <div class="bg-ancora-black/30 border border-white/10 p-6 rounded-xl">
              <h3 class="text-xl font-display text-white mb-4 flex items-center">
                <span class="h-2 w-2 bg-blue-500 rounded-full mr-3"></span>
                Dados Bancários (Para Pagamento)
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div><p class="text-gray-500 uppercase text-[10px] font-bold">Banco</p><p class="text-white text-base">{{ funcionario.banco || '-' }}</p></div>
                <div><p class="text-gray-500 uppercase text-[10px] font-bold">Agência</p><p class="text-white text-base">{{ funcionario.agencia || '-' }}</p></div>
                <div><p class="text-gray-500 uppercase text-[10px] font-bold">Conta</p><p class="text-white text-base">{{ funcionario.conta }} ({{ funcionario.tipo_conta }})</p></div>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="bg-gradient-to-br from-ancora-navy/80 to-ancora-black/80 border border-ancora-gold/30 p-6 rounded-xl shadow-xl">
              <h3 class="text-xl font-display text-ancora-gold mb-6">Contrato de Trabalho</h3>
              <div v-if="contratoAtivo" class="space-y-4">
                <div class="flex justify-between items-end border-b border-white/5 pb-2">
                  <span class="text-gray-400 text-sm">Cargo</span>
                  <span class="text-white font-bold">{{ contratoAtivo.cargo_detail?.nome }}</span>
                </div>
                <div class="flex justify-between items-end border-b border-white/5 pb-2">
                  <span class="text-gray-400 text-sm">Departamento</span>
                  <span class="text-white">{{ contratoAtivo.departamento_detail?.nome }}</span>
                </div>
                <div class="flex justify-between items-end border-b border-white/5 pb-2">
                  <span class="text-gray-400 text-sm">Salário Base</span>
                  <span class="text-ancora-gold font-bold text-lg">{{ formatCurrency(contratoAtivo.salario_base) }}</span>
                </div>
                <div class="flex justify-between items-end border-b border-white/5 pb-2">
                  <span class="text-gray-400 text-sm">Admissão</span>
                  <span class="text-white">{{ formatDate(contratoAtivo.data_inicio) }}</span>
                </div>
                <div class="mt-6">
                   <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                    CONTRATO ATIVO
                  </span>
                </div>
              </div>
              <div v-else class="text-center py-8 text-gray-500 italic">
                Crie um contrato para este funcionário.
              </div>
            </div>
          </div>
        </div>

        <!-- Aba: Ponto e Horas Extras -->
        <div v-if="activeTab === 'ponto'" class="space-y-6 animate-slide-up">
          <div class="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10">
            <div>
              <h3 class="text-lg font-display text-white">Registro de Ponto</h3>
              <p class="text-xs text-gray-500">Últimos lançamentos de jornada e horas extras.</p>
            </div>
            <button @click="openPontoModal" class="px-4 py-2 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-lg font-bold hover:bg-blue-600/30 transition-all">
              Lançar Ponto Manual
            </button>
          </div>

          <div class="overflow-x-auto rounded-xl border border-white/10">
            <table class="min-w-full bg-ancora-black/20 text-sm">
              <thead>
                <tr class="bg-white/5 text-gray-400 text-left uppercase text-[10px] font-bold">
                  <th class="py-3 px-6">Data</th>
                  <th class="py-3 px-6">Entradas/Saídas</th>
                  <th class="py-3 px-6 text-center">Horas Trab.</th>
                  <th class="py-3 px-6 text-center">H.E. (50%)</th>
                  <th class="py-3 px-6 text-center">Atrasos</th>
                  <th class="py-3 px-6">Tipo</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5 text-gray-300">
                <tr v-for="ponto in pontos" :key="ponto.id" class="hover:bg-white/5 transition-colors">
                  <td class="py-4 px-6 font-bold text-white">{{ formatDate(ponto.data) }}</td>
                  <td class="py-4 px-6">
                    <div class="flex gap-2">
                      <span class="px-1.5 py-0.5 bg-black/40 rounded text-[10px]">{{ ponto.entrada_1 }}</span>
                      <span class="px-1.5 py-0.5 bg-black/40 rounded text-[10px]">{{ ponto.saida_1 }}</span>
                      <span class="text-gray-600">|</span>
                      <span class="px-1.5 py-0.5 bg-black/40 rounded text-[10px]">{{ ponto.entrada_2 }}</span>
                      <span class="px-1.5 py-0.5 bg-black/40 rounded text-[10px]">{{ ponto.saida_2 }}</span>
                    </div>
                  </td>
                  <td class="py-4 px-6 text-center">{{ ponto.total_horas }}h</td>
                  <td class="py-4 px-6 text-center">
                    <span v-if="parseFloat(ponto.horas_extras) > 0" class="text-green-400 font-bold">+{{ ponto.horas_extras }}h</span>
                    <span v-else class="text-gray-600">-</span>
                  </td>
                  <td class="py-4 px-6 text-center">
                    <span v-if="parseFloat(ponto.atrasos) > 0" class="text-red-400 font-bold">-{{ ponto.atrasos }}h</span>
                    <span v-else class="text-gray-600">-</span>
                  </td>
                   <td class="py-4 px-6">
                    <span :class="ponto.manual ? 'text-amber-400' : 'text-blue-400'" class="text-[10px]">
                      {{ ponto.manual ? 'Manual' : 'Relógio' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="pontos.length === 0">
                  <td colspan="6" class="py-12 text-center text-gray-600 italic">Nenhum registro de ponto encontrado.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Aba: Ocorrências e Atestados -->
        <div v-if="activeTab === 'justificativas'" class="space-y-6 animate-slide-up">
           <div class="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10">
            <div>
              <h3 class="text-lg font-display text-white">Justificativas e Ocorrências</h3>
              <p class="text-xs text-gray-500">Atestados médicos, suspensões e faltas justificadas.</p>
            </div>
            <button @click="openJustModal" class="px-4 py-2 bg-purple-600/20 text-purple-400 border border-purple-500/30 rounded-lg font-bold hover:bg-purple-600/30 transition-all">
              Nova Ocorrência / Upload Atestado
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="just in justificativas" :key="just.id" class="p-5 bg-ancora-black/50 border border-white/5 rounded-2xl flex justify-between items-start hover:border-ancora-gold/30 transition-all">
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <span :class="getJustTypeClass(just.tipo)" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                    {{ formatJustType(just.tipo) }}
                  </span>
                  <span v-if="just.abona_ponto" class="text-[10px] text-green-400 bg-green-400/10 px-1.5 py-0.5 rounded">ABONADO</span>
                </div>
                <h4 class="text-white font-body text-lg">{{ formatDate(just.data_inicio) }} a {{ formatDate(just.data_fim) }}</h4>
                <p class="text-gray-500 text-sm line-clamp-2">{{ just.descricao }}</p>
                <div v-if="just.crm_medico" class="text-[10px] text-gray-400">
                  <span class="font-bold">Médico:</span> {{ just.nome_medico }} (CRM: {{ just.crm_medico }})
                </div>
              </div>
              <div class="flex flex-col items-end gap-3">
                <a v-if="just.documento" :href="just.documento" target="_blank" class="h-10 w-10 flex items-center justify-center bg-white/5 rounded-full hover:bg-ancora-gold/20 hover:text-ancora-gold transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </a>
                <button @click="deleteJustificativa(just.id)" class="text-red-500/50 hover:text-red-400 text-xs">Remover</button>
              </div>
            </div>
          </div>
          <div v-if="justificativas.length === 0" class="py-12 text-center text-gray-600 italic">Nenhuma ocorrência registrada.</div>
        </div>

        <!-- Aba: Holerites -->
        <div v-if="activeTab === 'holerites'" class="space-y-6 animate-slide-up">
           <div class="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10">
            <div>
              <h3 class="text-lg font-display text-white">Extratos de Holerite</h3>
              <p class="text-xs text-gray-500">Acesse e faça o download dos recibos de pagamento.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div v-for="holerite in holerites" :key="holerite.id" class="bg-ancora-black/50 border border-white/10 rounded-2xl overflow-hidden hover:border-ancora-gold transition-all group">
              <div class="bg-ancora-navy/50 p-4 border-b border-white/5 flex justify-between items-center">
                <span class="text-ancora-gold font-bold">{{ formatDateMonth(holerite.folha_pagamento_detail?.competencia) }}</span>
                <span class="text-[10px] bg-white/10 px-2 py-0.5 rounded text-gray-300">FECHADA</span>
              </div>
              <div class="p-5 space-y-4">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Liquido</span>
                  <span class="text-white font-bold">{{ formatCurrency(holerite.liquido_receber) }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-gray-500">Data Pagamento</span>
                  <span class="text-gray-300">{{ formatDate(holerite.data_pagamento) || 'A pagar' }}</span>
                </div>
                <button @click="downloadHolerite(holerite.id)" class="w-full mt-4 py-2.5 bg-white/5 group-hover:bg-ancora-gold group-hover:text-ancora-black transition-all rounded-xl font-bold flex items-center justify-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  PDF Holerite
                </button>
              </div>
            </div>
          </div>
          <div v-if="holerites.length === 0" class="py-12 text-center text-gray-600 italic">Nenhum holerite processado para este funcionário.</div>
        </div>

        <!-- Aba: Documentos -->
        <div v-if="activeTab === 'documentos'" class="space-y-6 animate-slide-up">
           <div class="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10">
            <div>
              <h3 class="text-lg font-display text-white">Prontuário Digital (GED)</h3>
              <p class="text-xs text-gray-500">Contratos, termos e outros documentos arquivados.</p>
            </div>
            <button @click="openDocModal" class="px-4 py-2 bg-ancora-gold/10 text-ancora-gold border border-ancora-gold/30 rounded-lg font-bold hover:bg-ancora-gold/20 transition-all">
              Upload de Documento
            </button>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
            <div v-for="doc in documentos" :key="doc.id" class="group relative flex flex-col items-center p-6 bg-white/5 border border-white/10 rounded-2xl hover:bg-ancora-navy/30 hover:border-ancora-gold/50 transition-all cursor-pointer">
              <div class="text-ancora-gold mb-3 transition-transform group-hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p class="text-white text-xs font-bold text-center line-clamp-2 h-8">{{ doc.descricao || formatDocType(doc.tipo) }}</p>
              <p class="text-[9px] text-gray-500 mt-2">{{ formatDate(doc.data_upload) }}</p>
              
              <div class="absolute inset-x-0 bottom-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                 <a :href="doc.arquivo" target="_blank" class="block w-full text-center bg-ancora-gold text-ancora-black text-[10px] font-bold py-1.5 rounded-lg">ABRIR</a>
              </div>
            </div>
          </div>
          <div v-if="documentos.length === 0" class="py-12 text-center text-gray-600 italic">Nenhum documento arquivado.</div>
        </div>
      </div>
    </div>

    <!-- Modais (Simplificados para esta implementação) -->
    <!-- Modal Justificativa -->
    <div v-if="isJustModalOpen" class="fixed inset-0 bg-ancora-black/80 flex items-center justify-center z-[100] backdrop-blur-sm p-4">
      <div class="bg-ancora-black border border-ancora-gold/30 p-8 rounded-2xl w-full max-w-lg shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <h2 class="text-2xl font-display text-white mb-6">Nova Ocorrência</h2>
        <form @submit.prevent="saveJustificativa" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Tipo</label>
              <select v-model="formJust.tipo" required class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white">
                <option value="ATESTADO_MEDICO">Atestado Médico</option>
                <option value="FALTA_JUSTIFICADA">Falta Justificada</option>
                <option value="SUSPENSAO">Suspensão</option>
                <option value="FERIAS">Férias</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Abonar?</label>
              <select v-model="formJust.abona_ponto" class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white">
                <option :value="true">Sim</option>
                <option :value="false">Não</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Data Início</label>
              <input type="date" v-model="formJust.data_inicio" required class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white"/>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Data Fim</label>
              <input type="date" v-model="formJust.data_fim" required class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white"/>
            </div>
          </div>
          
          <div v-if="formJust.tipo === 'ATESTADO_MEDICO'" class="grid grid-cols-2 gap-4 border-t border-white/5 pt-4">
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">CID</label>
              <input type="text" v-model="formJust.cid" class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white"/>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">CRM Médico</label>
              <input type="text" v-model="formJust.crm_medico" class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white"/>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Descrição</label>
            <textarea v-model="formJust.descricao" rows="2" class="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-white"></textarea>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Arquivo (Atestado)</label>
            <input type="file" @change="handleJustFile" class="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-ancora-gold file:text-ancora-black hover:file:bg-ancora-gold/80"/>
          </div>

          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="isJustModalOpen = false" class="px-6 py-2 text-gray-500">Cancelar</button>
            <button type="submit" class="px-6 py-2 bg-ancora-gold text-ancora-black font-bold rounded-xl">Salvar Ocorrência</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import FolhaService from '@/services/folha.service'

const route = useRoute()
const uiStore = useUiStore()

const funcionario = ref(null)
const contratoAtivo = ref(null)
const pontos = ref([])
const justificativas = ref([])
const documentos = ref([])
const loading = ref(true)
const error = ref(null)

const activeTab = ref('geral')
const tabs = ref([
  { id: 'geral', label: 'Cadastro' },
  { id: 'ponto', label: 'Cartão de Ponto' },
  { id: 'justificativas', label: 'Ocorrências' },
  { id: 'holerites', label: 'Holerites' },
  { id: 'documentos', label: 'Documentos' },
])

const holerites = ref([])

// Modais states
const isJustModalOpen = ref(false)
const formJust = ref({
  tipo: 'ATESTADO_MEDICO',
  data_inicio: '',
  data_fim: '',
  abona_ponto: true,
  descricao: '',
  cid: '',
  crm_medico: '',
  nome_medico: '',
  file: null
})

onMounted(async () => {
  await fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const id = route.params.id
    // Promise.all para performance
    const [funcData, contratos, pontosData, justs, docs, holeritesData] = await Promise.all([
      FolhaService.getFuncionario(id),
      FolhaService.getContratos({ funcionario: id, ativo: true }),
      FolhaService.getRegistrosPonto({ funcionario: id, limit: 10 }),
      FolhaService.getJustificativas({ funcionario: id }),
      FolhaService.getDocumentos({ funcionario: id }),
      FolhaService.getHolerites({ funcionario: id })
    ])
    
    funcionario.value = funcData
    contratoAtivo.value = contratos.results[0] || null
    pontos.value = pontosData.results || []
    justificativas.value = justs.results || []
    documentos.value = docs.results || []
    holerites.value = holeritesData.results || []
    
    // Atualizar contadores nas abas
    tabs.value[1].count = pontos.value.length
    tabs.value[2].count = justificativas.value.length
    tabs.value[3].count = holerites.value.length
    tabs.value[4].count = documentos.value.length

  } catch (err) {
    error.value = 'Falha ao carregar dados do funcionário.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Helpers
const formatCpf = (v) => v?.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")
const formatCurrency = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
const formatDate = (v) => v ? new Date(v).toLocaleDateString('pt-BR') : '-'
const formatDateMonth = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase()
}

const formatEndereco = (f) => {
  if (!f.logradouro) return '-'
  return `${f.logradouro}, ${f.numero} - ${f.bairro}, ${f.municipio}/${f.uf}`
}

const formatJustType = (t) => t.replace(/_/g, ' ')
const getJustTypeClass = (t) => {
  if (t === 'ATESTADO_MEDICO') return 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
  if (t === 'FALTA_NAO_JUSTIFICADA') return 'bg-red-500/20 text-red-400 border border-red-500/30'
  return 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
}

const formatDocType = (t) => t.replace(/_/g, ' ')

// Actions
function openJustModal() {
  isJustModalOpen.value = true
  formJust.value = {
    tipo: 'ATESTADO_MEDICO',
    data_inicio: new Date().toISOString().split('T')[0],
    data_fim: new Date().toISOString().split('T')[0],
    abona_ponto: true,
    descricao: '',
    cid: '',
    crm_medico: '',
    nome_medico: '',
    file: null
  }
}

function handleJustFile(e) {
  formJust.value.file = e.target.files[0]
}

async function saveJustificativa() {
  uiStore.setLoading(true)
  try {
    const formData = new FormData()
    formData.append('funcionario', funcionario.value.id)
    formData.append('tipo', formJust.value.tipo)
    formData.append('data_inicio', formJust.value.data_inicio)
    formData.append('data_fim', formJust.value.data_fim)
    formData.append('abona_ponto', formJust.value.abona_ponto)
    formData.append('descricao', formJust.value.descricao)
    if (formJust.value.cid) formData.append('cid', formJust.value.cid)
    if (formJust.value.crm_medico) formData.append('crm_medico', formJust.value.crm_medico)
    if (formJust.value.file) formData.append('documento', formJust.value.file)

    await FolhaService.createJustificativa(formData)
    uiStore.showNotification('Ocorrência registrada com sucesso!', 'success')
    isJustModalOpen.value = false
    await fetchData()
  } catch (err) {
    uiStore.showNotification('Erro ao salvar ocorrência.', 'error')
  } finally {
    uiStore.setLoading(false)
  }
}

async function deleteJustificativa(id) {
  if (confirm('Deseja remover esta ocorrência?')) {
    uiStore.setLoading(true)
    try {
      await FolhaService.deleteJustificativa(id)
      await fetchData()
    } catch (err) {
       uiStore.showNotification('Erro ao remover.', 'error')
    } finally {
      uiStore.setLoading(false)
    }
  }
}

async function downloadHolerite(id) {
  try {
    const blob = await FolhaService.getHoleritePdf(id)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `holerite_${funcionario.value.nome_completo}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    uiStore.showNotification('Erro ao baixar PDF.', 'error')
  }
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
.animate-slide-up { animation: slideUp 0.4s ease-out; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
