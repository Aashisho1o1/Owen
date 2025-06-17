// FORCE REDEPLOY to pick up new backend URL: 2025-01-21 18:00
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  }
})
