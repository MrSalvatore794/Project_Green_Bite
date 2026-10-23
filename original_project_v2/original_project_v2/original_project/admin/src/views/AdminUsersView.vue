<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchUser, fetchUsers } from '../services/users'
import type { AdminUser, AdminUserOrder } from '../services/users'
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

const users = ref<AdminUser[]>([])
const loading = ref(true)
const error = ref('')

const search = ref('')
const roleFilter = ref('all')

const showDetail = ref(false)
const selectedUser = ref<AdminUser | null>(null)
const selectedOrders = ref<AdminUserOrder[]>([])
const loadingDetail = ref(false)
const detailError = ref('')

const filteredUsers = computed(() => {
  let result = [...users.value]
  const q = search.value.trim().toLowerCase()
  if (q) {
    result = result.filter((u) => {
      return (
        u.name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        (u.phone ?? '').toLowerCase().includes(q)
      )
    })
  }
  if (roleFilter.value !== 'all') {
    result = result.filter((u) => u.role === roleFilter.value)
  }
  return result
})

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
    users.value = await fetchUsers()
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

async function openDetail(user: AdminUser): Promise<void> {
  showDetail.value = true
  loadingDetail.value = true
  detailError.value = ''
  selectedUser.value = user
  selectedOrders.value = []
  try {
    const data = await fetchUser(user.id)
    selectedUser.value = data.user
    selectedOrders.value = data.orders
  } catch (err) {
    detailError.value = errorMessage(err)
  } finally {
    loadingDetail.value = false
  }
}

function closeDetail(): void {
  showDetail.value = false
  selectedUser.value = null
  selectedOrders.value = []
}

onMounted(load)
</script>

<template>
  <section class="users-admin">
    <h1 class="users-admin__title">User Management</h1>

    <div class="users-admin__controls">
      <input
        v-model="search"
        class="users-admin__search"
        type="search"
        placeholder="Search name, email, phone…"
      />
      <select v-model="roleFilter" class="users-admin__select">
        <option value="all">All roles</option>
        <option value="customer">Customer</option>
        <option value="admin">Admin</option>
      </select>
    </div>

    <p v-if="error" class="users-admin__error" role="alert">{{ error }}</p>
    <p v-if="loading" class="users-admin__hint">Loading users…</p>
    <p v-else-if="filteredUsers.length === 0" class="users-admin__hint">No users found.</p>

    <ul v-else class="users-admin__list">
      <li v-for="user in filteredUsers" :key="user.id" class="user-row">
        <div class="user-row__body">
          <div class="user-row__header">
            <span class="user-row__name">{{ user.name }}</span>
            <span
              class="user-row__badge"
              :class="user.role === 'admin' ? 'user-row__badge--admin' : 'user-row__badge--customer'"
            >
              {{ user.role === 'admin' ? 'Admin' : 'Customer' }}
            </span>
          </div>
          <span class="user-row__email">{{ user.email }}</span>
          <span class="user-row__phone">{{ user.phone ?? '—' }}</span>
        </div>
        <button class="user-row__view" @click="openDetail(user)">View</button>
      </li>
    </ul>

    <div v-if="showDetail" class="user-detail__overlay" @click.self="closeDetail">
      <div class="user-detail">
        <div class="user-detail__header">
          <h2 class="user-detail__title">User #{{ selectedUser?.id ?? '…' }}</h2>
          <button class="user-detail__close" @click="closeDetail">Close</button>
        </div>

        <p v-if="loadingDetail" class="user-detail__hint">Loading…</p>
        <p v-if="detailError" class="user-detail__error" role="alert">{{ detailError }}</p>

        <template v-if="selectedUser">
          <div class="user-detail__section">
            <h3 class="user-detail__section-title">Customer information</h3>
            <p class="user-detail__text">Name: {{ selectedUser.name }}</p>
            <p class="user-detail__text">Email: {{ selectedUser.email }}</p>
            <p class="user-detail__text">Phone: {{ selectedUser.phone ?? '—' }}</p>
            <p class="user-detail__text">
              Role: {{ selectedUser.role === 'admin' ? 'Admin' : 'Customer' }}
            </p>
          </div>

          <div class="user-detail__section">
            <h3 class="user-detail__section-title">Orders ({{ selectedOrders.length }})</h3>
            <p v-if="selectedOrders.length === 0" class="user-detail__text">No orders.</p>
            <ul v-else class="user-detail__orders">
              <li v-for="order in selectedOrders" :key="order.id" class="user-detail__order">
                <span class="user-detail__order-id">Order #{{ order.id }}</span>
                <span class="user-detail__order-meta">
                  {{ order.pickup_date }} · {{ order.pickup_time }}
                </span>
                <span class="user-detail__order-total">
                  ${{ order.total_amount.toFixed(2) }}
                </span>
                <span class="user-detail__order-status">
                  {{ paymentLabel(order.payment_status) }} · {{ statusLabel(order.status) }}
                </span>
              </li>
            </ul>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
.users-admin {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.users-admin__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.users-admin__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.users-admin__search {
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

.users-admin__select {
  padding: 10px 12px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.users-admin__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.users-admin__hint {
  margin: 0;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.users-admin__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.user-row__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-row__header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-row__name {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.user-row__badge {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 11px;
  white-space: nowrap;
}

.user-row__badge--admin {
  background: var(--color-orange);
  color: #fff;
}

.user-row__badge--customer {
  background: var(--color-green-soft);
  color: #fff;
}

.user-row__email {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-deep-brown);
}

.user-row__phone {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.user-row__view {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.user-detail__overlay {
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

.user-detail {
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

.user-detail__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.user-detail__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 18px;
  color: var(--color-deep-brown);
}

.user-detail__close {
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
}

.user-detail__hint {
  margin: 0;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.user-detail__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.user-detail__section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 12px;
  border-top: 1px solid var(--color-beige);
}

.user-detail__section-title {
  margin: 0 0 4px;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.user-detail__text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.user-detail__orders {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-detail__order {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 6px 12px;
  align-items: baseline;
  padding: 10px;
  border-radius: var(--radius-md);
  background: var(--color-cream);
}

.user-detail__order-id {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 13px;
  color: var(--color-deep-brown);
}

.user-detail__order-meta {
  font-family: var(--font-secondary);
  font-size: 12px;
  color: var(--color-bread-brown);
}

.user-detail__order-total {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 13px;
  color: var(--color-green);
}

.user-detail__order-status {
  grid-column: 1 / -1;
  font-family: var(--font-secondary);
  font-size: 12px;
  color: var(--color-deep-brown);
}
</style>