import { api } from './api'

export interface AdminUser {
  id: number
  name: string
  email: string
  phone: string | null
  role: string
  created_at: string | null
}

export interface AdminUserOrder {
  id: number
  total_amount: number
  pickup_date: string
  pickup_time: string
  status: string
  payment_status: string
  created_at: string
}

interface UsersResponse {
  users: AdminUser[]
}

export interface UserDetailResponse {
  user: AdminUser
  orders: AdminUserOrder[]
}

export function fetchUsers(): Promise<AdminUser[]> {
  return api.get<UsersResponse>('/admin/users').then((data) => data.users)
}

export function fetchUser(id: number): Promise<UserDetailResponse> {
  return api.get<UserDetailResponse>(`/admin/users/${id}`)
}