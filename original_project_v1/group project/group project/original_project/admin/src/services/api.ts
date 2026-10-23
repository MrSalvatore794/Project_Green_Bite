export interface ApiErrorBody {
  error?: {
    code?: string
    message?: string
  }
}

export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

// The Admin app talks to the Flask API directly (cross-origin). The base URL
// is configured through VITE_API_BASE_URL; the development default is in
// .env.development.
const API_BASE: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5006/api/v1'

let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Unable to connect to GreenBite.')
  }

  const data = (await response.json().catch(() => null)) as (T & ApiErrorBody) | null

  if (!response.ok) {
    const code = data?.error?.code ?? 'UNKNOWN'
    const message = data?.error?.message ?? `Request failed (${response.status}).`
    throw new ApiError(response.status, code, message)
  }

  return data as T
}

async function uploadRequest<T>(path: string, formData: FormData): Promise<T> {
  const headers: Record<string, string> = {}
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  let response: Response
  try {
    // No Content-Type header: the browser sets the multipart boundary.
    response = await fetch(`${API_BASE}${path}`, { method: 'POST', body: formData, headers })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Unable to connect to GreenBite.')
  }

  const data = (await response.json().catch(() => null)) as (T & ApiErrorBody) | null

  if (!response.ok) {
    const code = data?.error?.code ?? 'UNKNOWN'
    const message = data?.error?.message ?? `Request failed (${response.status}).`
    throw new ApiError(response.status, code, message)
  }

  return data as T
}

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>(path, { method: 'GET' })
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: 'POST',
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  },
  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: 'PUT',
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  },
  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: 'PATCH',
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  },
  delete<T>(path: string): Promise<T> {
    return request<T>(path, { method: 'DELETE' })
  },
  upload<T>(path: string, formData: FormData): Promise<T> {
    return uploadRequest<T>(path, formData)
  },
}