import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  server: {
    port: 8090,
    open: false,
    proxy: {
      // 将 /api 开头的请求代理到后端，避免开发阶段的跨域问题
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
