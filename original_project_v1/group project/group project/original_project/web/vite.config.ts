import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// The dev server proxies /api to the Flask backend so the frontend can use
// relative /api/v1 paths without CORS issues during development.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5006',
        changeOrigin: true,
      },
      // Uploaded product images are served by Flask under /uploads/.
      '/uploads': {
        target: 'http://127.0.0.1:5006',
        changeOrigin: true,
      },
    },
  },
})
