<script setup>
import { computed } from 'vue'

import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const toneClass = computed(() => {
  const type = uiStore.notification?.type

  if (type === 'success') {
    return 'border-green-500/40 bg-green-500/15 text-green-100'
  }

  if (type === 'warning') {
    return 'border-yellow-500/40 bg-yellow-500/15 text-yellow-100'
  }

  if (type === 'error') {
    return 'border-red-500/40 bg-red-500/15 text-red-100'
  }

  return 'border-ancora-gold/30 bg-ancora-navy/70 text-white'
})
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-2"
  >
    <div
      v-if="uiStore.notification"
      class="fixed right-4 top-4 z-[60] w-[min(28rem,calc(100vw-2rem))] rounded-xl border px-4 py-3 shadow-2xl backdrop-blur"
      :class="toneClass"
      role="status"
      aria-live="polite"
    >
      <div class="flex items-start gap-3">
        <div class="flex-1 text-sm leading-6">{{ uiStore.notification.message }}</div>
        <button
          type="button"
          class="shrink-0 text-xs uppercase tracking-wide opacity-80 transition-opacity hover:opacity-100"
          @click="uiStore.clearNotification()"
        >
          Fechar
        </button>
      </div>
    </div>
  </Transition>
</template>
