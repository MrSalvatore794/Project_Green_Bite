<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<template>
  <p class="error-message" role="alert">{{ message }}</p>
</template>

<style scoped>
.error-message {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}
</style>
