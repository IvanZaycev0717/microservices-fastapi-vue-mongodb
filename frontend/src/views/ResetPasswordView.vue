<template>
  <div class="reset-password-view">
    <div class="reset-container">
      <h2>{{ t('ResetPassword.title') }}</h2>

      <form @submit.prevent="handleSubmit" class="reset-form">
        <div class="form-group">
          <label for="email">{{ t('ResetPassword.email') }}</label>
          <div class="input-wrapper">
            <input
              v-model="email"
              type="email"
              name="email"
              :placeholder="t('ResetPassword.emailPlaceholder')"
              class="form-input"
            />
            <span class="form-error">{{ emailError }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="newPassword">{{ t('ResetPassword.newPassword') }}</label>
          <div class="input-wrapper">
            <input
              v-model="newPassword"
              type="password"
              name="newPassword"
              :placeholder="t('ResetPassword.newPasswordPlaceholder')"
              class="form-input"
            />
            <span class="form-error">{{ newPasswordError }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">{{ t('ResetPassword.confirmPassword') }}</label>
          <div class="input-wrapper">
            <input
              v-model="confirmPassword"
              type="password"
              name="confirmPassword"
              :placeholder="t('ResetPassword.confirmPasswordPlaceholder')"
              class="form-input"
            />
            <span class="form-error">{{ confirmPasswordError }}</span>
          </div>
        </div>

        <button
          class="submit-button"
          :disabled="!emailMeta.valid || !newPasswordMeta.valid || !confirmPasswordMeta.valid"
        >
          {{ t('ResetPassword.submit') }}
        </button>
      </form>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useForm, useField } from 'vee-validate'
import * as yup from 'yup'
import axios from 'axios'
import { inject } from 'vue'
import { emailValidation, passwordValidation } from '@utils/validationHelpers.js'
import { getConfig } from '@utils/config'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = inject('toast')

const resetToken = ref('')
const successMessage = ref('')
const errorMessage = ref('')

const resetForm = useForm({
  validationSchema: yup.object({
    email: emailValidation(t),
    newPassword: passwordValidation(t),
    confirmPassword: passwordValidation(t).oneOf(
      [yup.ref('newPassword')],
      t('validation.passwordsMustMatch'),
    ),
  }),
})

const { value: email, errorMessage: emailError, meta: emailMeta } = useField('email')

const {
  value: newPassword,
  errorMessage: newPasswordError,
  meta: newPasswordMeta,
} = useField('newPassword')

const {
  value: confirmPassword,
  errorMessage: confirmPasswordError,
  meta: confirmPasswordMeta,
} = useField('confirmPassword')

onMounted(() => {
  resetToken.value = route.query.token
  if (!resetToken.value) {
    errorMessage.value = t('ResetPassword.invalidToken')
  }
})

const handleSubmit = resetForm.handleSubmit(async (values) => {
  try {
    const response = await axios.post(`${getConfig('VITE_API_BASE_URL')}/reset-password`, {
      reset_token: resetToken.value,
      new_password: values.newPassword,
      email: values.email,
    })

    if (response.data.success) {
      successMessage.value = t('ResetPassword.success')
      toast.success(t('ResetPassword.success'))
      setTimeout(() => {
        router.push('/')
      }, 2000)
    } else {
      errorMessage.value = response.data.message || t('ResetPassword.error')
    }
  } catch (err) {
    errorMessage.value = t('ResetPassword.networkError')
    console.error('Ошибка сброса пароля:', err)
  }
})
</script>

<style scoped>
.reset-password-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 2rem;
}

.reset-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: var(--modal-background);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-color);
}

.reset-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
  color: var(--text-color);
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background: var(--modal-input-background);
  color: var(--text-color);
}

.form-input:focus {
  outline: none;
  border-color: var(--selection-color);
}

.form-error {
  color: var(--error-text-color);
  font-size: 0.8rem;
  position: absolute;
  bottom: -1.25rem;
  left: 0;
}

.submit-button {
  padding: 0.75rem;
  background: var(--button-background-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover:not(:disabled) {
  background: var(--hover-button-background-color);
}

.submit-button:disabled {
  background: var(--modal-disabled-button-background);
  cursor: not-allowed;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #d4edda;
  color: #155724;
  border-radius: 4px;
  text-align: center;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  text-align: center;
}
</style>
