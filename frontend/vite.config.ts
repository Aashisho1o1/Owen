// FORCE REDEPLOY to pick up new VITE_API_URL env var: 2025-06-18 07:05
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Keep all console messages in production for debugging (only remove debugger)
  esbuild: {
    drop: process.env.NODE_ENV === 'production' ? ['debugger'] : []
  },
  build: {
    outDir: 'dist',
    // Use faster esbuild for minification instead of terser
    minify: 'esbuild',
    // Ensure proper source maps for debugging
    sourcemap: true,
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000
  },
  // Better error handling during development
  server: {
    port: 5174,
    strictPort: false,
    host: true,
    hmr: {
      overlay: true
    }
  }
})
