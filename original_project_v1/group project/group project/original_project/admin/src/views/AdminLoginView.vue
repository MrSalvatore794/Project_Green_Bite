<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminAuthStore } from '../stores/auth'
import { errorMessage } from '../services/errors'

const route = useRoute()
const router = useRouter()
const auth = useAdminAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit(): Promise<void> {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please enter your email and password.'
    return
  }

  loading.value = true
  try {
    const user = await auth.login(email.value, password.value)
    if (user.role !== 'admin') {
      auth.logout()
      error.value = 'This account does not have Admin access.'
      return
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/admin'
    router.push(redirect)
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="admin-login">
    <div class="admin-login__card">
      <div class="admin-login__brand">
        <img class="admin-login__logo" src="/assets/brand/logo2.png" alt="GreenBite Admin" />
        <h1 class="admin-login__title">Admin</h1>
        <p class="admin-login__subtitle">Sign in to manage your store.</p>
      </div>

      <form class="admin-login__form" novalidate @submit.prevent="submit">
        <label class="admin-login__field">
          <span class="admin-login__label">Email</span>
          <input
            v-model="email"
            class="admin-login__input"
            type="email"
            placeholder="admin@example.com"
            autocomplete="username"
            required
          />
        </label>
        <label class="admin-login__field">
          <span class="admin-login__label">Password</span>
          <input
            v-model="password"
            class="admin-login__input"
            type="password"
            placeholder="Your password"
            autocomplete="current-password"
            required
          />
        </label>

        <p v-if="error" class="admin-login__error" role="alert">{{ error }}</p>

        <button class="admin-login__submit" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--color-cream);
}

.admin-login__card {
  width: 100%;
  max-width: 400px;
  padding: 28px;
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.admin-login__brand {
  text-align: center;
  margin-bottom: 20px;
}

.admin-login__logo {
  height: 64px;
  width: auto;
  margin: 0 auto 12px;
}

.admin-login__title {
  margin: 0;
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 24px;
  color: var(--color-deep-brown);
}

.admin-login__subtitle {
  margin: 4px 0 0;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.admin-login__form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.admin-login__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-login__label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-deep-brown);
}

.admin-login__input {
  padding: 12px 16px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 15px;
  color: var(--color-deep-brown);
}

.admin-login__input:focus {
  outline: none;
  border-color: var(--color-green);
}

.admin-login__error {
  margin: 0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(228, 137, 75, 0.12);
  color: var(--color-orange);
  font-family: var(--font-primary);
  font-size: 14px;
}

.admin-login__submit {
  padding: 14px 24px;
  border-radius: var(--radius-pill);
  background: var(--color-green);
  color: #fff;
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 16px;
  box-shadow: var(--shadow-soft);
}

.admin-login__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>