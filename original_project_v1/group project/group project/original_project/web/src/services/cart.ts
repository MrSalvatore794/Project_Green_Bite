import { api } from './api'

export interface CartItem {
  product_id: number
  product_name: string
  unit_price: number
  quantity: number
  subtotal: number
  image_url: string
  stock_quantity: number
}

export interface Cart {
  items: CartItem[]
  total: number
}

interface CartResponse {
  cart: Cart
}

export function fetchCart(): Promise<Cart> {
  return api.get<CartResponse>('/cart').then((data) => data.cart)
}

export function addCartItem(productId: number, quantity: number): Promise<Cart> {
  return api
    .post<CartResponse>('/cart/items', { product_id: productId, quantity })
    .then((data) => data.cart)
}

export function updateCartItem(productId: number, quantity: number): Promise<Cart> {
  return api
    .put<CartResponse>(`/cart/items/${productId}`, { quantity })
    .then((data) => data.cart)
}

export function removeCartItem(productId: number): Promise<Cart> {
  return api.delete<CartResponse>(`/cart/items/${productId}`).then((data) => data.cart)
}

export function clearCart(): Promise<Cart> {
  return api.delete<CartResponse>('/cart').then((data) => data.cart)
}
