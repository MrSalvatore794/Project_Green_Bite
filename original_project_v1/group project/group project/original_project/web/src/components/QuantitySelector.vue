<script setup lang="ts">
const props = defineProps<{ modelValue: number; min?: number; max?: number; disabled?: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: number): void }>()

function change(delta: number): void {
  let value = props.modelValue + delta
  if (props.min !== undefined) value = Math.max(props.min, value)
  if (props.max !== undefined) value = Math.min(props.max, value)
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="quantity-selector">
    <button
      type="button"
      class="quantity-selector__btn"
      aria-label="Decrease quantity"
      :disabled="props.disabled || (min !== undefined && modelValue <= min)"
      @click="change(-1)"
    >
      −
    </button>
    <span class="quantity-selector__value" aria-live="polite">{{ modelValue }}</span>
    <button
      type="button"
      class="quantity-selector__btn"
      aria-label="Increase quantity"
      :disabled="props.disabled || (max !== undefined && modelValue >= max)"
      @click="change(1)"
    >
      +
    </button>
  </div>
</template>

<style scoped>
.quantity-selector {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: var(--radius-pill);
  background: var(--color-beige);
}

.quantity-selector__btn {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #fff;
  color: var(--color-deep-brown);
  font-family: var(--font-primary);
  font-size: 20px;
  font-weight: 600;
  line-height: 1;
}

.quantity-selector__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.quantity-selector__value {
  min-width: 28px;
  text-align: center;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 16px;
  color: var(--color-deep-brown);
}
</style>
