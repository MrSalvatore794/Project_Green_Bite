import { api } from './api'

export interface Product {
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

export interface ProductDetail extends Product {
  like_count: number
  liked_by_current_user: boolean
}

interface ProductsResponse {
  products: Product[]
}

interface ProductDetailResponse {
  product: ProductDetail
}

export interface LikeResponse {
  liked: boolean
  like_count: number
}

export function fetchProducts(): Promise<Product[]> {
  return api.get<ProductsResponse>('/products').then((data) => data.products)
}

export function fetchProduct(id: number): Promise<ProductDetail> {
  return api.get<ProductDetailResponse>(`/products/${id}`).then((data) => data.product)
}

export function likeProduct(id: number): Promise<LikeResponse> {
  return api.post<LikeResponse>(`/products/${id}/like`)
}

export function unlikeProduct(id: number): Promise<LikeResponse> {
  return api.delete<LikeResponse>(`/products/${id}/like`)
}
