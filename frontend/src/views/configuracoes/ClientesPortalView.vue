<template>
  <div class="p-4 space-y-6 max-w-5xl mx-auto">
    <!-- Cabeçalho -->
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Configurações</p>
          <h1 class="text-3xl font-display text-ancora-gold mb-1">Clientes do Portal</h1>
          <p class="text-gray-400 text-sm">Gerencie os acessos dos clientes ao portal de envio de documentos.</p>
        </div>
        <button
          type="button"
          @click="abrirModal()"
          class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 text-sm"
        >
          + Adicionar cliente
        </button>
      </div>
    </section>

    <!-- Tabela -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500 text-sm">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="border-b border-ancora-gold/20">
          <tr class="text-gray-500 text-xs uppercase tracking-wide">
            <th class="text-left px-4 py-3">Nome</th>
            <th class="text-left px-4 py-3">E-mail</th>
            <th class="text-left px-4 py-3">Portal</th>
            <th class="text-left px-4 py-3">Status</th>
            <th class="text-left px-4 py-3">Entrada</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="cliente in clientes"
            :key="cliente.id"
            class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20"
          >
            <td class="px-4 py-3 text-white">{{ cliente.nome }}</td>
            <td class="px-4 py-3 text-gray-400">{{ cliente.email }}</td>
            <td class="px-4 py-3 text-gray-400 font-mono text-xs">
              {{ cliente.portal_cliente_slug || '—' }}
            </td>
            <td class="px-4 py-3">
              <span
                :class="cliente.is_active ? 'text-green-400' : 'text-gray-500'"
                class="text-xs font-bold"
              >
                {{ cliente.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatData(cliente.date_joined) }}</td>
            <td class="px-4 py-3 flex gap-2 justify-end">
              <button
                type="button"
                @click="toggleAtivo(cliente)"
                class="text-xs text-gray-400 hover:text-red-400"
              >
                {{ cliente.is_active ? 'Desativar' : 'Ativar' }}
              </button>
            </td>
          </tr>
          <tr v-if="!clientes.length">
            <td colspan="6" class="px-4 py-6 text-center text-gray-500 text-sm">Nenhum cliente encontrado.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Modal -->
    <div
      v-if="modalAberto"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="fecharModal"
    >
      <div class="bg-ancora-black border border-ancora-gold/30 rounded-lg p-6 w-full max-w-md space-y-4">
        <h2 class="text-xl font-display text-ancora-gold">Adicionar cliente</h2>
        <form class="space-y-3" @submit.prevent="salvar">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Nome *</label>
            <input
              v-model="form.nome"
              required
              type="text"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">E-mail *</label>
            <input
              v-model="form.email"
              required
              type="email"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Senha temporária *</label>
            <input
              v-model="form.senha_temporaria"
              required
              type="password"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Portal vinculado</label>
            <select
              v-model="form.portal_cliente"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            >
              <option value="">— Nenhum —</option>
              <option v-for="p in portais" :key="p.id" :value="p.id">
                {{ p.slug }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              Ao vincular um portal, o cliente acessa diretamente o link <span class="font-mono">/portal/:slug/login</span>.
            </p>
          </div>
          <div class="flex gap-2 justify-end pt-2">
            <button type="button" @click="fecharModal" class="px-4 py-2 text-sm text-gray-400 hover:text-white">
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvando"
              class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold text-sm hover:bg-ancora-gold/80 disabled:opacity-50"
            >
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import IntakeService from '@/services/intake.service'
import UsuariosService from '@/services/usuarios.service'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const clientes = ref([])
const portais = ref([])
const loading = ref(false)
const modalAberto = ref(false)
const salvando = ref(false)
const form = ref({ nome: '', email: '', senha_temporaria: '', portal_cliente: '' })

onMounted(carregar)

async function carregar() {
  loading.value = true
  try {
    const [clientesResp, portaisResp] = await Promise.all([
      UsuariosService.listClientes(),
      IntakeService.getPortalClientes(),
    ])
    clientes.value = clientesResp.results || clientesResp || []
    portais.value = portaisResp.results || portaisResp || []
  } catch {
    uiStore.showNotification('Erro ao carregar dados.', 'error')
  } finally {
    loading.value = false
  }
}

function abrirModal() {
  form.value = { nome: '', email: '', senha_temporaria: '', portal_cliente: '' }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  form.value = { nome: '', email: '', senha_temporaria: '', portal_cliente: '' }
}

async function salvar() {
  salvando.value = true
  try {
    const payload = { ...form.value, perfil: 'CLIENTE' }
    if (!payload.portal_cliente) delete payload.portal_cliente
    const created = await UsuariosService.createUsuario(payload)
    clientes.value = [created, ...clientes.value]
    uiStore.showNotification('Cliente adicionado.', 'success')
    fecharModal()
  } catch (error) {
    const msg =
      error?.response?.data?.errors?.[0]?.message ||
      error?.response?.data?.message ||
      'Erro ao salvar.'
    uiStore.showNotification(msg, 'error')
  } finally {
    salvando.value = false
  }
}

async function toggleAtivo(cliente) {
  if (cliente.is_active) {
    try {
      await UsuariosService.deleteUsuario(cliente.id)
      const idx = clientes.value.findIndex(c => c.id === cliente.id)
      if (idx !== -1) clientes.value[idx] = { ...clientes.value[idx], is_active: false }
      uiStore.showNotification('Cliente desativado.', 'success')
    } catch (error) {
      const msg =
        error?.response?.data?.errors?.[0]?.message ||
        error?.response?.data?.message ||
        'Erro ao desativar.'
      uiStore.showNotification(msg, 'error')
    }
  } else {
    try {
      const updated = await UsuariosService.reativarUsuario(cliente.id)
      const idx = clientes.value.findIndex(c => c.id === cliente.id)
      if (idx !== -1) clientes.value[idx] = updated
      uiStore.showNotification('Cliente ativado.', 'success')
    } catch (error) {
      const msg =
        error?.response?.data?.errors?.[0]?.message ||
        error?.response?.data?.message ||
        'Erro ao ativar cliente.'
      uiStore.showNotification(msg, 'error')
    }
  }
}

function formatData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
