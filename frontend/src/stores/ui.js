import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const notification = ref(null) // { message: '...', type: 'success/error/warning' }
  let notificationTimeoutId = null

  // Tema: 'dark' (padrão) ou 'light'
  const theme = ref(localStorage.getItem('ancora-theme') || 'dark')

  function applyTheme(value) {
    const html = document.documentElement
    html.classList.remove('dark', 'light')
    html.classList.add(value)
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('ancora-theme', theme.value)
    applyTheme(theme.value)
  }

  function initTheme() {
    applyTheme(theme.value)
  }

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

  return {
    isLoading, notification, theme,
    setLoading, showNotification, clearNotification,
    toggleTheme, initTheme,
  }
})
