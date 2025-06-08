import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173
  },
  preview: {
    host: true,
    port: 4173,
    allowedHosts: [
      'healthcheck.railway.app',
      '.railway.app',
      'localhost'
    ]
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
