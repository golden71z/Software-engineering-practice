import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 8090,
    strictPort: true, // 端口被占用时直接报错，避免悄悄换端口导致代理和 CORS 对不上
    proxy: {
      // 开发期把 /api 和 /static 转发给后端，浏览器看到的是同源请求，不触发 CORS
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/static': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
