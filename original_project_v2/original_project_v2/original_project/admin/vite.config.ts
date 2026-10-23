import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// The Admin app calls the Flask API directly (cross-origin), so it does not
// use a Vite /api proxy. The API base URL comes from VITE_API_BASE_URL
// (see .env.development). The admin dev server runs on port 5174.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
  },
})