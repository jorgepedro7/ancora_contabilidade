<template>
  <div class="p-4 space-y-6 max-w-5xl mx-auto">
    <!-- Cabeçalho -->
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Configurações</p>
          <h1 class="text-3xl font-display text-ancora-gold mb-1">Equipe</h1>
          <p class="text-gray-400 text-sm">Gerencie os membros da equipe interna.</p>
        </div>
        <button
          type="button"
          @click="abrirModal()"
          class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 text-sm"
        >
          + Adicionar membro
        </button>
      </div>
    </section>

    <!-- Filtros -->
    <div class="flex gap-2">
      <button
        v-for="f in filtros"
        :key="f.value"
        @click="filtroAtivo = f.value"
        :class="[
          'px-3 py-1 rounded-full text-sm border',
          filtroAtivo === f.value
            ? 'bg-ancora-gold text-ancora-black border-ancora-gold font-bold'
            : 'text-gray-400 border-gray-700 hover:border-ancora-gold/50 hover:text-ancora-gold',
        ]"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Tabela -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500 text-sm">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="border-b border-ancora-gold/20">
          <tr class="text-gray-500 text-xs uppercase tracking-wide">
            <th class="text-left px-4 py-3">Nome</th>
            <th class="text-left px-4 py-3">E-mail</th>
            <th class="text-left px-4 py-3">Perfil</th>
            <th class="text-left px-4 py-3">Status</th>
            <th class="text-left px-4 py-3">Entrada</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="membro in listaFiltrada"
            :key="membro.id"
            class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20"
          >
            <td class="px-4 py-3 text-white">{{ membro.nome }}</td>
            <td class="px-4 py-3 text-gray-400">{{ membro.email }}</td>
            <td class="px-4 py-3">
              <span :class="badgePerfil(membro.perfil_empresa)" class="text-xs font-bold px-2 py-1 rounded">
                {{ membro.perfil_empresa }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                :class="membro.is_active ? 'text-green-400' : 'text-gray-500'"
                class="text-xs font-bold"
              >
                {{ membro.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatData(membro.date_joined) }}</td>
            <td class="px-4 py-3 flex gap-2 justify-end">
              <button
                type="button"
                @click="abrirModal(membro)"
                class="text-xs text-ancora-gold hover:underline"
              >
                Editar
              </button>
              <button
                type="button"
                @click="toggleAtivo(membro)"
                class="text-xs text-gray-400 hover:text-red-400"
              >
                {{ membro.is_active ? 'Desativar' : 'Ativar' }}
              </button>
            </td>
          </tr>
          <tr v-if="!listaFiltrada.length">
            <td colspan="6" class="px-4 py-6 text-center text-gray-500 text-sm">Nenhum membro encontrado.</td>
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
        <h2 class="text-xl font-display text-ancora-gold">
          {{ editando ? 'Editar membro' : 'Adicionar membro' }}
        </h2>
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
              :disabled="!!editando"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white disabled:opacity-50"
            />
          </div>
          <div v-if="!editando">
            <label class="block text-sm text-gray-300 mb-1">Senha temporária *</label>
            <input
              v-model="form.senha_temporaria"
              required
              type="password"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Perfil *</label>
            <select
              v-model="form.perfil"
              required
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            >
              <option value="ADMIN">Administrador</option>
              <option value="CONTADOR">Contador</option>
              <option value="AUXILIAR">Auxiliar Contábil</option>
              <option value="FINANCEIRO">Financeiro</option>
              <option value="CONSULTA">Consulta</option>
            </select>
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
import { computed, onMounted, ref } from 'vue'
import UsuariosService from '@/services/usuarios.service'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const membros = ref([])
const loading = ref(false)
const filtroAtivo = ref('todos')
const modalAberto = ref(false)
const editando = ref(null)
const salvando = ref(false)

const filtros = [
  { label: 'Todos', value: 'todos' },
  { label: 'Ativos', value: 'ativos' },
  { label: 'Inativos', value: 'inativos' },
]

const form = ref(formVazio())

function formVazio() {
  return { nome: '', email: '', senha_temporaria: '', perfil: 'CONTADOR' }
}

const listaFiltrada = computed(() => {
  if (filtroAtivo.value === 'ativos') return membros.value.filter(m => m.is_active)
  if (filtroAtivo.value === 'inativos') return membros.value.filter(m => !m.is_active)
  return membros.value
})

onMounted(carregar)

async function carregar() {
  loading.value = true
  try {
    const resp = await UsuariosService.listEquipe()
    membros.value = resp.results || resp || []
  } catch {
    uiStore.showNotification('Erro ao carregar equipe.', 'error')
  } finally {
    loading.value = false
  }
}

function abrirModal(membro = null) {
  editando.value = membro
  form.value = membro
    ? { nome: membro.nome, email: membro.email, perfil: membro.perfil_empresa, senha_temporaria: '' }
    : formVazio()
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  editando.value = null
}

async function salvar() {
  salvando.value = true
  try {
    if (editando.value) {
      const updated = await UsuariosService.updateUsuario(editando.value.id, {
        nome: form.value.nome,
        perfil: form.value.perfil,
      })
      const idx = membros.value.findIndex(m => m.id === editando.value.id)
      if (idx !== -1) membros.value[idx] = updated
      uiStore.showNotification('Membro atualizado.', 'success')
    } else {
      const created = await UsuariosService.createUsuario(form.value)
      membros.value = [created, ...membros.value]
      uiStore.showNotification('Membro adicionado.', 'success')
    }
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

async function toggleAtivo(membro) {
  if (membro.is_active) {
    try {
      await UsuariosService.deleteUsuario(membro.id)
      membro.is_active = false
      uiStore.showNotification('Usuário desativado.', 'success')
    } catch (error) {
      const msg =
        error?.response?.data?.errors?.[0]?.message ||
        error?.response?.data?.message ||
        'Erro ao desativar.'
      uiStore.showNotification(msg, 'error')
    }
  } else {
    try {
      const updated = await UsuariosService.updateUsuario(membro.id, { is_active: true })
      membro.is_active = updated.is_active
      uiStore.showNotification('Usuário ativado.', 'success')
    } catch {
      uiStore.showNotification('Erro ao ativar usuário.', 'error')
    }
  }
}

function badgePerfil(perfil) {
  const map = {
    ADMIN: 'bg-ancora-gold/20 text-ancora-gold',
    CONTADOR: 'bg-blue-500/20 text-blue-300',
    AUXILIAR: 'bg-purple-500/20 text-purple-300',
    FINANCEIRO: 'bg-green-600/20 text-green-300',
    CONSULTA: 'bg-gray-500/20 text-gray-300',
  }
  return map[perfil] || 'bg-gray-500/20 text-gray-300'
}

function formatData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
