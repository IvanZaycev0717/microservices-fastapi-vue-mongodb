import axios from 'axios'

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request interceptor
axios.interceptors.request.use(
  (config) => {
    // Токен будет добавляться через authStore в каждом компоненте
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor для обработки 401
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Здесь нужен доступ к authStore, но его нет глобально
      // Пока оставляем базовую логику
      console.log('401 error - token expired')
    }

    return Promise.reject(error)
  }
)