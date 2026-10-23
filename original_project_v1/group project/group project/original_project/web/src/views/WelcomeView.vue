<script setup lang="ts">
import { useRouter } from 'vue-router'
import BrandLogo from '../components/BrandLogo.vue'
import PrimaryButton from '../components/PrimaryButton.vue'

const router = useRouter()
</script>

<template>
  <section class="welcome">
    <BrandLogo variant="welcome" />
    <p class="welcome__slogan">Plant-based goodness, baked fresh daily.</p>
    <p class="welcome__tagline">Vegetarian &amp; Plant-Based · Pre-order Pickup</p>
    <div class="welcome__actions">
      <PrimaryButton @click="router.push('/home')">Get Started</PrimaryButton>
      <button class="welcome__secondary" @click="router.push('/login')">Login</button>
      <button class="welcome__secondary" @click="router.push('/register')">Create account</button>
    </div>
  </section>
</template>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
  padding-top: 48px;
}

.welcome__slogan {
  margin: 4px 0 0;
  font-family: var(--font-handwritten);
  font-size: 30px;
  line-height: 1.2;
  color: var(--color-deep-brown);
}

.welcome__tagline {
  margin: 0 0 20px;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.welcome__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.welcome__secondary {
  padding: 12px;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 15px;
  color: var(--color-deep-brown);
  border-radius: var(--radius-pill);
  background: var(--color-beige);
}
</style>
