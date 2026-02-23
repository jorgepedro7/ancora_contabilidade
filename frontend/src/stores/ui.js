import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const notification = ref(null) // { message: '...', type: 'success/error/warning' }

  function setLoading(state) {
    isLoading.value = state
  }

  function showNotification(message, type = 'info', duration = 3000) {
    notification.value = { message, type }
    if (duration > 0) {
      setTimeout(() => {
        notification.value = null
      }, duration)
    }
  }

  function clearNotification() {
    notification.value = null
  }

  return { isLoading, notification, setLoading, showNotification, clearNotification }
})
