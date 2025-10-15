<template>
  <div class="UserAuthDialog">
    <div v-if="!authStore.isAuthenticated" class="auth-buttons__container">
      <button class="auth-button" @click="openAuthModal">
        <LoginIcon />
        {{ t('UserAuthDialog.Enter') }}
      </button>
    </div>
    <div v-else class="auth-buttons__container">
      <button class="auth-button" @click="goToAccount">
        {{ t('UserAuthDialog.MyAccount') }}
      </button>
      <button class="auth-button logout" @click="handleLogout">
        <LogoutIcon />
      </button>
    </div>

    <div v-if="showAuthModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <button class="modal-close" @click="closeModals">×</button>

        <div class="modal-body">
          <div
            class="auth-form"
            v-if="!showRegModal && !showForgotPassModal && !showEmailSentModal"
          >
            <form @submit.prevent="handleAuthSubmit">
              <div class="form-group">
                <label for="authEmail">{{ t('UserAuthDialog.Email') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="authEmail"
                    name="email"
                    :placeholder="t('UserAuthDialog.EmailPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ authEmailError }}</span>
                </div>
              </div>

              <div class="form-group">
                <label for="authPassword">{{ t('UserAuthDialog.Password') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="authPassword"
                    type="password"
                    name="password"
                    :placeholder="t('UserAuthDialog.PasswordPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ authPasswordError }}</span>
                </div>
                <transition name="fade">
                  <div v-if="authError" class="auth-error">
                    {{ authError }}
                  </div>
                </transition>
              </div>

              <button
                class="submit-button"
                :disabled="!authEmailMeta.valid || !authPasswordMeta.valid"
              >
                {{ t('UserAuthDialog.SubmitEnterButton') }}
              </button>
            </form>

            <div class="form-footer">
              <a href="#" @click.prevent="switchToRegister">{{ t('UserAuthDialog.Register') }}</a>
              <a href="#" @click.prevent="switchToForgotPassword">{{
                t('UserAuthDialog.ForgotPassword')
              }}</a>
            </div>
          </div>

          <!-- Модальное окно регистрации -->
          <div class="reg-form" v-else-if="showRegModal">
            <h3>{{ t('UserAuthDialog.Register') }}</h3>
            <form @submit.prevent="handleRegSubmit">
              <div class="form-group">
                <label for="reg-email">{{ t('UserAuthDialog.Email') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="regEmail"
                    name="email"
                    :placeholder="t('UserAuthDialog.EmailPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ regEmailError }}</span>
                </div>
              </div>

              <div class="form-group">
                <label for="reg-password">{{ t('UserAuthDialog.Password') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="regPassword"
                    type="password"
                    name="password"
                    :placeholder="t('UserAuthDialog.PasswordPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ regPasswordError }}</span>
                </div>
              </div>

              <div class="form-group">
                <label for="reg-password-repeat">{{ t('UserAuthDialog.RepeatPassword') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="regPasswordRepeat"
                    type="password"
                    name="password"
                    :placeholder="t('UserAuthDialog.RepeatPasswordPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ regPasswordRepeatError }}</span>
                </div>
              </div>

              <button
                class="submit-button"
                :disabled="
                  !regEmailMeta.valid || !regPasswordMeta.valid || !regPasswordRepeatMeta.valid
                "
              >
                {{ t('UserAuthDialog.SignUp') }}
              </button>
            </form>

            <div class="form-footer">
              <a href="#" @click.prevent="switchToLogin">{{ t('UserAuthDialog.HaveAnAccount') }}</a>
            </div>
          </div>

          <div class="forgot-pass-form" v-else-if="showForgotPassModal">
            <h3>{{ t('UserAuthDialog.ForgotPassword') }}</h3>
            <form @submit.prevent="handleResetSubmit">
              <div class="form-group">
                <label for="resetPassword">{{ t('UserAuthDialog.ForgotPasswordMsg') }}</label>
                <div class="input-wrapper">
                  <input
                    v-model="resetEmail"
                    name="email"
                    :placeholder="t('UserAuthDialog.EmailPlaceholder')"
                    class="form-input"
                  />
                  <span class="form-error">{{ resetEmailError }}</span>
                </div>
              </div>

              <button class="submit-button" type="submit" :disabled="!resetEmailMeta.valid">
                {{ t('UserAuthDialog.ResetPassword') }}
              </button>
            </form>
          </div>

          <div class="email-sent-form" v-else-if="showEmailSentModal">
            <h3>{{ t('UserAuthDialog.ResetEmailSent') }}</h3>
            <button class="submit-button" @click="closeModals">
              {{ t('UserAuthDialog.CloseModal') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useForm, useField } from 'vee-validate'
import * as yup from 'yup'
import { useRouter } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
import { inject } from 'vue'
import { emailValidation, passwordValidation } from '@utils/validationHelpers.js'
import LoginIcon from '@icons/LoginIcon.vue'
import LogoutIcon from '@icons/LogoutIcon.vue'
import { useAuthStore } from '@stores/authStore.js'
import { getConfig } from '@utils/config'
const { t, locale } = useI18n()
const authError = ref('')
const authStore = useAuthStore()
const router = useRouter()
const toast = inject('toast')

/* Переход в личный кабинет */
const goToAccount = () => router.push('/account')

/* Управление преключением модальных окон */
const showAuthModal = ref(false)
const showRegModal = ref(false)
const showForgotPassModal = ref(false)
const showEmailSentModal = ref(false)

const openAuthModal = () => {
  showAuthModal.value = true
}

const closeModals = () => {
  showAuthModal.value = false
  showRegModal.value = false
  showForgotPassModal.value = false
  showEmailSentModal.value = false
}

const switchToRegister = () => {
  showRegModal.value = true
}

const switchToLogin = () => {
  showRegModal.value = false
}

const switchToForgotPassword = () => {
  showForgotPassModal.value = true
}

const switchToEmailSentModal = () => {
  showForgotPassModal.value = false
  showEmailSentModal.value = true
}

/* Управление валидацией полей форм модальных окон */
// Форма авторизации
const authForm = useForm({
  validationSchema: computed(() =>
    yup.object({
      email: emailValidation(t),
      password: passwordValidation(t),
    }),
  ),
})

const {
  value: authEmail,
  errorMessage: authEmailError,
  meta: authEmailMeta,
} = useField('email', undefined, { form: authForm })
const {
  value: authPassword,
  errorMessage: authPasswordError,
  meta: authPasswordMeta,
} = useField('password', undefined, { form: authForm })

// Форма регистрации
const regForm = useForm({
  validationSchema: computed(() =>
    yup.object({
      email: emailValidation(t),
      password: passwordValidation(t),
      passwordRepeat: passwordValidation(t).oneOf(
        [yup.ref('password')],
        t('validation.passwordsMustMatch'),
      ),
    }),
  ),
})

const {
  value: regEmail,
  errorMessage: regEmailError,
  meta: regEmailMeta,
} = useField('email', undefined, { form: regForm })
const {
  value: regPassword,
  errorMessage: regPasswordError,
  meta: regPasswordMeta,
} = useField('password', undefined, { form: regForm })
const {
  value: regPasswordRepeat,
  errorMessage: regPasswordRepeatError,
  meta: regPasswordRepeatMeta,
} = useField('passwordRepeat', undefined, { form: regForm })

// Форма сброса пароля
const resetForm = useForm({
  validationSchema: computed(() =>
    yup.object({
      email: emailValidation(t),
    }),
  ),
})

const {
  value: resetEmail,
  errorMessage: resetEmailError,
  meta: resetEmailMeta,
} = useField('email', undefined, { form: resetForm, validateOnValueUpdate: true })

// Обработчики
const handleAuthSubmit = authForm.handleSubmit(async (values) => {
  handleLogin(values.email, values.password)
})

const handleRegSubmit = regForm.handleSubmit((values) => {
  handleRegister(values.email, values.password)
})

const handleResetSubmit = resetForm.handleSubmit(async (values) => {
  try {
    await axios.post(`${getConfig('VITE_API_BASE_URL')}/forgot-password`, {
      email: values.email,
    })
    switchToEmailSentModal()
  } catch (err) {
    console.error('Ошибка восстановления пароля:', err)
    switchToEmailSentModal()
  }
})

/* Динамическая смена языка в модальных окнах */
watch(locale, () => {
  authForm.resetForm()
  regForm.resetForm()
  resetForm.resetForm()
})

const handleLogin = async (email, password) => {
  try {
    const result = await authStore.login({ email, password })

    if (result.success) {
      toast.success(t('auth.successful'))
      closeModals()
    } else {
      toast.error(result.error)
    }
  } catch (err) {
    toast.error(t('auth.login_error'))
  }
}

const handleLogout = async () => {
  await authStore.logout()
  toast.warning(t('auth.logout'))
  router.push('/')
  closeModals()
}

const handleRegister = async (email, password) => {
  try {
    const result = await authStore.register({
      email,
      password,
      roles: ['user'],
    })

    if (result.success) {
      toast.success(t('auth.successful'))
      closeModals()
    } else {
      toast.error(result.error)
    }
  } catch (err) {
    toast.error(t('auth.network_error'))
  }
}
</script>

<style scoped>
.UserAuthDialog {
  display: flex;
  align-content: center;
}

.auth-buttons__container {
  display: flex;
  width: 100%;
  height: 40px;
  gap: 2px;
}

.auth-button {
  position: relative;

  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1;

  font-family: inherit;
  font-size: 16px;
  border-radius: 5px;
  background: var(--button-background-color);
  color: var(--text-color);
  cursor: pointer;
}

.auth-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  transition: width 0.9s ease;
  z-index: -10;
}

.auth-button:hover {
  background-color: var(--hover-button-background-color);
}

.auth-button:hover::before {
  width: 100%;
  opacity: 1;
}

.logout {
  max-width: 40px;
  background-color: var(--logout-background-color);
}

/* Стили модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  color: var(--text-color);
  background: var(--modal-background);
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: modalFadeIn 0.3s ease-out;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 1rem 0;
}

.auth-form,
.reg-form,
.forgot-pass-form,
.email-sent-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  position: relative;
  align-items: stretch;
  gap: 3px;
}

.form-input {
  padding: 0.75rem;
  color: var(--text-color);
  background-color: var(--modal-input-background);
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--selection-color);
}

.submit-button {
  padding: 0.75rem;
  width: 100%;
  background-color: var(--modal-button-background);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: var(--modal-hover-button-background);
}

.submit-button:disabled {
  background-color: var(--modal-disabled-button-background);
  color: var(--modal-disabled-button-text);
  cursor: not-allowed;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.form-footer a {
  color: var(--text-color);
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  position: relative;
  margin-bottom: 1.5rem;
}

.form-error {
  position: absolute;
  bottom: -1.25rem;
  left: 0;
  color: var(--error-text-color);
  font-size: 0.8rem;
  white-space: nowrap;
}

.auth-error {
  color: var(--error-text-color);
  margin-bottom: 10px;
  padding: 8px 12px;
  background: var(--modal-background);
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Анимация появления */
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
