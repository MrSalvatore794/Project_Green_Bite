<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ name: string; size?: number }>()

// Supplied GreenBite icon assets (in /public/assets/icons).
const PNG_ICONS: Record<string, string> = {
  home: 'home.png',
  products: 'products.png',
  cart: 'cart.png',
  account: 'account.png',
  orders: 'orders.png',
  logout: 'logout.png',
  setting: 'setting.png',
  chat: 'chat.png',
  favorites: 'favorites.png',
  info: 'info.png',
}

// Fallback line icons for names without a supplied asset.
const SVG_PATHS: Record<string, string> = {
  back: '<path d="M15 4l-8 8 8 8"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  leaf: '<path d="M12 3C6 6 4 11 5 16c1 5 6 6 9 3 4-4 5-10 1-14-1-1.5-2-2-3-2z"/><path d="M12 3c-.5 7-.5 14-1 18"/>',
}

const isPng = computed(() => props.name in PNG_ICONS)
const src = computed(() => `/assets/icons/${PNG_ICONS[props.name] ?? ''}`)

const svg = computed(() => {
  const size = props.size ?? 24
  const inner = SVG_PATHS[props.name] ?? SVG_PATHS.leaf
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`
})
</script>

<template>
  <img
    v-if="isPng"
    class="base-icon__img"
    :src="src"
    :width="size ?? 24"
    :height="size ?? 24"
    alt=""
    aria-hidden="true"
  />
  <span v-else class="base-icon" v-html="svg" />
</template>

<style scoped>
.base-icon,
.base-icon__img {
  display: inline-block;
  line-height: 0;
}
</style>
