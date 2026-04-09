import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const notification = ref(null) // { message: '...', type: 'success/error/warning' }
  let notificationTimeoutId = null

  function setLoading(state) {
    isLoading.value = state
  }

  function showNotification(message, type = 'info', duration = 3000) {
    if (notificationTimeoutId) {
      clearTimeout(notificationTimeoutId)
      notificationTimeoutId = null
    }

    notification.value = { message, type }

    if (duration > 0) {
      notificationTimeoutId = setTimeout(() => {
        notification.value = null
        notificationTimeoutId = null
      }, duration)
    }
  }

  function clearNotification() {
    if (notificationTimeoutId) {
      clearTimeout(notificationTimeoutId)
      notificationTimeoutId = null
    }
    notification.value = null
  }

  return { isLoading, notification, setLoading, showNotification, clearNotification }
})
