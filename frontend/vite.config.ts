// FORCE REDEPLOY to pick up new VITE_API_URL env var: 2025-06-18 07:05
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    // Prevent variable name mangling that causes "api.post is not a function" errors
    minify: 'terser',
    terserOptions: {
      mangle: {
        // Keep function names and important variables
        keep_fnames: true,
        keep_classnames: true,
        // Preserve critical API-related identifiers
        reserved: [
          'apiClient', 'axios', 'api', 'apiService',
          'post', 'get', 'put', 'delete', 'patch',
          'chat', 'analyzeWriting', 'submitFeedback',
          'healthCheck', 'getDocuments', 'createDocument',
          'updateDocument', 'deleteDocument', 'safeApiCall',
          'handleApiError', 'AxiosInstance', 'AxiosError'
        ]
      },
      compress: {
        // Keep function names in production for better debugging
        keep_fnames: true,
        keep_classnames: true,
        drop_console: false, // Keep console logs for debugging
        // Don't optimize function calls that might break our API
        reduce_funcs: false,
        reduce_vars: false
      }
    },
    // Ensure proper source maps for debugging
    sourcemap: true,
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // Additional rollup options to preserve function names
    rollupOptions: {
      output: {
        // Preserve function names in output
        preserveModules: false,
        // Use more descriptive chunk names
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId 
            ? chunkInfo.facadeModuleId.split('/').pop()?.replace('.ts', '').replace('.tsx', '') 
            : 'chunk';
          return `assets/${facadeModuleId}-[hash].js`;
        }
      }
    }
  },
  // Ensure proper environment variable handling
  define: {
    // Explicitly define environment variables
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
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
