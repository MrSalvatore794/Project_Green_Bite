import { computed, reactive } from 'vue'
import { api, setAccessToken } from '../services/api'

export interface User {
  id: number
  name: string
  email: string
  phone: string | null
  role: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

interface UserResponse {
  user: User
}

const TOKEN_KEY = 'greenbite.token'

const state = reactive({
  token: null as string | null,
  user: null as User | null,
})

const isAuthenticated = computed(() => state.token !== null)

function persistToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

function applySession(token: string, user: User): void {
  state.token = token
  state.user = user
  setAccessToken(token)
  persistToken(token)
}

async function login(email: string, password: string): Promise<void> {
  const data = await api.post<LoginResponse>('/auth/login', { email, password })
  applySession(data.access_token, data.user)
}

async function register(name: string, email: string, phone: string, password: string): Promise<void> {
  await api.post('/auth/register', { name, email, phone, password })
  await login(email, password)
}

async function loadCurrentUser(): Promise<void> {
  if (!state.token) return
  const data = await api.get<UserResponse>('/users/me')
  state.user = data.user
}

async function restoreSession(): Promise<void> {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) return
  setAccessToken(token)
  state.token = token
  try {
    const data = await api.get<UserResponse>('/users/me')
    state.user = data.user
  } catch {
    logout()
  }
}

function logout(): void {
  state.token = null
  state.user = null
  setAccessToken(null)
  persistToken(null)
}

export function useAuthStore() {
  return { state, isAuthenticated, login, register, logout, loadCurrentUser, restoreSession }
}
