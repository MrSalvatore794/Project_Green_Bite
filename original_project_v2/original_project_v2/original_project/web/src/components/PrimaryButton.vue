<script setup lang="ts">
defineProps<{ type?: 'button' | 'submit'; disabled?: boolean }>()
const emit = defineEmits<{ (e: 'click'): void }>()
</script>

<template>
  <button class="primary-button" :type="type ?? 'button'" :disabled="disabled" @click="emit('click')">
    <slot />
  </button>
</template>

<style scoped>
.primary-button {
  width: 100%;
  padding: 14px 24px;
  border-radius: var(--radius-pill);
  background: var(--color-orange);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 16px;
  box-shadow: var(--shadow-soft);
  transition: transform 0.1s ease, opacity 0.1s ease;
}

.primary-button:active {
  transform: scale(0.98);
}

.primary-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
