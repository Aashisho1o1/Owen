// FORCE REDEPLOY to pick up new VITE_API_URL env var: 2025-06-18 07:05
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  }
})
