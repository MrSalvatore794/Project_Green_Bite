<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import QuantitySelector from '../components/QuantitySelector.vue'
import BaseIcon from '../components/BaseIcon.vue'
import { fetchProduct, likeProduct, unlikeProduct } from '../services/products'
import type { ProductDetail } from '../services/products'
import { addCartItem } from '../services/cart'
import { ApiError } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../utils/errors'

const props = defineProps<{ id: string }>()
const router = useRouter()
const auth = useAuthStore()

const product = ref<ProductDetail | null>(null)
const loading = ref(true)
const error = ref('')
const notFound = ref(false)
const quantity = ref(1)
const adding = ref(false)
const added = ref(false)
const addError = ref('')
const showGuestPrompt = ref(false)
const likeSubmitting = ref(false)
const likeError = ref('')
const showLikePrompt = ref(false)

let addedTimer: number | undefined

const available = computed(
  () => product.value !== null && product.value.is_active && product.value.stock_quantity > 0,
)

const maxQuantity = computed(() => {
  const p = product.value
  if (!p || !p.is_active || p.stock_quantity <= 0) return 1
  return p.stock_quantity
})

async function toggleLike(): Promise<void> {
  if (!product.value || likeSubmitting.value) return
  likeError.value = ''

  if (!auth.isAuthenticated) {
    showLikePrompt.value = true
    return
  }

  likeSubmitting.value = true
  try {
    const result = product.value.liked_by_current_user
      ? await unlikeProduct(product.value.id)
      : await likeProduct(product.value.id)
    product.value.like_count = result.like_count
    product.value.liked_by_current_user = result.liked
  } catch (err) {
    likeError.value = errorMessage(err)
  } finally {
    likeSubmitting.value = false
  }
}

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  notFound.value = false
  try {
    product.value = await fetchProduct(Number(props.id))
    quantity.value = 1
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound.value = true
    } else {
      error.value = errorMessage(err)
    }
  } finally {
    loading.value = false
  }
}

function addToCart(): void {
  if (!product.value) return
  addError.value = ''
  added.value = false

  if (!auth.isAuthenticated) {
    showGuestPrompt.value = true
    return
  }

  void submitAddToCart()
}

async function submitAddToCart(): Promise<void> {
  if (!product.value || adding.value) return
  adding.value = true
  try {
    await addCartItem(product.value.id, quantity.value)
    added.value = true
    if (addedTimer !== undefined) window.clearTimeout(addedTimer)
    addedTimer = window.setTimeout(() => {
      added.value = false
      addedTimer = undefined
    }, 3000)
  } catch (err) {
    addError.value = errorMessage(err)
  } finally {
    adding.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="detail">
    <div class="detail__actions">
      <router-link to="/products" class="detail__action" aria-label="Back to products">
        <BaseIcon name="back" :size="22" />
      </router-link>
      <button
        class="detail__action detail__action--like"
        :class="{ 'detail__action--active': product?.liked_by_current_user }"
        :aria-pressed="product?.liked_by_current_user ?? false"
        :disabled="likeSubmitting"
        aria-label="Toggle like"
        @click="toggleLike"
      >
        <BaseIcon name="favorites" :size="20" />
        <span v-if="product" class="detail__like-count">{{ product.like_count }}</span>
      </button>
    </div>

    <LoadingState v-if="loading" />

    <div v-else-if="notFound" class="detail__notfound">
      <ErrorMessage message="Product not found." />
      <PrimaryButton @click="router.push('/products')">Back to Products</PrimaryButton>
    </div>

    <div v-else-if="error" class="detail__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <div v-else-if="product" class="detail__content">
      <img class="detail__image" :src="product.image_url" :alt="product.name" />

      <div v-if="showLikePrompt && !auth.isAuthenticated" class="detail__guest">
        <p class="detail__guest-text">Please log in to like this product.</p>
        <div class="detail__guest-actions">
          <router-link :to="{ path: '/login', query: { redirect: `/products/${props.id}` } }" class="detail__guest-btn">Log in</router-link>
          <router-link :to="{ path: '/register', query: { redirect: `/products/${props.id}` } }" class="detail__guest-btn">Register</router-link>
        </div>
      </div>
      <ErrorMessage v-if="likeError" :message="likeError" />

      <div class="detail__header">
        <h1 class="detail__name">{{ product.name }}</h1>
        <span class="detail__price">${{ product.price.toFixed(2) }}</span>
      </div>

      <p v-if="product.vegan || product.vegetarian" class="detail__meta">
        {{ product.vegan ? 'Vegan' : 'Vegetarian' }}
      </p>
      <p v-if="product.category" class="detail__meta">{{ product.category }}</p>

      <div v-if="product.description" class="detail__section">
        <h2 class="detail__section-title">Description</h2>
        <p class="detail__text">{{ product.description }}</p>
      </div>

      <div class="detail__buy">
        <QuantitySelector v-model="quantity" :min="1" :max="maxQuantity" />
        <PrimaryButton :disabled="!available || adding" @click="addToCart">
          {{ adding ? 'Adding…' : 'Add to Cart' }}
        </PrimaryButton>
      </div>

      <div v-if="showGuestPrompt && !auth.isAuthenticated" class="detail__guest">
        <p class="detail__guest-text">
          Only registered or logged-in customers can add items to the cart.
        </p>
        <div class="detail__guest-actions">
          <router-link :to="{ path: '/login', query: { redirect: `/products/${props.id}` } }" class="detail__guest-btn">
            Log in
          </router-link>
          <router-link :to="{ path: '/register', query: { redirect: `/products/${props.id}` } }" class="detail__guest-btn">
            Register
          </router-link>
        </div>
      </div>

      <p class="detail__availability" :class="{ 'detail__availability--out': !available }">
        {{ available ? `${product.stock_quantity} in stock` : 'Out of stock' }}
      </p>

      <p v-if="added" class="detail__success">
        Added to cart ✓
        <router-link to="/cart" class="detail__view-cart">View Cart</router-link>
      </p>
      <ErrorMessage v-if="addError" :message="addError" />

      <div v-if="product.ingredients" class="detail__section">
        <h2 class="detail__section-title">Ingredients</h2>
        <p class="detail__text">{{ product.ingredients }}</p>
      </div>

      <div v-if="product.allergens" class="detail__section">
        <h2 class="detail__section-title">Allergen Information</h2>
        <p class="detail__text">{{ product.allergens }}</p>
      </div>

      <img
        v-if="product.detail_image_url"
        class="detail__detail-image"
        :src="product.detail_image_url"
        :alt="`${product.name} detail`"
      />
    </div>
  </section>
</template>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Sticky Back/Favourite actions that stay accessible while the detail scrolls.
   They sit just below the global AppHeader and overlap the product image. */
.detail__actions {
  position: sticky;
  top: var(--app-header-height);
  z-index: 5;
  display: flex;
  justify-content: space-between;
  padding: 12px;
}

.detail__action {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-soft);
  color: var(--color-deep-brown);
}

.detail__action--active {
  color: var(--color-orange);
}

.detail__action--like {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: auto;
  padding: 0 14px;
  border-radius: var(--radius-pill);
}

.detail__action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.detail__like-count {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.detail__action--active .detail__like-count {
  color: var(--color-orange);
}

.detail__notfound,
.detail__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Pull the loaded content up under the actions bar so Back/Favourite overlay
   the product image. 12px padding + 42px button + 12px padding = 66px bar,
   plus the 16px flex gap = 82px. */
.detail__content {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: -82px;
}

.detail__image {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  background: var(--color-beige);
  box-shadow: var(--shadow-card);
}

.detail__detail-image {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  background: var(--color-beige);
  box-shadow: var(--shadow-card);
}

.detail__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.detail__name {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.detail__price {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 20px;
  color: var(--color-green);
}

.detail__meta {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.detail__availability {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-green);
}

.detail__availability--out {
  color: var(--color-orange);
}

.detail__buy {
  display: flex;
  align-items: center;
  gap: 14px;
}

.detail__buy :deep(.primary-button) {
  flex: 1;
}

.detail__guest {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(232, 185, 93, 0.15);
}

.detail__guest-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.detail__guest-actions {
  display: flex;
  gap: 10px;
}

.detail__guest-btn {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
}

.detail__success {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-green);
}

.detail__view-cart {
  margin-left: 8px;
  font-weight: 700;
  text-decoration: underline;
}

.detail__section {
  padding-top: 4px;
  border-top: 1px solid var(--color-beige);
}

.detail__section-title {
  margin: 0 0 6px;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.detail__text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-bread-brown);
}
</style>

