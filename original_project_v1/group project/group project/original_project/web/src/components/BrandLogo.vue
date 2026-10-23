<script setup lang="ts">
withDefaults(defineProps<{ variant?: 'header' | 'welcome' }>(), { variant: 'header' })
</script>

<template>
  <router-link to="/" class="brand-logo" aria-label="GreenBite home">
    <img
      v-if="variant === 'welcome'"
      class="brand-logo__img brand-logo__img--welcome"
      src="/assets/brand/logo2.png"
      alt="GreenBite"
    />
    <img
      v-else
      class="brand-logo__img brand-logo__img--header"
      src="/assets/brand/logo1.png"
      alt="GreenBite"
    />
  </router-link>
</template>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  line-height: 0;
}

.brand-logo__img--header {
  height: 38px;
  width: auto;
}

.brand-logo__img--welcome {
  height: 140px;
  width: auto;
}
</style>
