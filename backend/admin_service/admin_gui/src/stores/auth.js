import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'boot/axios'


export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const isRefreshing = ref(false)

  const setToken = (token) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  const clearToken = () => {
    accessToken.value = null
    localStorage.removeItem('access_token')
  }

  const tryRefresh = async () => {
    if (isRefreshing.value) return false
    isRefreshing.value = true

    try {
      const response = await api.post(
        '/auth/refresh',
        {},
        {
          withCredentials: true,
        },
      )
      setToken(response.data.access_token)
      return true
    } catch (error) {
      clearToken()
      console.log(error)
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  return { accessToken, setToken, clearToken, tryRefresh }
})