<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const CARDS = [
  { title: 'Products', text: 'Manage the product catalogue.', to: '/admin/products' },
  { title: 'Orders', text: 'Manage customer orders.', to: '/admin/orders' },
  { title: 'Users', text: 'Manage user accounts.', to: '/admin/users' },
]
</script>

<template>
  <section class="admin-dashboard">
    <h1 class="admin-dashboard__title">GreenBite Admin Dashboard</h1>
    <p class="admin-dashboard__subtitle">Welcome, Admin.</p>

    <div class="admin-dashboard__cards">
      <button
        v-for="card in CARDS"
        :key="card.to"
        class="admin-dashboard__card"
        @click="router.push(card.to)"
      >
        <h2 class="admin-dashboard__card-title">{{ card.title }}</h2>
        <p class="admin-dashboard__card-text">{{ card.text }}</p>
      </button>
    </div>
  </section>
</template>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.admin-dashboard__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.admin-dashboard__subtitle {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.admin-dashboard__cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-top: 16px;
}

@media (min-width: 600px) {
  .admin-dashboard__cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

.admin-dashboard__card {
  text-align: left;
  padding: 18px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.admin-dashboard__card-title {
  margin: 0 0 4px;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-deep-brown);
}

.admin-dashboard__card-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}
</style>