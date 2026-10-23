<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createProduct,
  fetchProducts,
  mediaUrl,
  setProductStatus,
  updateProduct,
  updateProductStock,
  uploadProductImage,
} from '../services/products'
import type { AdminProduct } from '../services/products'
import { errorMessage } from '../services/errors'

type Filter = 'all' | 'active' | 'inactive'
type SortKey = 'star' | 'name' | 'stock'

const products = ref<AdminProduct[]>([])
const loading = ref(true)
const error = ref('')

const search = ref('')
const filter = ref<Filter>('all')
const sort = ref<SortKey>('star')

const showForm = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const formError = ref('')

const form = ref({
  name: '',
  description: '',
  price: '0',
  stock: '0',
  starLevel: 0,
  active: true,
})
const mainImageFile = ref<File | null>(null)
const detailImageFile = ref<File | null>(null)
const currentImageUrl = ref('')
const currentDetailUrl = ref('')

const filteredProducts = computed(() => {
  let result = [...products.value]
  const q = search.value.trim().toLowerCase()
  if (q) result = result.filter((p) => p.name.toLowerCase().includes(q))
  if (filter.value === 'active') result = result.filter((p) => p.is_active)
  if (filter.value === 'inactive') result = result.filter((p) => !p.is_active)
  if (sort.value === 'name') result.sort((a, b) => a.name.localeCompare(b.name))
  if (sort.value === 'stock') result.sort((a, b) => a.stock_quantity - b.stock_quantity)
  // 'star' keeps the server's default ordering (star_level DESC).
  return result
})

function stars(level: number): string {
  return '★'.repeat(level) + '☆'.repeat(5 - level)
}

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

function openCreate(): void {
  editingId.value = null
  form.value = { name: '', description: '', price: '0', stock: '0', starLevel: 0, active: true }
  mainImageFile.value = null
  detailImageFile.value = null
  currentImageUrl.value = ''
  currentDetailUrl.value = ''
  formError.value = ''
  showForm.value = true
}

function openEdit(product: AdminProduct): void {
  editingId.value = product.id
  form.value = {
    name: product.name,
    description: product.description,
    price: String(product.price),
    stock: String(product.stock_quantity),
    starLevel: product.star_level,
    active: product.is_active,
  }
  mainImageFile.value = null
  detailImageFile.value = null
  currentImageUrl.value = product.image_url
  currentDetailUrl.value = product.detail_image_url
  formError.value = ''
  showForm.value = true
}

function closeForm(): void {
  showForm.value = false
}

function onMainImage(event: Event): void {
  const input = event.target as HTMLInputElement
  mainImageFile.value = input.files?.[0] ?? null
}

function onDetailImage(event: Event): void {
  const input = event.target as HTMLInputElement
  detailImageFile.value = input.files?.[0] ?? null
}

async function save(): Promise<void> {
  if (saving.value) return
  formError.value = ''

  const price = Number(form.value.price)
  const stock = Number(form.value.stock)
  if (!form.value.name.trim()) {
    formError.value = 'Name is required.'
    return
  }
  if (Number.isNaN(price) || price < 0) {
    formError.value = 'Price must be a non-negative number.'
    return
  }
  if (Number.isNaN(stock) || stock < 0 || !Number.isInteger(stock)) {
    formError.value = 'Stock must be a non-negative integer.'
    return
  }

  saving.value = true
  try {
    let product: AdminProduct
    if (editingId.value === null) {
      product = await createProduct({
        name: form.value.name.trim(),
        description: form.value.description,
        price,
        stock_quantity: stock,
        star_level: form.value.starLevel,
      })
    } else {
      product = await updateProduct(editingId.value, {
        name: form.value.name.trim(),
        description: form.value.description,
        price,
        star_level: form.value.starLevel,
      })
      product = await updateProductStock(product.id, stock)
    }

    if (product.is_active !== form.value.active) {
      product = await setProductStatus(product.id, form.value.active)
    }
    if (mainImageFile.value) {
      product = await uploadProductImage(product.id, mainImageFile.value, 'main')
    }
    if (detailImageFile.value) {
      product = await uploadProductImage(product.id, detailImageFile.value, 'detail')
    }

    showForm.value = false
    await load()
  } catch (err) {
    formError.value = errorMessage(err)
  } finally {
    saving.value = false
  }
}

async function toggleActive(product: AdminProduct): Promise<void> {
  try {
    await setProductStatus(product.id, !product.is_active)
    await load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}

onMounted(load)
</script>

<template>
  <section class="products-admin">
    <div class="products-admin__header">
      <h1 class="products-admin__title">Product Management</h1>
      <button class="products-admin__add" @click="openCreate">Add Product</button>
    </div>

    <div class="products-admin__controls">
      <input
        v-model="search"
        class="products-admin__search"
        type="search"
        placeholder="Search products…"
      />
      <select v-model="filter" class="products-admin__select">
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
      <select v-model="sort" class="products-admin__select">
        <option value="star">Star level</option>
        <option value="name">Name</option>
        <option value="stock">Stock</option>
      </select>
    </div>

    <p v-if="error" class="products-admin__error" role="alert">{{ error }}</p>
    <p v-if="loading" class="products-admin__hint">Loading products…</p>

    <ul v-else class="products-admin__list">
      <li v-for="product in filteredProducts" :key="product.id" class="product-row">
        <img class="product-row__image" :src="mediaUrl(product.image_url)" :alt="product.name" />
        <div class="product-row__body">
          <span class="product-row__name">{{ product.name }}</span>
          <span class="product-row__meta">
            ${{ product.price.toFixed(2) }} · Stock {{ product.stock_quantity }}
          </span>
          <span class="product-row__stars">{{ stars(product.star_level) }}</span>
        </div>
        <span
          class="product-row__status"
          :class="{ 'product-row__status--inactive': !product.is_active }"
        >
          {{ product.is_active ? 'Active' : 'Inactive' }}
        </span>
        <div class="product-row__actions">
          <button class="product-row__btn" @click="openEdit(product)">Edit</button>
          <button class="product-row__btn" @click="toggleActive(product)">
            {{ product.is_active ? 'Deactivate' : 'Activate' }}
          </button>
        </div>
      </li>
    </ul>

    <div v-if="showForm" class="product-form__overlay" @click.self="closeForm">
      <form class="product-form" novalidate @submit.prevent="save">
        <h2 class="product-form__title">
          {{ editingId === null ? 'Add Product' : 'Edit Product' }}
        </h2>

        <label class="product-form__field">
          <span class="product-form__label">Name</span>
          <input v-model="form.name" class="product-form__input" placeholder="Product name" />
        </label>

        <label class="product-form__field">
          <span class="product-form__label">Description</span>
          <textarea
            v-model="form.description"
            class="product-form__input product-form__textarea"
            rows="3"
            placeholder="Description"
          />
        </label>

        <div class="product-form__row">
          <label class="product-form__field">
            <span class="product-form__label">Price</span>
            <input
              v-model="form.price"
              class="product-form__input"
              type="number"
              step="0.01"
              min="0"
            />
          </label>
          <label class="product-form__field">
            <span class="product-form__label">Stock</span>
            <input
              v-model="form.stock"
              class="product-form__input"
              type="number"
              step="1"
              min="0"
            />
          </label>
        </div>

        <label class="product-form__field">
          <span class="product-form__label">Star level (0–5)</span>
          <select v-model.number="form.starLevel" class="product-form__input">
            <option v-for="n in 6" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
          </select>
        </label>

        <label class="product-form__field product-form__check">
          <input v-model="form.active" type="checkbox" />
          <span class="product-form__label">Active</span>
        </label>

        <label class="product-form__field">
          <span class="product-form__label">Main image</span>
          <img
            v-if="currentImageUrl"
            class="product-form__preview"
            :src="mediaUrl(currentImageUrl)"
            alt="Current main image"
          />
          <input type="file" accept=".jpg,.jpeg,.png,.webp" @change="onMainImage" />
        </label>

        <label class="product-form__field">
          <span class="product-form__label">Detail image</span>
          <img
            v-if="currentDetailUrl"
            class="product-form__preview"
            :src="mediaUrl(currentDetailUrl)"
            alt="Current detail image"
          />
          <input type="file" accept=".jpg,.jpeg,.png,.webp" @change="onDetailImage" />
        </label>

        <p v-if="formError" class="product-form__error" role="alert">{{ formError }}</p>

        <div class="product-form__actions">
          <button type="button" class="product-form__cancel" @click="closeForm">Cancel</button>
          <button type="submit" class="product-form__submit" :disabled="saving">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.products-admin {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.products-admin__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.products-admin__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.products-admin__add {
  padding: 10px 18px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
}

.products-admin__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.products-admin__search {
  flex: 1;
  min-width: 160px;
  padding: 10px 14px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.products-admin__select {
  padding: 10px 12px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.products-admin__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.products-admin__hint {
  margin: 0;
  color: var(--color-bread-brown);
  font-family: var(--font-secondary);
  font-size: 14px;
}

.products-admin__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.product-row__image {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  object-fit: cover;
  background: var(--color-beige);
}

.product-row__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.product-row__name {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-deep-brown);
}

.product-row__meta {
  font-family: var(--font-secondary);
  font-size: 13px;
  color: var(--color-bread-brown);
}

.product-row__stars {
  font-size: 13px;
  color: var(--color-yellow);
  letter-spacing: 1px;
}

.product-row__status {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  background: var(--color-green-soft);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 11px;
  white-space: nowrap;
}

.product-row__status--inactive {
  background: var(--color-bread-brown);
}

.product-row__actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.product-row__btn {
  padding: 6px 10px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
}

.product-form__overlay {
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

.product-form {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.product-form__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 18px;
  color: var(--color-deep-brown);
}

.product-form__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.product-form__check {
  flex-direction: row;
  align-items: center;
}

.product-form__label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-deep-brown);
}

.product-form__input {
  padding: 10px 14px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 14px;
  color: var(--color-deep-brown);
}

.product-form__input:focus {
  outline: none;
  border-color: var(--color-green);
}

.product-form__textarea {
  resize: vertical;
}

.product-form__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.product-form__preview {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-beige);
}

.product-form__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.product-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.product-form__cancel {
  padding: 10px 18px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
}

.product-form__submit {
  padding: 10px 20px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
}

.product-form__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>