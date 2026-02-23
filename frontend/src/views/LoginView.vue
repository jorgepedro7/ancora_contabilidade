<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUiStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  uiStore.setLoading(true)
  errorMessage.value = ''
  try {
    await authStore.login({ email: email.value, password: password.value })
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.'
    uiStore.showNotification(errorMessage.value, 'error')
  } finally {
    uiStore.setLoading(false)
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-ancora-black">
    <div class="w-full max-w-md p-8 space-y-6 bg-ancora-black/50 rounded-lg shadow-lg border border-ancora-gold/30">
      <h2 class="text-3xl font-display font-bold text-center text-ancora-gold uppercase tracking-wider">Âncora</h2>
      <p class="text-center text-gray-400">Entre na sua conta</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="email" class="block text-sm font-body text-gray-300">E-mail</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"
            placeholder="seu@email.com"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-body text-gray-300">Senha</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            class="mt-1 block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md shadow-sm focus:outline-none focus:ring-ancora-gold focus:border-ancora-gold sm:text-sm text-white"
            placeholder="********"
          />
        </div>
        <div v-if="errorMessage" class="text-red-500 text-sm text-center">
          {{ errorMessage }}
        </div>
        <div>
          <button
            type="submit"
            :disabled="uiStore.isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-bold text-ancora-black bg-ancora-gold hover:bg-ancora-gold/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ancora-gold disabled:opacity-50"
          >
            <span v-if="uiStore.isLoading">Entrando...</span>
            <span v-else>Entrar</span>
          </button>
        </div>
      </form>
      <div class="text-center">
        <a href="#" class="text-sm text-ancora-gold hover:underline">Esqueceu sua senha?</a>
      </div>
    </div>
  </div>
</template>
