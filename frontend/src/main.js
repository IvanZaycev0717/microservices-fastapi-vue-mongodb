import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import toast from './plugins/toast'
import VueClickAway from 'vue3-click-away'
import VueLazyLoad from 'vue-lazyload'
import VueEasyLightbox from 'vue-easy-lightbox'
import Vue3EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import en from '@/assets/locales/en.json'
import ru from '@/assets/locales/ru.json'
import errorImage from '@assets/placeholders/error-image.webp'
import cardPlaceholder from '@assets/placeholders/card-placeholder.webp'

import '@utils/axiosInterceptor.js'

const originalAddEventListener = EventTarget.prototype.addEventListener
EventTarget.prototype.addEventListener = function (type, listener, options) {
  const scrollBlockingEvents = ['wheel', 'touchstart', 'touchmove', 'touchend']

  if (scrollBlockingEvents.includes(type)) {
    if (typeof options === 'object') {
      options = { ...options, passive: true }
    } else if (options === undefined || typeof options === 'boolean') {
      options = { passive: true }
    }
  }

  originalAddEventListener.call(this, type, listener, options)
}

const i18n = createI18n({
  legacy: false,
  objectNotation: true,
  locale: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',
  messages: { en, ru },
})

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
import { useAuthStore } from '@stores/authStore.js'
const authStore = useAuthStore()

if (!authStore.accessToken) {
  authStore.refreshToken().then((success) => {
    if (success) {
      console.log('Access token refreshed on app start')
    }
  })
}

app.component('EasyDataTable', Vue3EasyDataTable)
app.use(VueEasyLightbox)
app.use(VueLazyLoad, {
  preLoad: 1.2,
  error: errorImage,
  loading: cardPlaceholder,
  attempt: 2,
  throttleWait: 300,
})
app.use(i18n)
app.use(toast)
app.use(router)
app.use(VueClickAway)
app.mount('#app')
