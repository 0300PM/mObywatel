import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'
import type { ServerResponse } from 'node:http'

const CEL_API = process.env.API_TARGET || 'http://127.0.0.1:8790'

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
      '/api': {
        target: CEL_API,
        changeOrigin: false,
        configure: (proxy) => {
          proxy.on('error', (_blad, _zadanie, odpowiedz) => {
            const r = odpowiedz as ServerResponse | undefined
            if (!r || r.headersSent || r.writableEnded) return
            const tresc = JSON.stringify({
              error: `Serwer API nie odpowiada na ${CEL_API}. Uruchom python3 serwer/server.py `
                + 'albo docker compose up -d --force-recreate.'
            })
            r.writeHead(503, {
              'Content-Type': 'application/json; charset=utf-8',
              'Content-Length': Buffer.byteLength(tresc),
              'Cache-Control': 'no-store'
            })
            r.end(tresc)
          })
        }
      }
    }
  }
})
