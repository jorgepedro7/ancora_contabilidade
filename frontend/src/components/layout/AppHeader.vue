<script setup>
import { useAuthStore } from '@/stores/auth'
import { useEmpresaStore } from '@/stores/empresa'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const empresaStore = useEmpresaStore()
const uiStore = useUiStore()
</script>

<template>
  <header class="bg-ancora-black border-b border-ancora-navy/60 px-4 py-3 flex justify-between items-center flex-shrink-0">
    <div class="flex items-center gap-4">
      <h1 class="text-2xl font-display text-ancora-gold uppercase tracking-wider">ÂNCORA</h1>
      <span v-if="empresaStore.activeEmpresa" class="text-sm" style="color: rgb(var(--color-text-muted))">
        <span class="hidden sm:inline">Empresa ativa: </span>
        <span class="font-bold" style="color: rgb(var(--color-text))">
          {{ empresaStore.activeEmpresa.nome_fantasia || empresaStore.activeEmpresa.razao_social }}
        </span>
      </span>
    </div>

    <div class="flex items-center gap-3">
      <!-- Toggle de tema -->
      <button
        @click="uiStore.toggleTheme()"
        class="p-2 rounded-md border border-ancora-navy/60 hover:border-ancora-gold/50 transition-colors"
        :title="uiStore.theme === 'dark' ? 'Mudar para tema claro' : 'Mudar para tema escuro'"
      >
        <span v-if="uiStore.theme === 'dark'" class="text-sm">☀️</span>
        <span v-else class="text-sm">🌙</span>
      </button>

      <a
        href="#"
        @click.prevent="authStore.logout()"
        class="text-sm text-ancora-gold hover:text-ancora-gold/70 transition-colors"
      >
        Sair
      </a>
    </div>
  </header>
</template>
