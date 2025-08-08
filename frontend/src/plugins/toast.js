import { createApp, ref } from 'vue'
import Toast from '@components/ToastMessage.vue'

const toastQueue = ref([])
let toastCount = 0

export default {
  install(app) {
    const showToast = (message, type = 'info', duration = 5000) => {
      const id = toastCount++
      const container = document.createElement('div')
      document.body.appendChild(container)

      const toastApp = createApp(Toast, {
        message,
        type,
        duration,
        onClose: () => {
          toastApp.unmount()
          document.body.removeChild(container)
          toastQueue.value = toastQueue.value.filter((t) => t.id !== id)
        },
      })

      toastApp.mount(container)

      const toast = { id, component: toastApp }
      toastQueue.value.push(toast)

      return toast
    }

    const toast = {
      success: (message, duration) => showToast(message, 'success', duration),
      error: (message, duration) => showToast(message, 'error', duration),
      warning: (message, duration) => showToast(message, 'warning', duration),
      info: (message, duration) => showToast(message, 'info', duration),
    }

    app.config.globalProperties.$toast = toast
    app.provide('toast', toast)
  },
}
