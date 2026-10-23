<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import QuantitySelector from '../components/QuantitySelector.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { useAuthStore } from '../stores/auth'
import { clearCart, fetchCart, removeCartItem, updateCartItem } from '../services/cart'
import type { Cart, CartItem } from '../services/cart'
import { errorMessage } from '../utils/errors'

const router = useRouter()
const auth = useAuthStore()

const cart = ref<Cart | null>(null)
const loading = ref(true)
const error = ref('')
const mutationError = ref('')
const updatingId = ref<number | null>(null)
const removingId = ref<number | null>(null)
const clearing = ref(false)

const isEmpty = computed(() => cart.value !== null && cart.value.items.length === 0)

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    cart.value = await fetchCart()
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

async function onQuantityChange(item: CartItem, next: number): Promise<void> {
  if (updatingId.value !== null || item.quantity === next) return
  updatingId.value = item.product_id
  mutationError.value = ''
  try {
    cart.value = await updateCartItem(item.product_id, next)
  } catch (err) {
    mutationError.value = errorMessage(err)
  } finally {
    updatingId.value = null
  }
}

async function onRemove(item: CartItem): Promise<void> {
  if (removingId.value !== null) return
  removingId.value = item.product_id
  mutationError.value = ''
  try {
    cart.value = await removeCartItem(item.product_id)
  } catch (err) {
    mutationError.value = errorMessage(err)
  } finally {
    removingId.value = null
  }
}

async function onClear(): Promise<void> {
  if (!window.confirm('Clear all items from your cart?')) return
  clearing.value = true
  mutationError.value = ''
  try {
    cart.value = await clearCart()
  } catch (err) {
    mutationError.value = errorMessage(err)
  } finally {
    clearing.value = false
  }
}

function goCheckout(): void {
  router.push('/checkout')
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace({ path: '/login', query: { redirect: '/cart' } })
    return
  }
  void load()
})
</script>

<template>
  <section class="cart">
    <SectionTitle title="Your Cart" />

    <LoadingState v-if="loading" />

    <div v-else-if="error" class="cart__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <template v-else-if="cart">
      <div v-if="isEmpty" class="cart__empty">
        <p class="cart__empty-text">Your cart is empty.</p>
        <PrimaryButton @click="router.push('/products')">Browse Products</PrimaryButton>
      </div>

      <template v-else>
        <ErrorMessage v-if="mutationError" :message="mutationError" />

        <ul class="cart__list">
          <li v-for="item in cart.items" :key="item.product_id" class="cart__item">
            <img class="cart__item-image" :src="item.image_url" :alt="item.product_name" />
            <div class="cart__item-body">
              <h3 class="cart__item-name">{{ item.product_name }}</h3>
              <span class="cart__item-price">${{ item.unit_price.toFixed(2) }}</span>
              <div class="cart__item-actions">
                <QuantitySelector
                  :model-value="item.quantity"
                  :min="1"
                  :max="item.stock_quantity"
                  :disabled="updatingId === item.product_id"
                  @update:model-value="onQuantityChange(item, $event)"
                />
                <button
                  class="cart__remove"
                  :disabled="removingId === item.product_id"
                  @click="onRemove(item)"
                >
                  Remove
                </button>
              </div>
            </div>
          </li>
        </ul>

        <div class="cart__summary">
          <div class="cart__subtotal-row">
            <span class="cart__subtotal-label">Subtotal</span>
            <span class="cart__subtotal">${{ cart.total.toFixed(2) }}</span>
          </div>
          <PrimaryButton @click="goCheckout">Checkout</PrimaryButton>
          <button class="cart__clear" :disabled="clearing" @click="onClear">Clear cart</button>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.cart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cart__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cart__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px 0;
  text-align: center;
}

.cart__empty-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 15px;
  color: var(--color-bread-brown);
}

.cart__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cart__item {
  display: flex;
  gap: 14px;
  padding: 12px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.cart__item-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  object-fit: cover;
  background: var(--color-beige);
}

.cart__item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cart__item-name {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.cart__item-price {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-green);
}

.cart__item-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 4px;
}

.cart__remove {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-orange);
  padding: 6px 10px;
}

.cart__remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cart__summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.cart__subtotal-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.cart__subtotal-label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.cart__subtotal {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 18px;
  color: var(--color-green);
}

.cart__clear {
  align-self: center;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-bread-brown);
  text-decoration: underline;
  padding: 6px 10px;
}

.cart__clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
