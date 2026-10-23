<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import BrandLogo from './BrandLogo.vue'
import BaseIcon from './BaseIcon.vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()

const authenticated = computed(() => auth.isAuthenticated.value)
const cartCount = computed(() => cart.state.totalQuantity)
const showBadge = computed(() => authenticated.value && cartCount.value > 0)

watch(
  authenticated,
  (isAuthed) => {
    if (isAuthed) {
      void cart.load().catch(() => {})
    } else {
      cart.reset()
    }
  },
  { immediate: true },
)

function goToAccount(): void {
  router.push(auth.isAuthenticated ? '/account' : '/login')
}

function goToCart(): void {
  if (auth.isAuthenticated) {
    router.push('/cart')
  } else {
    router.push({ path: '/login', query: { redirect: '/cart' } })
  }
}
</script>

<template>
  <header class="app-header">
    <BrandLogo />
    <nav class="app-header__actions" aria-label="Account actions">
      <button class="app-header__icon" aria-label="Account" @click="goToAccount">
        <BaseIcon name="account" :size="26" />
      </button>
      <button class="app-header__icon app-header__icon--cart" aria-label="Cart" @click="goToCart">
        <BaseIcon name="cart" :size="26" />
        <span v-if="showBadge" class="app-header__badge" aria-hidden="true">
          {{ cartCount > 99 ? '99+' : cartCount }}
        </span>
      </button>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-cream);
  border-bottom: 1px solid var(--color-beige);
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.app-header__icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: var(--color-deep-brown);
}

.app-header__icon:hover {
  background: var(--color-beige);
}

.app-header__icon--cart {
  position: relative;
}

.app-header__badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: var(--color-orange);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 11px;
  line-height: 1;
}
</style>
