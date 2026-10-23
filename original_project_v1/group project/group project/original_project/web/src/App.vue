<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import BottomNavigation from './components/BottomNavigation.vue'

const route = useRoute()
</script>

<template>
  <div class="app-shell" :class="{ 'app-shell--no-scroll': route.meta.noScroll }">
    <AppHeader />
    <main class="app-main" :class="{ 'app-main--no-scroll': route.meta.noScroll }">
      <router-view />
    </main>
    <BottomNavigation v-if="!route.meta.hideNav" />
  </div>
</template>

<style scoped>
.app-shell {
  max-width: 430px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-cream);
  box-shadow: 0 0 40px rgba(139, 94, 60, 0.12);
}

.app-shell--no-scroll {
  height: 100vh;
  overflow: hidden;
}

.app-main {
  flex: 1;
  padding: var(--space-4);
}

.app-main--no-scroll {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
