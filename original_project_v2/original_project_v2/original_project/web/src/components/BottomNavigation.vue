<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import BaseIcon from './BaseIcon.vue'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

interface NavItem {
  name: string
  label: string
  to: string
  icon: string
  protected: boolean
}

const items: NavItem[] = [
  { name: 'home', label: 'Home', to: '/', icon: 'home', protected: false },
  { name: 'products', label: 'Products', to: '/products', icon: 'products', protected: false },
  { name: 'orders', label: 'Orders', to: '/orders', icon: 'orders', protected: true },
  { name: 'account', label: 'Account', to: '/account', icon: 'account', protected: false },
]

function isActive(to: string): boolean {
  if (to === '/') {
    return route.path === '/' || route.path === '/home'
  }
  if (to === '/products') {
    return route.path === '/products' || route.path.startsWith('/products/')
  }
  return route.path === to
}

function goTo(item: NavItem): void {
  if (item.protected && !auth.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: item.to } })
  } else {
    router.push(item.to)
  }
}
</script>

<template>
  <nav class="bottom-nav" aria-label="Primary navigation">
    <button
      v-for="item in items"
      :key="item.name"
      class="bottom-nav__item"
      :class="{ 'bottom-nav__item--active': isActive(item.to) }"
      @click="goTo(item)"
    >
      <BaseIcon :name="item.icon" :size="26" />
      <span class="bottom-nav__label">{{ item.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: sticky;
  bottom: 0;
  z-index: 10;
  display: flex;
  justify-content: space-around;
  padding: 8px 8px calc(8px + env(safe-area-inset-bottom));
  background: var(--color-cream);
  border-top: 1px solid var(--color-beige);
}

.bottom-nav__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  color: var(--color-bread-brown);
  font-family: var(--font-primary);
  font-size: 11px;
  font-weight: 600;
  opacity: 0.6;
}

.bottom-nav__item--active {
  color: var(--color-deep-brown);
  opacity: 1;
}
</style>
