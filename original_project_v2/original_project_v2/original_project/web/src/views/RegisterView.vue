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

const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)

function validate(): string | null {
  if (!name.value.trim()) return 'Please enter your name.'
  if (!email.value.trim()) return 'Please enter your email.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) return 'Please enter a valid email address.'
  if (!phone.value.trim()) return 'Please enter your phone number.'
  if (!password.value) return 'Please enter a password.'
  if (password.value !== confirm.value) return 'Passwords do not match.'
  return null
}

function redirectTarget(): string {
  return typeof route.query.redirect === 'string' ? route.query.redirect : '/'
}

async function submit(): Promise<void> {
  error.value = ''
  const validationError = validate()
  if (validationError) {
    error.value = validationError
    return
  }
  loading.value = true
  try {
    await auth.register(name.value.trim(), email.value.trim(), phone.value.trim(), password.value)
    router.push(redirectTarget())
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="register">
    <SectionTitle title="Create account" subtitle="Join the GreenBite community" />
    <form class="register__form" novalidate @submit.prevent="submit">
      <FormField v-model="name" label="Name" placeholder="Your name" required />
      <FormField v-model="email" label="Email" type="email" placeholder="you@example.com" required />
      <FormField v-model="phone" label="Phone" type="tel" placeholder="021 123 4567" required />
      <FormField v-model="password" label="Password" type="password" placeholder="Password" required />
      <FormField v-model="confirm" label="Confirm password" type="password" placeholder="Confirm password" required />
      <ErrorMessage v-if="error" :message="error" />
      <PrimaryButton type="submit" :disabled="loading">
        {{ loading ? 'Creating account…' : 'Create account' }}
      </PrimaryButton>
    </form>
    <p class="register__hint">
      Already have an account?
      <a href="#" @click.prevent="router.push('/login')">Login</a>
    </p>
  </section>
</template>

<style scoped>
.register {
  display: flex;
  flex-direction: column;
}

.register__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.register__hint {
  margin-top: 20px;
  text-align: center;
  font-family: var(--font-secondary);
  font-size: 14px;
  color: var(--color-bread-brown);
}

.register__hint a {
  font-weight: 700;
  color: var(--color-deep-brown);
}
</style>
