<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAdminAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAdminAuthStore()

const NAV = [
  { label: 'Dashboard', to: '/admin' },
  { label: 'Products', to: '/admin/products' },
  { label: 'Orders', to: '/admin/orders' },
  { label: 'Users', to: '/admin/users' },
]

function isActive(to: string): boolean {
  if (to === '/admin') return route.path === '/admin'
  return route.path === to || route.path.startsWith(to + '/')
}

function logout(): void {
  auth.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-shell">
    <header class="admin-shell__header">
      <div class="admin-shell__brand">
        <img class="admin-shell__logo" src="/assets/brand/logo2.png" alt="GreenBite Admin" />
        <span class="admin-shell__badge">Admin</span>
      </div>
      <div class="admin-shell__actions">
        <span v-if="auth.state.user" class="admin-shell__user">{{ auth.state.user.name }}</span>
        <button class="admin-shell__logout" @click="logout">Logout</button>
      </div>
    </header>

    <nav class="admin-shell__nav" aria-label="Admin navigation">
      <router-link
        v-for="item in NAV"
        :key="item.to"
        :to="item.to"
        class="admin-shell__link"
        :class="{ 'admin-shell__link--active': isActive(item.to) }"
      >
        {{ item.label }}
      </router-link>
    </nav>

    <main class="admin-shell__main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-shell {
  max-width: 760px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-cream);
}

.admin-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid var(--color-beige);
}

.admin-shell__brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-shell__logo {
  height: 34px;
  width: auto;
}

.admin-shell__badge {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 11px;
}

.admin-shell__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-shell__user {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-deep-brown);
}

.admin-shell__logout {
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.admin-shell__nav {
  display: flex;
  gap: 4px;
  padding: 10px 16px;
  background: var(--color-green-dark);
  overflow-x: auto;
}

.admin-shell__link {
  flex-shrink: 0;
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: #fff;
}

.admin-shell__link--active {
  background: #fff;
  color: var(--color-green-dark);
}

.admin-shell__main {
  flex: 1;
  padding: 16px;
}
</style>