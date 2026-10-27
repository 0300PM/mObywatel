import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    assetsInlineLimit: 0,
    rollupOptions: {
      input: {
        aplikacja: fileURLToPath(new URL('./index.html', import.meta.url)),
        komputer: fileURLToPath(new URL('./komputer.html', import.meta.url))
      }
    }
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': { target: 'http://127.0.0.1:8790', changeOrigin: false }
    }
  }
})
