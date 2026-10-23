<script setup lang="ts">
import type { Product } from '../services/products'

defineProps<{ product: Product }>()
</script>

<template>
  <router-link :to="`/products/${product.id}`" class="product-card">
    <img class="product-card__image" :src="product.image_url" :alt="product.name" />
    <div class="product-card__body">
      <h3 class="product-card__name">{{ product.name }}</h3>
      <span class="product-card__price">${{ product.price.toFixed(2) }}</span>
      <span class="product-card__cta">Details</span>
    </div>
  </router-link>
</template>

<style scoped>
.product-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
  text-decoration: none;
}

.product-card__image {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  background: var(--color-beige);
}

.product-card__body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
}

.product-card__name {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  line-height: 1.25;
  color: var(--color-deep-brown);
}

.product-card__price {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-green);
}

.product-card__cta {
  align-self: flex-start;
  margin-top: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  background: var(--color-orange);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 12px;
}
</style>
