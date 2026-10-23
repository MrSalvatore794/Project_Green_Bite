<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import ProductCard from '../components/ProductCard.vue'
import BaseIcon from '../components/BaseIcon.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { fetchLikedProducts, unlikeProduct } from '../services/products'
import type { Product } from '../services/products'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../utils/errors'

const router = useRouter()
const auth = useAuthStore()

const products = ref<Product[]>([])
const loading = ref(true)
const error = ref('')
const removingId = ref<number | null>(null)
const mutationError = ref('')

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    products.value = await fetchLikedProducts()
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

async function onUnlike(product: Product): Promise<void> {
  if (removingId.value !== null) return
  removingId.value = product.id
  mutationError.value = ''
  try {
    await unlikeProduct(product.id)
    products.value = products.value.filter((item) => item.id !== product.id)
  } catch (err) {
    mutationError.value = errorMessage(err)
  } finally {
    removingId.value = null
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace({ path: '/login', query: { redirect: '/liked' } })
    return
  }
  void load()
})
</script>

<template>
  <section class="liked">
    <SectionTitle title="Liked" subtitle="Products you've favourited" />

    <LoadingState v-if="loading" />

    <div v-else-if="error" class="liked__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <p v-else-if="products.length === 0" class="liked__empty">
      You haven't liked any products yet.
    </p>

    <template v-else>
      <ErrorMessage v-if="mutationError" :message="mutationError" />

      <div class="liked__grid">
        <div v-for="product in products" :key="product.id" class="liked__item">
          <ProductCard :product="product" />
          <button
            class="liked__remove"
            :aria-label="`Unlike ${product.name}`"
            :disabled="removingId === product.id"
            @click="onUnlike(product)"
          >
            <BaseIcon name="favorites" :size="18" />
          </button>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.liked {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.liked__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.liked__empty {
  margin: 0;
  padding: 32px 0;
  text-align: center;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.liked__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.liked__item {
  position: relative;
}

.liked__remove {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-soft);
}

.liked__remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
