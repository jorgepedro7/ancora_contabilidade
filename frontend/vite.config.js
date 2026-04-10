import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const proxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000'
const allowedHosts = (process.env.VITE_ALLOWED_HOSTS || 'localhost,127.0.0.1').split(',').map(h => h.trim()).filter(Boolean)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts,
    hmr: {
      host: 'localhost',
      port: 3000,
    },
    proxy: {
      '/api': {
        target: proxyTarget, // Django backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
