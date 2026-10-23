<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  fetchOrder,
  fetchOrders,
  updateOrderStatus,
  updatePaymentStatus,
} from '../services/orders'
import type { AdminOrder, AdminOrderSummary } from '../services/orders'
import { errorMessage } from '../services/errors'

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

const NEXT_STATUS: Record<string, { label: string; next: string } | undefined> = {
  pending: { label: 'Confirm Order', next: 'confirmed' },
  confirmed: { label: 'Start Preparing', next: 'preparing' },
  preparing: { label: 'Mark Ready for Pickup', next: 'ready_for_pickup' },
  ready_for_pickup: { label: 'Mark Collected', next: 'collected' },
  collected: undefined,
}

const orders = ref<AdminOrderSummary[]>([])
const loading = ref(true)
const error = ref('')

const search = ref('')
const paymentFilter = ref('all')
const statusFilter = ref('all')

const showDetail = ref(false)
const selectedOrder = ref<AdminOrder | null>(null)
const loadingDetail = ref(false)
const actionError = ref('')

const filteredOrders = computed(() => {
  let result = [...orders.value]
  const q = search.value.trim().toLowerCase()
  if (q) {
    result = result.filter((o) => {
      return (
        String(o.id).includes(q) ||
        o.customer_name.toLowerCase().includes(q) ||
        o.phone.toLowerCase().includes(q) ||
        o.payment_reference.toLowerCase().includes(q)
      )
    })
  }
  if (paymentFilter.value !== 'all') {
    result = result.filter((o) => o.payment_status === paymentFilter.value)
  }
  if (statusFilter.value === 'canceled') {
    result = result.filter((o) => !!o.canceled_at)
  } else if (statusFilter.value !== 'all') {
    result = result.filter((o) => o.status === statusFilter.value && !o.canceled_at)
  }
  return result
})

function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status
}

function paymentLabel(status: string): string {
  return PAYMENT_LABELS[status] ?? status
}

function paymentActions(status: string): string[] {
  if (status === 'pending') return ['completed', 'failed']
  if (status === 'failed') return ['completed']
  return []
}

function paymentActionLabel(status: string): string {
  return status === 'completed' ? 'Mark Payment Completed' : 'Mark Payment Failed'
}

function isCanceled(order: { canceled_at?: string | null }): boolean {
  return !!order.canceled_at
}

function displayStatus(order: { status: string; canceled_at?: string | null }): string {
  return isCanceled(order) ? 'Canceled' : statusLabel(order.status)
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

async function openDetail(order: AdminOrderSummary): Promise<void> {
  showDetail.value = true
  loadingDetail.value = true
  actionError.value = ''
  selectedOrder.value = null
  try {
    selectedOrder.value = await fetchOrder(order.id)
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    loadingDetail.value = false
  }
}

function closeDetail(): void {
  showDetail.value = false
  selectedOrder.value = null
}

async function markPayment(status: string): Promise<void> {
  if (!selectedOrder.value) return
  actionError.value = ''
  try {
    selectedOrder.value = await updatePaymentStatus(selectedOrder.value.id, status)
    await load()
  } catch (err) {
    actionError.value = errorMessage(err)
  }
}

async function advanceStatus(next: string): Promise<void> {
  if (!selectedOrder.value) return
  actionError.value = ''
  try {
    selectedOrder.value = await updateOrderStatus(selectedOrder.value.id, next)
    await load()
  } catch (err) {
    actionError.value = errorMessage(err)
  }
}

onMounted(load)
</script>

<template>
  <section class="orders-admin">
    <h1 class="orders-admin__title">Order Management</h1>

    <div class="orders-admin__controls">
      <input
        v-model="search"
        class="orders-admin__search"
        type="search"
        placeholder="Search ID, name, phone, reference…"
      />
      <select v-model="paymentFilter" class="orders-admin__select">
        <option value="all">Payment: All</option>
        <option value="pending">Payment: Pending</option>
        <option value="completed">Payment: Completed</option>
        <option value="failed">Payment: Failed</option>
      </select>
      <select v-model="statusFilter" class="orders-admin__select">
        <option value="all">Status: All</option>
        <option value="pending">Status: Pending</option>
        <option value="confirmed">Status: Confirmed</option>
        <option value="preparing">Status: Preparing</option>
        <option value="ready_for_pickup">Status: Ready for pickup</option>
        <option value="collected">Status: Collected</option>
        <option value="canceled">Status: Canceled</option>
      </select>
    </div>

    <p v-if="error" class="orders-admin__error" role="alert">{{ error }}</p>
    <p v-if="loading" class="orders-admin__hint">Loading orders…</p>
    <p v-else-if="filteredOrders.length === 0" class="orders-admin__hint">No orders found.</p>

    <ul v-else class="orders-admin__list">
      <li v-for="order in filteredOrders" :key="order.id" class="order-row">
        <div class="order-row__header">
          <span class="order-row__id">Order #{{ order.id }}</span>
          <span class="order-row__badge order-row__badge--payment">
            {{ paymentLabel(order.payment_status) }}
          </span>
          <span class="order-row__badge order-row__badge--status">
            {{ displayStatus(order) }}
          </span>
        </div>
        <div class="order-row__meta">
          <span>{{ order.customer_name }}</span>
          <span>{{ order.phone }}</span>
        </div>
        <div class="order-row__footer">
          <span class="order-row__total">${{ order.total_amount.toFixed(2) }}</span>
          <button class="order-row__view" @click="openDetail(order)">View</button>
        </div>
      </li>
    </ul>

    <div v-if="showDetail" class="order-detail__overlay" @click.self="closeDetail">
      <div class="order-detail">
        <div class="order-detail__header">
          <h2 class="order-detail__title">Order #{{ selectedOrder?.id ?? '…' }}</h2>
          <button class="order-detail__close" @click="closeDetail">Close</button>
        </div>

        <p v-if="loadingDetail" class="order-detail__hint">Loading…</p>
        <p v-if="actionError" class="order-detail__error" role="alert">{{ actionError }}</p>

        <template v-if="selectedOrder">
          <div class="order-detail__section">
            <h3 class="order-detail__section-title">Customer</h3>
            <p class="order-detail__text">{{ selectedOrder.customer_name }}</p>
            <p class="order-detail__text">{{ selectedOrder.phone }}</p>
          </div>

          <div class="order-detail__section">
            <h3 class="order-detail__section-title">Pickup</h3>
            <p class="order-detail__text">
              {{ selectedOrder.pickup_date }} · {{ selectedOrder.pickup_time }}
            </p>
          </div>

          <div class="order-detail__section">
            <h3 class="order-detail__section-title">Items</h3>
            <ul class="order-detail__items">
              <li
                v-for="item in selectedOrder.items"
                :key="item.product_id"
                class="order-detail__item"
              >
                <span class="order-detail__item-name">{{ item.product_name }}</span>
                <span class="order-detail__item-qty">
                  ${{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
                </span>
                <span class="order-detail__item-subtotal">
                  ${{ item.subtotal.toFixed(2) }}
                </span>
              </li>
            </ul>
            <div class="order-detail__total-row">
              <span>Total</span>
              <span class="order-detail__total">${{ selectedOrder.total_amount.toFixed(2) }}</span>
            </div>
          </div>

          <div class="order-detail__section">
            <h3 class="order-detail__section-title">Payment</h3>
            <p class="order-detail__text">
              Status: {{ paymentLabel(selectedOrder.payment_status) }}
            </p>
            <p class="order-detail__text">Reference: {{ selectedOrder.payment_reference }}</p>
            <p class="order-detail__note">
              Payment is verified manually against the bank transfer.
            </p>
            <div
              v-if="paymentActions(selectedOrder.payment_status).length"
              class="order-detail__actions"
            >
              <button
                v-for="action in paymentActions(selectedOrder.payment_status)"
                :key="action"
                class="order-detail__btn order-detail__btn--payment"
                @click="markPayment(action)"
              >
                {{ paymentActionLabel(action) }}
              </button>
            </div>
          </div>

          <div class="order-detail__section">
            <h3 class="order-detail__section-title">Order Status</h3>
            <p class="order-detail__text">
              Current: {{ displayStatus(selectedOrder) }}
            </p>
            <div v-if="!isCanceled(selectedOrder) && NEXT_STATUS[selectedOrder.status]" class="order-detail__actions">
              <button
                class="order-detail__btn order-detail__btn--status"
                @click="advanceStatus(NEXT_STATUS[selectedOrder.status]!.next)"
              >
                {{ NEXT_STATUS[selectedOrder.status]!.label }}
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
.orders-admin {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.orders-admin__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.orders-admin__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.orders-admin__search {
  flex: 1;
  min-width: 180px;
  padding: 10px 14px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.orders-admin__select {
  padding: 10px 12px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.orders-admin__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.orders-admin__hint {
  margin: 0;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.orders-admin__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.order-row__header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.order-row__id {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
  margin-right: auto;
}

.order-row__badge {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 11px;
  white-space: nowrap;
}

.order-row__badge--payment {
  background: var(--color-yellow);
  color: var(--color-deep-brown);
}

.order-row__badge--status {
  background: var(--color-green-soft);
  color: #fff;
}

.order-row__meta {
  display: flex;
  gap: 16px;
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.order-row__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.order-row__total {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-green);
}

.order-row__view {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.order-detail__overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px;
  background: rgba(139, 94, 60, 0.35);
  overflow-y: auto;
}

.order-detail {
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
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
  font-size: 18px;
  color: var(--color-deep-brown);
}

.order-detail__close {
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.order-detail__hint {
  margin: 0;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.order-detail__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.order-detail__section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 12px;
  border-top: 1px solid var(--color-beige);
}

.order-detail__section-title {
  margin: 0 0 4px;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.order-detail__note {
  margin: 4px 0 0;
  font-family: var(--font-secondary);
  font-size: 12px;
  color: var(--color-bread-brown);
}

.order-detail__items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-detail__item {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.order-detail__item-name {
  flex: 1;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__item-qty {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.order-detail__item-subtotal {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__total-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding-top: 8px;
  margin-top: 4px;
  border-top: 1px solid var(--color-beige);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.order-detail__total {
  font-weight: 700;
  font-size: 16px;
  color: var(--color-green);
}

.order-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
}

.order-detail__btn {
  padding: 10px 16px;
  border-radius: var(--radius-pill);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.order-detail__btn--payment {
  background: var(--color-green);
  color: #fff;
}

.order-detail__btn--status {
  background: var(--color-orange);
  color: #fff;
}
</style>