<template>
  <div class="p-4 space-y-6 max-w-5xl mx-auto">
    <!-- Cabeçalho -->
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Área do Cliente</p>
      <h1 class="text-3xl font-display text-ancora-gold mb-2">
        {{ portalConfig?.portal?.slug ? `Portal ${portalConfig.portal.slug}` : 'Portal do Cliente' }}
      </h1>
      <p class="text-white">
        {{ empresaStore.activeEmpresa?.nome_fantasia || empresaStore.activeEmpresa?.razao_social || 'Envie documentos para o escritório de contabilidade.' }}
      </p>
      <p v-if="portalConfig?.portal?.email_responsavel" class="text-sm text-gray-400 mt-2">
        Responsável: {{ portalConfig.portal.email_responsavel }}
      </p>
      <p v-if="loadError" class="mt-3 text-sm text-red-300">{{ loadError }}</p>
    </section>

    <!-- Orientações / Configuração -->
    <section v-if="portalConfig" class="bg-ancora-navy/30 border border-ancora-gold/20 rounded-lg p-6">
      <h2 class="text-lg font-display text-ancora-gold mb-3">Orientações de Envio</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
        <div>
          <p class="text-xs uppercase tracking-wide text-gray-500">Tipos aceitos</p>
          <p class="mt-1">{{ (portalConfig.tipos_documento_permitidos || []).map(t => t.label).join(', ') }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-wide text-gray-500">Extensões permitidas</p>
          <p class="mt-1 font-mono text-xs">{{ portalConfig.extensoes_permitidas.join(' ') }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-wide text-gray-500">Tamanho máximo</p>
          <p class="mt-1">{{ portalConfig.tamanho_maximo_mb }} MB por arquivo</p>
        </div>
      </div>
    </section>

    <!-- Formulário de upload -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
      <h2 class="text-xl font-display text-ancora-gold mb-4">Enviar Documento</h2>
      <form class="space-y-4" @submit.prevent="submitUpload">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Título *</label>
            <input
              v-model="form.titulo"
              required
              type="text"
              placeholder="Ex.: Extrato bancário - Março/2026"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Tipo de documento *</label>
            <select
              v-model="form.tipo_documento"
              required
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            >
              <option value="FINANCEIRO">Financeiro</option>
              <option value="GERAL">Geral</option>
              <option value="FISCAL">Fiscal</option>
              <option value="FOLHA">Folha</option>
              <option value="CONTRATUAL">Contratual</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Competência *</label>
            <input
              v-model="form.competencia"
              required
              type="month"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Referência do cliente</label>
            <input
              v-model="form.referencia_cliente"
              type="text"
              placeholder="Código interno, protocolo etc."
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm text-gray-300 mb-1">Arquivo *</label>
          <input
            ref="fileInputRef"
            required
            type="file"
            :accept="acceptAttr"
            @change="handleFileChange"
            class="w-full text-sm text-gray-300"
          />
          <p v-if="fileError" class="mt-1 text-xs text-red-300">{{ fileError }}</p>
          <p v-else-if="selectedFile" class="mt-1 text-xs text-gray-400">
            {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </p>
        </div>

        <div>
          <label class="block text-sm text-gray-300 mb-1">Observações</label>
          <textarea
            v-model="form.observacoes"
            rows="3"
            placeholder="Alguma informação adicional para o escritório?"
            class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
          ></textarea>
        </div>

        <div class="flex items-center justify-end">
          <button
            type="submit"
            :disabled="submitting || !!fileError || !selectedFile"
            class="px-5 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 disabled:opacity-50"
          >
            {{ submitting ? 'Enviando...' : 'Enviar documento' }}
          </button>
        </div>
      </form>
    </section>

    <!-- Meus Envios -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-display text-ancora-gold">Meus Envios</h2>
        <button
          type="button"
          @click="loadDocuments"
          class="text-sm text-gray-400 hover:text-ancora-gold"
        >
          Atualizar
        </button>
      </div>

      <div v-if="loadingDocs" class="text-gray-500 text-sm">Carregando envios...</div>

      <div v-else-if="myDocuments.length" class="space-y-3">
        <div
          v-for="doc in myDocuments"
          :key="doc.id"
          class="border border-ancora-gold/10 rounded-md p-4 bg-ancora-black/40"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <p class="text-white font-bold truncate">{{ doc.titulo }}</p>
              <p class="text-sm text-gray-400">
                {{ doc.tipo_documento }} • {{ formatCompetencia(doc.competencia) }}
              </p>
              <p v-if="doc.arquivo_nome" class="text-xs text-gray-500 mt-1 truncate">
                {{ doc.arquivo_nome }}
              </p>
              <p
                v-if="doc.log_validacao"
                class="text-xs text-gray-400 mt-2"
              >
                • {{ doc.log_validacao }}
              </p>
            </div>
            <span
              class="text-xs font-bold px-2 py-1 rounded whitespace-nowrap"
              :class="badgeClass(doc.status)"
            >
              {{ statusLabel(doc.status) }}
            </span>
          </div>
        </div>
      </div>

      <p v-else class="text-gray-500 text-sm">Você ainda não enviou documentos.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import IntakeService from '@/services/intake.service'
import { useEmpresaStore } from '@/stores/empresa'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const empresaStore = useEmpresaStore()
const uiStore = useUiStore()

const slug = computed(() => route.params.slug)

const portalConfig = ref(null)
const loadError = ref('')
const loadingDocs = ref(false)
const myDocuments = ref([])
const submitting = ref(false)
const selectedFile = ref(null)
const fileError = ref('')
const fileInputRef = ref(null)

const form = ref(defaultForm())

function defaultForm() {
  return {
    titulo: '',
    tipo_documento: 'FINANCEIRO',
    competencia: new Date().toISOString().slice(0, 7),
    referencia_cliente: '',
    observacoes: '',
  }
}

const acceptAttr = computed(() => {
  return (portalConfig.value?.extensoes_permitidas || []).join(',')
})

onMounted(() => {
  loadPortal()
  loadDocuments()
})

watch(slug, () => {
  loadPortal()
})

async function loadPortal() {
  loadError.value = ''
  try {
    portalConfig.value = await IntakeService.getClientPortalConfig(slug.value)
  } catch (error) {
    console.error(error)
    loadError.value = 'Não foi possível carregar a configuração do portal.'
  }
}

async function loadDocuments() {
  loadingDocs.value = true
  try {
    const resp = await IntakeService.listMyDocuments()
    myDocuments.value = resp.results || resp || []
  } catch (error) {
    console.error(error)
    uiStore.showNotification('Erro ao carregar seus envios.', 'error')
  } finally {
    loadingDocs.value = false
  }
}

function handleFileChange(event) {
  const file = event.target.files?.[0] || null
  selectedFile.value = file
  fileError.value = validateFile(file)
}

function validateFile(file) {
  if (!file) return ''
  const extensions = portalConfig.value?.extensoes_permitidas || []
  const maxMb = portalConfig.value?.tamanho_maximo_mb || 10
  const name = (file.name || '').toLowerCase()
  const ok = extensions.some((ext) => name.endsWith(ext))
  if (!ok) {
    return `Extensão não permitida. Aceitas: ${extensions.join(', ')}`
  }
  if (file.size > maxMb * 1024 * 1024) {
    return `Arquivo excede o tamanho máximo de ${maxMb} MB.`
  }
  return ''
}

async function submitUpload() {
  if (!selectedFile.value) {
    uiStore.showNotification('Selecione um arquivo para enviar.', 'error')
    return
  }
  if (fileError.value) {
    uiStore.showNotification(fileError.value, 'error')
    return
  }

  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('titulo', form.value.titulo)
    payload.append('tipo_documento', form.value.tipo_documento)
    payload.append('tipo_entrega', 'UPLOAD')
    payload.append('competencia', `${form.value.competencia}-01`)
    payload.append('arquivo', selectedFile.value)
    if (form.value.observacoes) {
      payload.append('observacoes', form.value.observacoes)
    }
    if (form.value.referencia_cliente) {
      payload.append('referencia_cliente', form.value.referencia_cliente)
    }
    if (portalConfig.value?.portal?.id) {
      payload.append('portal_cliente', portalConfig.value.portal.id)
    }

    const response = await IntakeService.uploadDocument(payload)

    // Optimistic update: prepend to list imediatamente
    myDocuments.value = [response, ...myDocuments.value]

    uiStore.showNotification(
      `Documento enviado. Status: ${statusLabel(response.status)}`,
      response.status === 'REPROVADO' ? 'error' : 'success'
    )

    // Reset
    form.value = defaultForm()
    selectedFile.value = null
    fileError.value = ''
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }

    // Refresh autoritativo
    loadDocuments()
  } catch (error) {
    console.error(error)
    const backendMsg =
      error?.response?.data?.errors?.[0]?.message ||
      error?.response?.data?.message ||
      error?.response?.data?.arquivo?.[0] ||
      error?.response?.data?.detail ||
      'Erro ao enviar documento.'
    uiStore.showNotification(backendMsg, 'error')
  } finally {
    submitting.value = false
  }
}

function formatFileSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function formatCompetencia(value) {
  if (!value) return ''
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR', {
    month: '2-digit',
    year: 'numeric',
  })
}

function statusLabel(status) {
  const map = {
    NOVO: 'Novo',
    VALIDADO: 'Validado',
    REPROVADO: 'Reprovado',
    EM_ANALISE: 'Em análise',
  }
  return map[status] || status
}

function badgeClass(status) {
  if (status === 'VALIDADO') {
    return 'bg-green-600/20 text-green-300'
  }
  if (status === 'REPROVADO') {
    return 'bg-red-600/20 text-red-300'
  }
  return 'bg-yellow-500/20 text-yellow-300'
}
</script>
