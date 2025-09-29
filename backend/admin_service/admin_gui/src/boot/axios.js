import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

export default boot(({ app, router }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !originalRequest.url.includes('/auth/refresh')
      ) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            failedQueue.push(() => resolve(api(originalRequest)))
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const response = await api.post('/auth/refresh', {}, { withCredentials: true })
          const newToken = response.data.access_token

          localStorage.setItem('access_token', newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`

          failedQueue.forEach((cb) => cb())
          failedQueue = []

          return api(originalRequest)
        } catch (refreshError) {
          failedQueue.forEach((cb) => cb())
          failedQueue = []
          localStorage.removeItem('access_token')

          router.push('/login')
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    },
  )
})

export function loginUser(credentials) {
  const formData = new URLSearchParams()
  formData.append('email', credentials.email)
  formData.append('password', credentials.password)

  return api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export function logoutUser() {
  return api.post(
    '/auth/logout',
    {},
    {
      withCredentials: true,
    },
  )
}

export { axios, api }
