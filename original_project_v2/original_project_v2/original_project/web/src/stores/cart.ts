import { reactive } from 'vue'
import {
  addCartItem,
  clearCart,
  fetchCart,
  removeCartItem,
  updateCartItem,
} from '../services/cart'
import type { Cart } from '../services/cart'

const state = reactive({
  totalQuantity: 0,
})

function sumQuantity(cart: Cart): number {
  return cart.items.reduce((sum, item) => sum + item.quantity, 0)
}

function applyCart(cart: Cart): void {
  state.totalQuantity = sumQuantity(cart)
}

async function load(): Promise<void> {
  applyCart(await fetchCart())
}

function reset(): void {
  state.totalQuantity = 0
}

async function add(productId: number, quantity: number): Promise<Cart> {
  const cart = await addCartItem(productId, quantity)
  applyCart(cart)
  return cart
}

async function update(productId: number, quantity: number): Promise<Cart> {
  const cart = await updateCartItem(productId, quantity)
  applyCart(cart)
  return cart
}

async function remove(productId: number): Promise<Cart> {
  const cart = await removeCartItem(productId)
  applyCart(cart)
  return cart
}

async function clear(): Promise<Cart> {
  const cart = await clearCart()
  applyCart(cart)
  return cart
}

export function useCartStore() {
  return { state, applyCart, load, reset, add, update, remove, clear }
}
