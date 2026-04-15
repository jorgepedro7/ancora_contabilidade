<script setup>
import { computed, onMounted } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppToast from '@/components/ui/AppToast.vue'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const uiStore = useUiStore()

// Rotas que não exibem o layout interno do escritório
const isClientPortal = computed(() => route.meta.clientPortal === true)
const isLogin = computed(() => route.name === 'login')
const showBackofficeLayout = computed(() => !isLogin.value && !isClientPortal.value)

onMounted(() => {
  uiStore.initTheme()
})
</script>

<template>
  <div class="flex h-screen flex-col bg-ancora-black" style="color: rgb(var(--color-text))">
    <AppHeader v-if="showBackofficeLayout" />
    <div class="flex min-h-0 flex-1 overflow-hidden">
      <AppSidebar v-if="showBackofficeLayout" class="min-h-0 overflow-y-auto flex-shrink-0" />
      <main class="min-h-0 flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>
    <AppFooter v-if="showBackofficeLayout" />
    <AppToast />
  </div>
</template>
