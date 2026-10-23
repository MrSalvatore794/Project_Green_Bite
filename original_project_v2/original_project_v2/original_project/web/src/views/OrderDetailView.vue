<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import { cancelOrder, fetchOrder } from '../services/orders'
import type { Order } from '../services/orders'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../utils/errors'

const props = defineProps<{ id: string }>()
const router = useRouter()
const auth = useAuthStore()

const order = ref<Order | null>(null)
const loading = ref(true)
const error = ref('')
const canceling = ref(false)
const cancelError = ref('')

const statusLabel = computed(() => {
  if (order.value?.canceled_at) return 'Canceled'
  const s = order.value?.status ?? ''
  return s
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
})

const paymentLabel = computed(() => {
  const labels: Record<string, string> = {
    pending: 'Pending',
    completed: 'Completed',
    failed: 'Failed',
  }
  const s = order.value?.payment_status ?? ''
  return labels[s] ?? s
})

const canCancel = computed(() => {
  const o = order.value
  return o !== null && o.status === 'pending' && !o.canceled_at
})

function confirmCancel(): void {
  if (!order.value || canceling.value) return
  const paid = order.value.payment_status === 'completed'
  const message = paid
    ? 'Cancel this order? Your payment has been recorded as completed. The merchant must verify and process the refund separately. This action does not mean the refund has been completed.'
    : 'Cancel this order? The order will be canceled and the reserved stock will be returned.'
  if (!window.confirm(message)) return
  void submitCancel()
}

async function submitCancel(): Promise<void> {
  if (!order.value || canceling.value) return
  canceling.value = true
  cancelError.value = ''
  try {
    order.value = await cancelOrder(order.value.id)
  } catch (err) {
    cancelError.value = errorMessage(err)
  } finally {
    canceling.value = false
  }
}

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    order.value = await fetchOrder(Number(props.id))
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace({ path: '/login', query: { redirect: `/orders/${props.id}` } })
    return
  }
  void load()
})
</script>

<template>
  <section class="order-detail">
    <LoadingState v-if="loading" />

    <div v-else-if="error" class="order-detail__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <template v-else-if="order">
      <router-link to="/orders" class="order-detail__back">← Back to My Orders</router-link>

      <div class="order-detail__header">
        <h1 class="order-detail__title">Order #{{ order.id }}</h1>
        <span class="order-detail__status">{{ statusLabel }}</span>
      </div>

      <div class="order-detail__card">
        <h2 class="order-detail__card-title">Items</h2>
        <ul class="order-detail__list">
          <li v-for="item in order.items" :key="item.product_id" class="order-detail__item">
            <div class="order-detail__item-body">
              <span class="order-detail__item-name">{{ item.product_name }}</span>
              <span class="order-detail__item-meta">
                ${{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
              </span>
            </div>
            <span class="order-detail__item-price">${{ item.subtotal.toFixed(2) }}</span>
          </li>
        </ul>
        <div class="order-detail__total-row">
          <span class="order-detail__total-label">Total</span>
          <span class="order-detail__total">${{ order.total_amount.toFixed(2) }}</span>
        </div>
      </div>

      <div class="order-detail__card">
        <h2 class="order-detail__card-title">Pickup</h2>
        <p class="order-detail__text">Pickup only.</p>
        <p class="order-detail__text">{{ order.pickup_date }} · {{ order.pickup_time }}</p>
      </div>

      <div class="order-detail__card">
        <h2 class="order-detail__card-title">Payment</h2>
        <p class="order-detail__text">Bank transfer · {{ paymentLabel }}</p>
        <p class="order-detail__text">Reference: {{ order.payment_reference }}</p>
      </div>

      <ErrorMessage v-if="cancelError" :message="cancelError" />

      <div v-if="order.canceled_at" class="order-detail__canceled">
        <p class="order-detail__canceled-text">
          {{
            order.payment_status === 'completed'
              ? 'Order canceled. Your refund is pending merchant verification. No refund has been confirmed as completed.'
              : 'Order canceled. The reserved stock has been returned.'
          }}
        </p>
      </div>

      <button
        v-if="canCancel"
        class="order-detail__cancel"
        :disabled="canceling"
        @click="confirmCancel"
      >
        {{ canceling ? 'Canceling…' : 'Cancel Order' }}
      </button>

      <PrimaryButton @click="router.push('/products')">Continue Shopping</PrimaryButton>
    </template>
  </section>
</template>

<style scoped>
.order-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-detail__back {
  align-self: flex-start;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-detail__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.order-detail__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.order-detail__status {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  background: var(--color-yellow);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 12px;
}

.order-detail__card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.order-detail__card-title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.order-detail__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-detail__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.order-detail__item-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-detail__item-name {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__item-meta {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.order-detail__item-price {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__total-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--color-beige);
}

.order-detail__total-label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.order-detail__total {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 18px;
  color: var(--color-green);
}

.order-detail__text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.order-detail__cancel {
  align-self: center;
  padding: 8px 12px;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-orange);
  text-decoration: underline;
}

.order-detail__cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.order-detail__canceled {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
}

.order-detail__canceled-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-deep-brown);
}
</style>
