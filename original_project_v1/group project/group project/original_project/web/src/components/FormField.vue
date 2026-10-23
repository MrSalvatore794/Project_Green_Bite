<script setup lang="ts">
defineProps<{
  label: string
  modelValue: string
  type?: string
  placeholder?: string
  required?: boolean
}>()

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

function onInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <label class="form-field">
    <span class="form-field__label">{{ label }}</span>
    <input
      class="form-field__input"
      :type="type ?? 'text'"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      @input="onInput"
    />
  </label>
</template>

<style scoped>
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field__label {
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 13px;
  color: var(--color-deep-brown);
}

.form-field__input {
  padding: 12px 16px;
  border: 1.5px solid var(--color-beige);
  border-radius: var(--radius-md);
  background: #fff;
  font-family: var(--font-primary);
  font-size: 15px;
  color: var(--color-deep-brown);
}

.form-field__input:focus {
  outline: none;
  border-color: var(--color-green);
}
</style>
