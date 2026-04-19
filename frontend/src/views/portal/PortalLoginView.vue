<template>
  <div class="min-h-screen bg-ancora-black flex items-center justify-center px-4">
    <div class="w-full max-w-sm space-y-6">
      <!-- Logo / Cabeçalho -->
      <div class="text-center">
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Âncora Contabilidade</h1>
        <p class="text-gray-400 text-sm">Portal do cliente</p>
        <p v-if="slug" class="text-xs text-gray-600 font-mono mt-1">{{ slug }}</p>
      </div>

      <!-- Card de login -->
      <form
        class="bg-ancora-black/60 border border-ancora-gold/20 rounded-lg p-6 space-y-4"
        @submit.prevent="fazerLogin"
      >
        <div>
          <label for="email" class="block text-sm text-gray-300 mb-1">E-mail</label>
          <input
            id="email"
            v-model="form.email"
            required
            type="email"
            autocomplete="username"
            placeholder="seu@email.com"
            class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white placeholder-gray-600 focus:outline-none focus:border-ancora-gold/50"
          />
        </div>
        <div>
          <label for="password" class="block text-sm text-gray-300 mb-1">Senha</label>
          <input
            id="password"
            v-model="form.password"
            required
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white placeholder-gray-600 focus:outline-none focus:border-ancora-gold/50"
          />
        </div>

        <p v-if="erro" class="text-red-400 text-sm">{{ erro }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/80 disabled:opacity-50 transition-colors"
        >
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p class="text-center text-xs text-gray-600">
        Acesso exclusivo para clientes do portal. Equipe interna usa o
        <a href="/login" class="text-ancora-gold/60 hover:text-ancora-gold underline">login padrão</a>.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const slug = route.params.slug
const loading = ref(false)
const erro = ref('')
const form = ref({ email: '', password: '' })

async function fazerLogin() {
  loading.value = true
  erro.value = ''
  try {
    // authStore.login() já redireciona o CLIENTE para /area_cliente/:slug após o login
    await authStore.login({ email: form.value.email, password: form.value.password })
  } catch (error) {
    const msg =
      error?.response?.data?.detail ||
      error?.response?.data?.errors?.[0]?.message ||
      'E-mail ou senha incorretos.'
    erro.value = msg
  } finally {
    loading.value = false
  }
}
</script>
