<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

<template>
  <div class="section-title">
    <h2 class="section-title__heading">{{ title }}</h2>
    <p v-if="subtitle" class="section-title__subtitle">{{ subtitle }}</p>
  </div>
</template>

<style scoped>
.section-title {
  margin-bottom: var(--space-4);
}

.section-title__heading {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 22px;
  color: var(--color-deep-brown);
}

.section-title__subtitle {
  margin: 4px 0 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}
</style>
