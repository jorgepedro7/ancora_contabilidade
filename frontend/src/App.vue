<script setup>
import { RouterView, useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-ancora-black text-white">
    <AppHeader v-if="route.name !== 'login'" />
    <div class="flex flex-1 overflow-hidden">
      <AppSidebar v-if="route.name !== 'login'" />
      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>
    <AppFooter v-if="route.name !== 'login'" />
  </div>
</template>

<style>
/* Basic global styles, consider moving to main.css */
body {
  font-family: 'Montserrat', sans-serif;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'Cinzel', 'Cormorant Garamond', serif;
}
</style>
