import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api/login': { target: 'http://localhost:8008', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/signup': { target: 'http://localhost:8008', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/users': { target: 'http://localhost:8008', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/owner': { target: 'http://localhost:8011', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/reviews': { target: 'http://localhost:8010', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/restaurants': { target: 'http://localhost:8009', rewrite: (path) => path.replace(/^\/api/, '') },
      '/api/favorites': { target: 'http://localhost:8008', rewrite: (path) => path.replace(/^\/api/, '') },
    },
  },
})
