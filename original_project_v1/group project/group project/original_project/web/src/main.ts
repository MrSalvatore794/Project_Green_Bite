import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/tokens.css'
import './styles/base.css'

const auth = useAuthStore()
auth.restoreSession()

createApp(App).use(router).mount('#app')
