<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import FormField from '../components/FormField.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { useAuthStore } from '../stores/auth'
import { fetchCart } from '../services/cart'
import type { Cart } from '../services/cart'
import { createOrder } from '../services/orders'
import type { Order } from '../services/orders'
import { errorMessage } from '../utils/errors'

const BANK = {
  bank: 'BNZ',
  accountName: 'Wanggui Song',
  accountNumber: '12-3638-0248893-00',
}

const router = useRouter()
const auth = useAuthStore()

const cart = ref<Cart | null>(null)
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const submitError = ref('')
const confirmedOrder = ref<Order | null>(null)

const customerName = ref('')
const phone = ref('')
const pickupDate = ref('')
const pickupTime = ref('')
const paymentReference = ref('')

const isEmpty = computed(() => cart.value !== null && cart.value.items.length === 0)

async function loadCart(): Promise<void> {
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

watch(
  () => auth.state.user,
  (user) => {
    if (!user) return
    if (!customerName.value) customerName.value = user.name
    if (!phone.value) phone.value = user.phone ?? ''
  },
  { immediate: true },
)

async function confirmOrder(): Promise<void> {
  if (submitting.value) return
  submitError.value = ''

  const missing: string[] = []
  if (!customerName.value.trim()) missing.push('name')
  if (!phone.value.trim()) missing.push('phone')
  if (!pickupDate.value) missing.push('pickup date')
  if (!pickupTime.value) missing.push('pickup time')
  if (!paymentReference.value.trim()) missing.push('payment reference')
  if (missing.length) {
    submitError.value = 'Please complete: ' + missing.join(', ') + '.'
    return
  }

  submitting.value = true
  try {
    const order = await createOrder({
      customer_name: customerName.value.trim(),
      phone: phone.value.trim(),
      pickup_date: pickupDate.value,
      pickup_time: pickupTime.value,
      payment_reference_type: 'bank_transfer',
      payment_reference: paymentReference.value.trim(),
    })
    confirmedOrder.value = order
  } catch (err) {
    submitError.value = errorMessage(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace({ path: '/login', query: { redirect: '/checkout' } })
    return
  }
  void loadCart()
})
</script>

<template>
  <section class="checkout">
    <SectionTitle title="Checkout" subtitle="Review your order and complete payment." />

    <div v-if="confirmedOrder" class="checkout__confirmed">
      <h2 class="checkout__confirmed-title">Order confirmed!</h2>
      <p class="checkout__confirmed-text">
        Thank you for your order. Your payment confirmation has been submitted.
      </p>
      <p class="checkout__confirmed-order">Order #{{ confirmedOrder.id }}</p>
      <PrimaryButton @click="router.push(`/orders/${confirmedOrder.id}`)">View Order</PrimaryButton>
      <button class="checkout__link" @click="router.push('/products')">Continue Shopping</button>
    </div>

    <template v-else>
      <LoadingState v-if="loading" />

      <div v-else-if="error" class="checkout__error">
        <ErrorMessage :message="error" />
        <PrimaryButton @click="loadCart">Try again</PrimaryButton>
      </div>

      <div v-else-if="isEmpty" class="checkout__empty">
        <p class="checkout__empty-text">Your cart is empty.</p>
        <PrimaryButton @click="router.push('/products')">Browse Products</PrimaryButton>
        <button class="checkout__link" @click="router.push('/cart')">Back to Cart</button>
      </div>

      <template v-else-if="cart">
        <div class="checkout__card">
          <h2 class="checkout__card-title">Order Summary</h2>
          <ul class="checkout__list">
            <li v-for="item in cart.items" :key="item.product_id" class="checkout__item">
              <img class="checkout__item-image" :src="item.image_url" :alt="item.product_name" />
              <div class="checkout__item-body">
                <span class="checkout__item-name">{{ item.product_name }}</span>
                <span class="checkout__item-meta">
                  ${{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
                </span>
              </div>
              <span class="checkout__item-price">${{ item.subtotal.toFixed(2) }}</span>
            </li>
          </ul>
          <div class="checkout__total-row">
            <span class="checkout__total-label">Total</span>
            <span class="checkout__total">${{ cart.total.toFixed(2) }}</span>
          </div>
        </div>

        <div class="checkout__card">
          <h2 class="checkout__card-title">Payment by Bank Transfer</h2>
          <p class="checkout__note">Please transfer the total amount to:</p>
          <dl class="checkout__bank">
            <div class="checkout__bank-row"><dt>Bank</dt><dd>{{ BANK.bank }}</dd></div>
            <div class="checkout__bank-row"><dt>Account name</dt><dd>{{ BANK.accountName }}</dd></div>
            <div class="checkout__bank-row"><dt>Account number</dt><dd>{{ BANK.accountNumber }}</dd></div>
            <div class="checkout__bank-row"><dt>Amount</dt><dd>${{ cart.total.toFixed(2) }}</dd></div>
          </dl>
        </div>

        <div class="checkout__card">
          <h2 class="checkout__card-title">Pickup</h2>
          <p class="checkout__note">
            Pickup only. Your order will be prepared after the payment confirmation is submitted.
          </p>
        </div>

        <form class="checkout__card" novalidate @submit.prevent="confirmOrder">
          <h2 class="checkout__card-title">Your details</h2>
          <FormField v-model="customerName" label="Name" placeholder="Your name" required />
          <FormField v-model="phone" label="Phone" type="tel" placeholder="Your phone number" required />
          <FormField v-model="pickupDate" label="Pickup date" type="date" required />
          <FormField v-model="pickupTime" label="Pickup time" type="time" required />
          <FormField
            v-model="paymentReference"
            label="Payment reference"
            placeholder="Bank transfer reference"
            required
          />

          <ErrorMessage v-if="submitError" :message="submitError" />

          <PrimaryButton type="submit" :disabled="submitting">
            {{ submitting ? 'Confirming order...' : 'Payment completed & confirm order' }}
          </PrimaryButton>
        </form>

        <button class="checkout__link" @click="router.push('/cart')">Back to Cart</button>
      </template>
    </template>
  </section>
</template>

<style scoped>
.checkout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkout__error,
.checkout__empty {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkout__empty {
  align-items: center;
  padding: 32px 0;
  text-align: center;
}

.checkout__empty-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 15px;
  color: var(--color-bread-brown);
}

.checkout__card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.checkout__card-title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.checkout__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkout__item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.checkout__item-image {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  object-fit: cover;
  background: var(--color-beige);
}

.checkout__item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.checkout__item-name {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.checkout__item-meta {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.checkout__item-price {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.checkout__total-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--color-beige);
}

.checkout__total-label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.checkout__total {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 18px;
  color: var(--color-green);
}

.checkout__note {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.checkout__bank {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkout__bank-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.checkout__bank-row dt {
  color: var(--color-bread-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
}

.checkout__bank-row dd {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 14px;
  color: var(--color-deep-brown);
}

.checkout__link {
  align-self: center;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
  text-decoration: underline;
  padding: 6px 10px;
}

.checkout__confirmed {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 32px 16px;
  text-align: center;
}

.checkout__confirmed-title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 24px;
  color: var(--color-green);
}

.checkout__confirmed-text {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 15px;
  color: var(--color-deep-brown);
}

.checkout__confirmed-order {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-deep-brown);
}
</style>
