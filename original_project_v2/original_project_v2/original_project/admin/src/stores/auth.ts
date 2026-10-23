import { computed, reactive } from 'vue'
import { api, setAccessToken } from '../services/api'

export interface AdminUser {
  id: number
  name: string
  email: string
  phone: string | null
  role: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: AdminUser
}

interface UserResponse {
  user: AdminUser
}

const TOKEN_KEY = 'greenbite.admin.token'

const state = reactive({
  token: null as string | null,
  user: null as AdminUser | null,
})

const isAuthenticated = computed(() => state.token !== null)

function persistToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

function applySession(token: string, user: AdminUser): void {
  state.token = token
  state.user = user
  setAccessToken(token)
  persistToken(token)
}

async function login(email: string, password: string): Promise<AdminUser> {
  const data = await api.post<LoginResponse>('/auth/login', { email, password })
  applySession(data.access_token, data.user)
  return data.user
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

export function useAdminAuthStore() {
  return { state, isAuthenticated, login, logout, loadCurrentUser, restoreSession }
}