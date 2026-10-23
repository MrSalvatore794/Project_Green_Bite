import { api } from './api'

export interface AdminProduct {
  id: number
  name: string
  description: string
  price: number
  category: string
  vegetarian: boolean
  vegan: boolean
  ingredients: string
  allergens: string
  stock_quantity: number
  is_active: boolean
  image_url: string
  detail_image_url: string
  star_level: number
}

interface ProductsResponse {
  products: AdminProduct[]
}

interface ProductResponse {
  product: AdminProduct
}

export interface CreateProductPayload {
  name: string
  description?: string
  price: number
  stock_quantity?: number
  category?: string
  vegetarian?: boolean
  vegan?: boolean
  ingredients?: string
  allergens?: string
  star_level?: number
}

export interface UpdateProductPayload {
  name?: string
  description?: string
  price?: number
  category?: string
  vegetarian?: boolean
  vegan?: boolean
  ingredients?: string
  allergens?: string
  star_level?: number
}

export function fetchProducts(): Promise<AdminProduct[]> {
  return api.get<ProductsResponse>('/admin/products').then((data) => data.products)
}

export function createProduct(payload: CreateProductPayload): Promise<AdminProduct> {
  return api
    .post<ProductResponse>('/admin/products', payload)
    .then((data) => data.product)
}

export function updateProduct(id: number, payload: UpdateProductPayload): Promise<AdminProduct> {
  return api
    .put<ProductResponse>(`/admin/products/${id}`, payload)
    .then((data) => data.product)
}

export function setProductStatus(id: number, isActive: boolean): Promise<AdminProduct> {
  return api
    .patch<ProductResponse>(`/admin/products/${id}/status`, { is_active: isActive })
    .then((data) => data.product)
}

export function updateProductStock(id: number, stock: number): Promise<AdminProduct> {
  return api
    .patch<ProductResponse>(`/admin/products/${id}/stock`, { stock_quantity: stock })
    .then((data) => data.product)
}

export function uploadProductImage(
  id: number,
  file: File,
  kind: 'main' | 'detail',
): Promise<AdminProduct> {
  const formData = new FormData()
  formData.append('image', file)
  const path = kind === 'detail' ? `/admin/products/${id}/detail-image` : `/admin/products/${id}/image`
  return api.upload<ProductResponse>(path, formData).then((data) => data.product)
}

// Resolve a logical media path (e.g. /uploads/products/x.jpg) to a full URL.
// Production can override the media base with VITE_MEDIA_BASE_URL.
export function mediaUrl(path: string): string {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  const mediaBase = import.meta.env.VITE_MEDIA_BASE_URL as string | undefined
  if (mediaBase) return `${mediaBase}${path}`
  const apiBase =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
    'http://127.0.0.1:5006/api/v1'
  const origin = apiBase.replace(/\/api\/v1\/?$/, '')
  return `${origin}${path}`
}