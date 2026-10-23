<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SectionTitle from '../components/SectionTitle.vue'
import FormField from '../components/FormField.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../utils/errors'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function redirectTarget(): string {
  return typeof route.query.redirect === 'string' ? route.query.redirect : '/'
}

async function submit(): Promise<void> {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please enter your email and password.'
    return
  }
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(redirectTarget())
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="login">
    <SectionTitle title="Login" subtitle="Welcome back to GreenBite" />
    <form class="login__form" novalidate @submit.prevent="submit">
      <FormField v-model="email" label="Email" type="email" placeholder="you@example.com" required />
      <FormField v-model="password" label="Password" type="password" placeholder="Password" required />
      <ErrorMessage v-if="error" :message="error" />
      <PrimaryButton type="submit" :disabled="loading">
        {{ loading ? 'Logging in…' : 'Login' }}
      </PrimaryButton>
    </form>
    <p class="login__hint">
      No account yet?
      <a href="#" @click.prevent="router.push('/register')">Register</a>
    </p>
  </section>
</template>

<style scoped>
.login {
  display: flex;
  flex-direction: column;
}

.login__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login__hint {
  margin-top: 20px;
  text-align: center;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.login__hint a {
  font-weight: 700;
  color: var(--color-deep-brown);
}
</style>
