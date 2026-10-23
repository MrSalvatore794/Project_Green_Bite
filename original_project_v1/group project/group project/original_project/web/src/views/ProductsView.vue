<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LoadingState from '../components/LoadingState.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import ProductCard from '../components/ProductCard.vue'
import { fetchProducts } from '../services/products'
import type { Product } from '../services/products'
import { errorMessage } from '../utils/errors'

const products = ref<Product[]>([])
const loading = ref(true)
const error = ref('')

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    products.value = await fetchProducts()
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="products">
    <div class="products__banner">
      <img class="products__banner-image" src="/assets/brand/banner1.png" alt="GreenBite banner" />
    </div>

    <LoadingState v-if="loading" />

    <div v-else-if="error" class="products__error">
      <ErrorMessage :message="error" />
      <PrimaryButton @click="load">Try again</PrimaryButton>
    </div>

    <p v-else-if="products.length === 0" class="products__empty">
      No products are available right now.
    </p>

    <div v-else class="products__grid">
      <ProductCard v-for="product in products" :key="product.id" :product="product" />
    </div>
  </section>
</template>

<style scoped>
.products {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.products__banner {
  overflow: hidden;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  background: var(--color-beige);
}

.products__banner-image {
  display: block;
  width: 100%;
  height: auto;
}

.products__error {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.products__empty {
  margin: 0;
  padding: 32px 0;
  text-align: center;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.products__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
</style>
