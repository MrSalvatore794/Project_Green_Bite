<script setup lang="ts">
import { useRouter } from 'vue-router'
import PrimaryButton from '../components/PrimaryButton.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
</script>

<template>
  <section class="home">
    <div class="home__hero">
      <div class="home__cta">
        <PrimaryButton @click="router.push('/products')">Get Started</PrimaryButton>
      </div>
    </div>

    <div v-if="!auth.isAuthenticated" class="home__auth">
      <button class="home__auth-link" @click="router.push('/login')">Login</button>
      <span class="home__auth-sep">·</span>
      <button class="home__auth-link" @click="router.push('/register')">Create account</button>
    </div>
  </section>
</template>

<style scoped>
.home {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* AD1 fills the hero area with CSS cover behaviour (no stretch / no contain). */
.home__hero {
  position: relative;
  flex: 1;
  min-height: 0;
  border-radius: var(--radius-lg);
  background-image: url('/assets/brand/ad1.png');
  background-size: cover;
  background-position: center;
  background-color: var(--color-beige);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

/* Get Started sits ON TOP of the poster, centred in the reserved CTA area. */
.home__cta {
  position: absolute;
  left: 50%;
  bottom: 12%;
  transform: translateX(-50%);
  width: 70%;
}

.home__auth {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 2px 0;
}

.home__auth-link {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-deep-brown);
  padding: 4px 8px;
}

.home__auth-sep {
  color: var(--color-bread-brown);
}
</style>

