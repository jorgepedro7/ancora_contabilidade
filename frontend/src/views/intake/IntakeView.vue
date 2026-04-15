<template>
  <div class="p-4 space-y-6">
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Backoffice interno</p>
          <h1 class="text-3xl font-display text-ancora-gold mb-2">Central de Recebimentos</h1>
          <p class="text-white text-lg">{{ empresaStore.activeEmpresa?.nome_fantasia || empresaStore.activeEmpresa?.razao_social || 'Empresa não selecionada' }}</p>
          <p class="text-gray-400 mt-2">
            {{ authStore.user?.perfil_empresa === 'CLIENTE'
              ? 'Acompanhe os documentos já encaminhados ao escritório e o retorno da operação.'
              : 'Registre documentos recebidos por e-mail, WhatsApp, coleta manual ou portal externo. Esta tela é da equipe interna.' }}
          </p>
          <p v-if="authStore.user?.perfil_empresa !== 'CLIENTE'" class="mt-3 text-xs text-gray-500">
            A área externa para upload do cliente deve ser publicada separadamente, por exemplo em
            <span class="font-mono text-gray-300">seu-dominio.com.br/area_cliente</span>.
          </p>
        </div>

        <div v-if="empresaStore.activeEmpresa" class="text-sm text-gray-400">
          <p>CNPJ: {{ formatCnpj(empresaStore.activeEmpresa.cnpj) }}</p>
          <p class="mt-2">Perfil atual: {{ authStore.user?.perfil_empresa || 'OPERACAO' }}</p>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
      <div class="space-y-6">
        <section
          v-if="authStore.user?.perfil_empresa !== 'CLIENTE'"
          class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6"
        >
          <div class="flex items-start justify-between gap-4 mb-4">
            <div>
              <h2 class="text-xl font-display text-ancora-gold">Área do Cliente</h2>
              <p class="text-sm text-gray-400">Configure o acesso externo que o cliente usará para subir arquivos fora do backoffice.</p>
            </div>
            <span
              class="text-xs uppercase tracking-wide px-2 py-1 rounded"
              :class="portalClienteId ? 'bg-green-600/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'"
            >
              {{ portalClienteId ? 'Área configurada' : 'Área pendente' }}
            </span>
          </div>

          <form class="grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="salvarPortal">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Slug da área</label>
              <input v-model="portalForm.slug" type="text" required class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">E-mail responsável</label>
              <input v-model="portalForm.email_responsavel" type="email" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Telefone responsável</label>
              <input v-model="portalForm.telefone_responsavel" type="text" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
            </div>
            <label class="flex items-center gap-3 text-sm text-gray-300">
              <input v-model="portalForm.recebe_alertas" type="checkbox" class="rounded border-ancora-gold/30 bg-ancora-black/70" />
              Receber alertas automáticos
            </label>
            <div class="md:col-span-2 rounded-md border border-ancora-gold/20 bg-ancora-navy/20 p-4">
              <p class="text-xs uppercase tracking-wide text-gray-500">URL sugerida para o cliente</p>
              <p class="mt-2 break-all font-mono text-sm text-white">{{ portalPublicUrl }}</p>
              <p class="mt-2 text-xs text-gray-400">
                Use essa URL em um domínio público para o cliente enviar documentos. A Central de Recebimentos continua sendo exclusiva da operação.
              </p>
            </div>
            <div class="md:col-span-2">
              <button type="submit" :disabled="savingPortal" class="px-5 py-2 bg-ancora-navy text-ancora-gold border border-ancora-gold/40 rounded-md font-bold hover:bg-ancora-navy/80 disabled:opacity-50">
                {{ savingPortal ? 'Salvando...' : portalClienteId ? 'Atualizar área do cliente' : 'Criar área do cliente' }}
              </button>
            </div>
          </form>
        </section>

        <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
          <div class="mb-4">
            <h2 class="text-xl font-display text-ancora-gold">Registrar recebimento interno</h2>
            <p class="text-sm text-gray-400 mt-1">Use este formulário quando a equipe receber arquivos por e-mail, WhatsApp, coleta física ou importação manual.</p>
          </div>
          <form class="space-y-4" @submit.prevent="submitRecebimento">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">Título</label>
                <input v-model="form.titulo" required type="text" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Tipo de documento</label>
                <select v-model="form.tipo_documento" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white">
                  <option value="FISCAL">Fiscal</option>
                  <option value="FOLHA">Folha</option>
                  <option value="FINANCEIRO">Financeiro</option>
                  <option value="CONTRATUAL">Contratual</option>
                  <option value="GERAL">Geral</option>
                </select>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Tipo de entrega</label>
                <select v-model="form.tipo_entrega" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white">
                  <option value="UPLOAD">Upload interno</option>
                  <option value="EMAIL">Recebido por e-mail</option>
                  <option value="API">Integração/API</option>
                  <option value="MANUAL">Registro manual</option>
                </select>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Competência</label>
                <input v-model="form.competencia" required type="month" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
              </div>
              <div v-if="authStore.user?.perfil_empresa !== 'CLIENTE' && portalClientes.length">
                <label class="block text-sm text-gray-300 mb-1">Área do cliente vinculada</label>
                <select v-model="form.portal_cliente" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white">
                  <option value="">Sem área específica</option>
                  <option v-for="portal in portalClientes" :key="portal.id" :value="portal.id">
                    {{ portal.slug }}
                  </option>
                </select>
              </div>

              <div v-if="form.tipo_documento === 'FISCAL'">
                <label class="block text-sm text-gray-300 mb-1">Nota Fiscal (opcional)</label>
                <input type="text" placeholder="Número ou chave NF" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm" />
                <p class="text-xs text-gray-500 mt-1">Vinculação manual pode ser feita depois se necessário</p>
              </div>

              <div v-if="form.tipo_documento === 'FOLHA'">
                <label class="block text-sm text-gray-300 mb-1">Funcionário/Contrato (opcional)</label>
                <input type="text" placeholder="Nome do funcionário ou contrato" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm" />
                <p class="text-xs text-gray-500 mt-1">Vinculação manual pode ser feita depois se necessário</p>
              </div>

              <div v-if="form.tipo_documento === 'CONTRATUAL'">
                <label class="block text-sm text-gray-300 mb-1">Contrato (opcional)</label>
                <input type="text" placeholder="Número ou descrição do contrato" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm" />
                <p class="text-xs text-gray-500 mt-1">Vinculação manual pode ser feita depois se necessário</p>
              </div>
            </div>

            <div>
              <label class="block text-sm text-gray-300 mb-1">Arquivo recebido</label>
              <input required type="file" @change="handleFileChange" class="w-full text-sm text-gray-300" />
            </div>

            <div>
              <label class="block text-sm text-gray-300 mb-1">Observações</label>
              <textarea v-model="form.observacoes" rows="3" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"></textarea>
            </div>

            <div class="flex items-center justify-between gap-4">
              <p class="text-xs text-gray-500">
                Documentos sem vinculação interna (nota fiscal, funcionário, contrato) entrarão em triagem para vinculação manual.
              </p>
              <button type="submit" :disabled="submitting" class="px-5 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 disabled:opacity-50">
                {{ submitting ? 'Registrando...' : 'Registrar documento' }}
              </button>
            </div>
          </form>
        </section>
      </div>

      <div class="space-y-6">
        <section
          v-if="authStore.user?.perfil_empresa !== 'CLIENTE'"
          class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6"
        >
          <h2 class="text-xl font-display text-ancora-gold mb-4">Exportação Questor</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Competência</label>
              <input v-model="exportCompetencia" type="month" class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white" />
            </div>
            <button @click="exportarQuestor" :disabled="exporting" class="w-full px-5 py-2 bg-ancora-navy text-ancora-gold border border-ancora-gold/40 rounded-md font-bold hover:bg-ancora-navy/80 disabled:opacity-50">
              {{ exporting ? 'Gerando...' : 'Gerar pacote Questor' }}
            </button>

            <div v-if="ultimoLote" class="border border-ancora-gold/20 rounded-md p-4 bg-ancora-navy/20">
              <p class="text-sm text-gray-300">Último lote</p>
              <p class="text-white font-bold">{{ formatCompetencia(ultimoLote.competencia) }} • {{ ultimoLote.status }}</p>
              <p class="text-xs text-gray-500 mt-1">Documentos exportados: {{ ultimoLote.resumo?.documentos_exportados ?? 0 }}</p>
              <a v-if="ultimoLote.download_url" :href="ultimoLote.download_url" target="_blank" rel="noreferrer" class="inline-block mt-3 text-sm text-ancora-gold hover:underline">
                Baixar arquivo
              </a>
            </div>
          </div>
        </section>

        <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-xl font-display text-ancora-gold">Checklists por competência</h2>
              <p class="text-sm text-gray-400">Visão consolidada do que já foi recebido e do que ainda está pendente.</p>
            </div>
            <button @click="loadData" class="text-sm text-gray-400 hover:text-ancora-gold">Atualizar</button>
          </div>

          <div v-if="checklists.length" class="overflow-x-auto">
            <table class="min-w-full text-sm text-left">
              <thead class="text-ancora-gold uppercase">
                <tr>
                  <th class="py-2 pr-4">Competência</th>
                  <th class="py-2 pr-4">Módulo</th>
                  <th class="py-2 pr-4">Status</th>
                  <th class="py-2 pr-4">Documentos</th>
                  <th class="py-2 pr-4">Pendências</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="checklist in checklists" :key="checklist.id" class="border-t border-ancora-gold/10">
                  <td class="py-2 pr-4">{{ formatCompetencia(checklist.competencia) }}</td>
                  <td class="py-2 pr-4">{{ checklist.modulo }}</td>
                  <td class="py-2 pr-4">{{ checklist.status }}</td>
                  <td class="py-2 pr-4">{{ checklist.total_documentos }}</td>
                  <td class="py-2 pr-4">{{ checklist.total_pendencias_abertas }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-gray-500">Nenhum checklist encontrado.</p>
        </section>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
        <h2 class="text-xl font-display text-ancora-gold mb-4">Últimos recebimentos</h2>
        <div v-if="recebimentos.length" class="space-y-3">
          <div v-for="recebimento in recebimentos" :key="recebimento.id" class="border border-ancora-gold/10 rounded-md p-4 bg-ancora-black/40">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-white font-bold">{{ recebimento.titulo }}</p>
                <p class="text-sm text-gray-400">{{ recebimento.tipo_documento }} • {{ formatCompetencia(recebimento.competencia) }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  <span v-if="recebimento.origem_upload" class="inline-block bg-ancora-navy/40 px-2 py-0.5 rounded mr-2">{{ recebimento.origem_upload }}</span>
                  <span v-if="recebimento.enviado_por" class="text-gray-400">Enviado por: {{ recebimento.enviado_por }}</span>
                </p>
                <p v-if="recebimento.portal_cliente_slug" class="text-xs text-gray-500 mt-1">Área externa: {{ recebimento.portal_cliente_slug }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ recebimento.arquivo_nome }}</p>
              </div>
              <div class="text-right">
                <span class="text-xs font-bold px-2 py-1 rounded block" :class="badgeClass(recebimento.status)">
                  {{ recebimento.status }}
                </span>
                <p class="text-xs text-gray-500 mt-2">{{ getStatusMessage(recebimento.status) }}</p>
              </div>
            </div>
            <div
              v-if="recebimento.status === 'REPROVADO' && authStore.user?.perfil_empresa !== 'CLIENTE'"
              class="mt-3 flex gap-2"
            >
              <button @click="confirmarRecebimento(recebimento.id, 'VALIDADO')" class="px-3 py-1 text-xs bg-green-600 rounded hover:bg-green-500">
                Confirmar validado
              </button>
              <button @click="confirmarRecebimento(recebimento.id, 'REPROVADO')" class="px-3 py-1 text-xs bg-red-700 rounded hover:bg-red-600">
                Manter reprovado
              </button>
            </div>
          </div>
        </div>
        <p v-else class="text-gray-500">Nenhum recebimento registrado ainda.</p>
      </div>

      <div class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg p-6">
        <h2 class="text-xl font-display text-ancora-gold mb-4">Pendências</h2>
        <div v-if="pendencias.length" class="space-y-3">
          <div v-for="pendencia in pendencias" :key="pendencia.id" class="border border-red-500/20 rounded-md p-4 bg-red-500/5">
            <div class="flex items-center justify-between">
              <p class="text-white font-bold">{{ pendencia.titulo }}</p>
              <span class="text-xs font-bold text-red-300">{{ pendencia.status }}</span>
            </div>
            <p class="text-sm text-gray-300 mt-2 whitespace-pre-line">{{ pendencia.descricao }}</p>
          </div>
        </div>
        <p v-else class="text-gray-500">Nenhuma pendência em aberto.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import IntakeService from '@/services/intake.service'
import { useAuthStore } from '@/stores/auth'
import { useEmpresaStore } from '@/stores/empresa'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const empresaStore = useEmpresaStore()
const uiStore = useUiStore()

const submitting = ref(false)
const exporting = ref(false)
const savingPortal = ref(false)
const recebimentos = ref([])
const pendencias = ref([])
const checklists = ref([])
const portalClientes = ref([])
const ultimoLote = ref(null)
const portalClienteId = ref(null)
const exportCompetencia = ref(new Date().toISOString().slice(0, 7))
const selectedFile = ref(null)

const portalForm = reactive({
  slug: '',
  email_responsavel: '',
  telefone_responsavel: '',
  recebe_alertas: true,
})
const portalPublicUrl = computed(() => `https://seu-dominio.com.br/area_cliente/${portalForm.slug || buildDefaultSlug(empresaStore.activeEmpresa) || 'cliente'}`)

const form = ref({
  titulo: '',
  tipo_documento: 'FINANCEIRO',
  tipo_entrega: 'UPLOAD',
  competencia: new Date().toISOString().slice(0, 7),
  observacoes: '',
  portal_cliente: '',
})

onMounted(() => {
  hydratePortalDefaults()
  loadData()
})

watch(() => empresaStore.activeEmpresa?.id, () => {
  hydratePortalDefaults()
  loadData()
})

function hydratePortalDefaults() {
  const empresa = empresaStore.activeEmpresa
  if (!empresa) {
    return
  }

  if (!portalClienteId.value) {
    portalForm.slug = buildDefaultSlug(empresa)
  }
}

async function loadData() {
  try {
    const [recebimentosResp, pendenciasResp, checklistsResp, portalResp, lotesResp] = await Promise.all([
      IntakeService.getRecebimentos(),
      IntakeService.getPendencias(),
      IntakeService.getChecklists(),
      IntakeService.getPortalClientes(),
      IntakeService.getLotes(),
    ])

    recebimentos.value = recebimentosResp.results || []
    pendencias.value = pendenciasResp.results || []
    checklists.value = checklistsResp.results || []
    portalClientes.value = portalResp.results || []
    ultimoLote.value = (lotesResp.results || [])[0] || null

    syncPortalState()
  } catch (error) {
    uiStore.showNotification('Erro ao carregar dados da central de recebimentos.', 'error')
    console.error(error)
  }
}

function syncPortalState() {
  const portalPrincipal = portalClientes.value[0]

  if (!portalPrincipal) {
    portalClienteId.value = null
    form.value.portal_cliente = ''
    portalForm.slug = buildDefaultSlug(empresaStore.activeEmpresa)
    portalForm.email_responsavel = ''
    portalForm.telefone_responsavel = ''
    portalForm.recebe_alertas = true
    return
  }

  portalClienteId.value = portalPrincipal.id
  form.value.portal_cliente = portalPrincipal.id
  portalForm.slug = portalPrincipal.slug
  portalForm.email_responsavel = portalPrincipal.email_responsavel || ''
  portalForm.telefone_responsavel = portalPrincipal.telefone_responsavel || ''
  portalForm.recebe_alertas = portalPrincipal.recebe_alertas
}

function handleFileChange(event) {
  selectedFile.value = event.target.files[0] || null
}

async function salvarPortal() {
  savingPortal.value = true
  try {
    const payload = {
      slug: portalForm.slug,
      email_responsavel: portalForm.email_responsavel || null,
      telefone_responsavel: portalForm.telefone_responsavel || null,
      recebe_alertas: portalForm.recebe_alertas,
    }

    if (portalClienteId.value) {
      await IntakeService.updatePortalCliente(portalClienteId.value, payload)
    } else {
      await IntakeService.createPortalCliente(payload)
    }

    uiStore.showNotification('Configuração da área do cliente salva com sucesso.', 'success')
    await loadData()
  } catch (error) {
    uiStore.showNotification('Erro ao salvar a configuração da área do cliente.', 'error')
    console.error(error)
  } finally {
    savingPortal.value = false
  }
}

async function submitRecebimento() {
  if (!selectedFile.value) {
    uiStore.showNotification('Selecione o arquivo recebido para registrar.', 'warning')
    return
  }

  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('titulo', form.value.titulo)
    payload.append('tipo_documento', form.value.tipo_documento)
    payload.append('tipo_entrega', form.value.tipo_entrega)
    payload.append('competencia', `${form.value.competencia}-01`)
    payload.append('arquivo', selectedFile.value)
    payload.append('observacoes', form.value.observacoes || '')

    if (form.value.portal_cliente) {
      payload.append('portal_cliente', form.value.portal_cliente)
    }

    const response = await IntakeService.createRecebimento(payload)
    const message = response.status === 'NOVO'
      ? 'Documento enviado como NOVO. Aguardando triagem da equipe.'
      : response.status === 'VALIDADO'
      ? 'Documento validado com sucesso!'
      : 'Documento registrado com restrições. Verifique com a equipe.'
    uiStore.showNotification(message, response.status === 'VALIDADO' ? 'success' : response.status === 'NOVO' ? 'warning' : 'error')

    form.value = {
      titulo: '',
      tipo_documento: 'FINANCEIRO',
      tipo_entrega: 'UPLOAD',
      competencia: new Date().toISOString().slice(0, 7),
      observacoes: '',
      portal_cliente: portalClienteId.value || '',
    }
    selectedFile.value = null
    await loadData()
  } catch (error) {
    uiStore.showNotification('Erro ao registrar documento.', 'error')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

async function confirmarRecebimento(documentoId, status) {
  try {
    await IntakeService.confirmarRecebimento({
      documento_id: documentoId,
      status,
      observacoes: status === 'VALIDADO'
        ? 'Validação confirmada manualmente pela operação.'
        : 'Documento mantido como reprovado pela operação.',
    })
    uiStore.showNotification('Status do documento atualizado.', 'success')
    await loadData()
  } catch (error) {
    uiStore.showNotification('Erro ao confirmar documento.', 'error')
    console.error(error)
  }
}

async function exportarQuestor() {
  exporting.value = true
  try {
    ultimoLote.value = await IntakeService.exportarQuestor({
      competencia: exportCompetencia.value,
    })
    uiStore.showNotification('Pacote Questor gerado com sucesso.', 'success')
  } catch (error) {
    uiStore.showNotification('Erro ao exportar para o Questor.', 'error')
    console.error(error)
  } finally {
    exporting.value = false
  }
}

function buildDefaultSlug(empresa) {
  const base = empresa?.nome_fantasia || empresa?.razao_social || empresa?.cnpj || 'cliente'
  return base
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function formatCompetencia(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR', {
    month: '2-digit',
    year: 'numeric',
  })
}

function formatCnpj(cnpj) {
  if (!cnpj) return ''
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function getStatusMessage(status) {
  if (status === 'NOVO') {
    return 'Aguardando triagem ou vinculação'
  }
  if (status === 'VALIDADO') {
    return 'Documento validado'
  }
  if (status === 'REPROVADO') {
    return 'Documento reprovado'
  }
  return 'Status desconhecido'
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
