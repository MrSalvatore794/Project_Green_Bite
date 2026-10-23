<script setup lang="ts">
import { useRouter } from 'vue-router'
import SectionTitle from '../components/SectionTitle.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout(): void {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <section class="account">
    <SectionTitle title="Account" />
    <template v-if="auth.isAuthenticated && auth.state.user">
      <div class="account__card">
        <p class="account__name">{{ auth.state.user.name }}</p>
        <p class="account__field">{{ auth.state.user.email }}</p>
        <p v-if="auth.state.user.phone" class="account__field">{{ auth.state.user.phone }}</p>
      </div>
      <PrimaryButton @click="logout">Log out</PrimaryButton>
    </template>
    <template v-else>
      <p class="account__hint">Sign in to view your account.</p>
      <PrimaryButton @click="router.push('/login')">Login</PrimaryButton>
    </template>
  </section>
</template>

<style scoped>
.account {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.account__card {
  padding: 20px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.account__name {
  margin: 0 0 8px;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 20px;
  color: var(--color-deep-brown);
}

.account__field {
  margin: 2px 0;
  font-family: var(--font-secondary);
  font-size: 15px;
  color: var(--color-bread-brown);
}

.account__hint {
  margin: 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}
</style>
