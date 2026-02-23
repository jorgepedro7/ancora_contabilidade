<script setup>
import { useAuthStore } from '@/stores/auth'
import { useEmpresaStore } from '@/stores/empresa'

const authStore = useAuthStore()
const empresaStore = useEmpresaStore()

function handleLogout() {
  authStore.logout()
}
</script>

<template>
  <header class="bg-ancora-black text-white p-4 flex justify-between items-center border-b border-ancora-navy">
    <div class="flex items-center">
      <h1 class="text-2xl font-display text-ancora-gold uppercase tracking-wider">ÂNCORA</h1>
      <span class="ml-4 text-sm text-gray-400" v-if="empresaStore.activeEmpresa">
        Empresa Ativa: <span class="font-bold">{{ empresaStore.activeEmpresa.nome_fantasia || empresaStore.activeEmpresa.razao_social }}</span>
      </span>
    </div>
    <nav>
      <ul class="flex space-x-4">
        <li>
          <a href="#" @click.prevent="handleLogout" class="text-ancora-gold hover:text-ancora-gold/80 transition-colors">Sair</a>
        </li>
      </ul>
    </nav>
  </header>
</template>
