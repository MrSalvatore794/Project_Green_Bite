<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { fetchOrders } from '../services/orders'
import type { OrderSummary } from '../services/orders'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../utils/errors'

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  confirmed: 'Confirmed',
  preparing: 'Preparing',
  ready_for_pickup: 'Ready for pickup',
  collected: 'Collected',
}

const PAYMENT_LABELS: Record<string, string> = {
  pending: 'Pending',
  completed: 'Completed',
  failed: 'Failed',
}

const router = useRouter()
const auth = useAuthStore()

const orders = ref<OrderSummary[]>([])
const loading = ref(true)
const error = ref('')

const isEmpty = computed(() => orders.value.length === 0)

function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status
}

function paymentLabel(status: string): string {
  return PAYMENT_LABELS[status] ?? status
}

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    orders.value = await fetchOrders()
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace({ path: '/login', query: { redirect: '/orders' } })
    return
  }
  void load()
})
</script>

<template>
  <section class="orders">
    <SectionTitle title="My Orders" />

    <LoadingState v-if="loading" />

    <div v-else-if="error" class="orders__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <div v-else-if="isEmpty" class="orders__empty">
      <p class="orders__empty-text">You have no orders yet.</p>
      <PrimaryButton @click="router.push('/products')">Browse Products</PrimaryButton>
    </div>

    <ul v-else class="orders__list">
      <li v-for="order in orders" :key="order.id" class="orders__card">
        <div class="orders__header">
          <span class="orders__number">Order #{{ order.id }}</span>
          <span class="orders__status">{{ statusLabel(order.status) }}</span>
        </div>

        <template v-if="order.items.length > 0">
          <div class="orders__item">
            <span class="orders__item-name">{{ order.items[0].product_name }}</span>
            <span class="orders__item-qty">× {{ order.items[0].quantity }}</span>
          </div>
          <p v-if="order.items.length > 1" class="orders__more">
            + {{ order.items.length - 1 }} more item{{ order.items.length > 2 ? 's' : '' }}
          </p>
        </template>

        <div class="orders__row">
          <span class="orders__label">Pickup</span>
          <span class="orders__value">{{ order.pickup_date }} · {{ order.pickup_time }}</span>
        </div>

        <div class="orders__row">
          <span class="orders__label">Payment</span>
          <span class="orders__value">{{ paymentLabel(order.payment_status) }}</span>
        </div>

        <div class="orders__row">
          <span class="orders__label">Total</span>
          <span class="orders__total">${{ order.total_amount.toFixed(2) }}</span>
        </div>

        <router-link :to="`/orders/${order.id}`" class="orders__view">View Order →</router-link>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.orders {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.orders__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.orders__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px 0;
  text-align: center;
}

.orders__empty-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 15px;
  color: var(--color-bread-brown);
}

.orders__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.orders__card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.orders__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.orders__number {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-deep-brown);
}

.orders__status {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  background: var(--color-yellow);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 12px;
}

.orders__item {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.orders__item-name {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.orders__item-qty {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.orders__more {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.orders__row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--color-beige);
}

.orders__label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-bread-brown);
}

.orders__value {
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.orders__total {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-green);
}

.orders__view {
  align-self: flex-end;
  margin-top: 4px;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-orange);
}
</style>
