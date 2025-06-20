// FORCE REDEPLOY to pick up new VITE_API_URL env var: 2025-06-18 07:05
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    // Prevent variable name mangling that causes "Be.post is not a function" errors
    minify: 'terser',
    terserOptions: {
      mangle: {
        // Keep function names and important variables
        keep_fnames: true,
        reserved: ['apiClient', 'axios', 'api', 'post', 'get', 'put', 'delete']
      },
      compress: {
        // Keep function names in production for better debugging
        keep_fnames: true,
        drop_console: false, // Keep console logs for debugging
      }
    },
    // Ensure proper source maps for debugging
    sourcemap: true,
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000
  },
  // Ensure proper environment variable handling
  define: {
    // Explicitly define environment variables
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL),
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
