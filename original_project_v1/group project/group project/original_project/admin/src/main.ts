import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAdminAuthStore } from './stores/auth'
import './styles/tokens.css'
import './styles/base.css'

const auth = useAdminAuthStore()
auth.restoreSession()

createApp(App).use(router).mount('#app')