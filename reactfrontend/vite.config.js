import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  define: {
    'import.meta.env.DEV': mode === 'development',
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
        manualChunks: {
          // Split vendor chunks for better caching
          react: ['react', 'react-dom'],
          vendor: ['axios', 'react-router-dom']
        }
      }
    },
    // Production-specific optimizations
    minify: 'terser',
    sourcemap: mode !== 'production', // Disable sourcemaps in production
    chunkSizeWarningLimit: 1000 // Increase chunk size warning limit (in kB)
  },
  // Netlify-specific base path (only if deploying to subdirectory)
  base: mode === 'production' ? '/' : '/'
}));