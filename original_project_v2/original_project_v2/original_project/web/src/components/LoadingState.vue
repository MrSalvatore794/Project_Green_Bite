<template>
  <div class="loading-state" role="status" aria-label="Loading">
    <span class="loading-state__spinner" aria-hidden="true" />
    <span class="loading-state__text">Loading…</span>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 0;
  color: var(--color-bread-brown);
  font-family: var(--font-primary);
}

.loading-state__spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-beige);
  border-top-color: var(--color-green);
  border-radius: 50%;
  animation: loading-spin 0.8s linear infinite;
}

@keyframes loading-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
