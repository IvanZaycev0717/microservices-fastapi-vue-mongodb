import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  const checkAuth = async () => {
    try {
      isLoading.value = true
      const response = await axios.get('http://localhost:3000/api/check-auth', {
        withCredentials: true,
      })

      isAuthenticated.value = response.data.isAuthenticated
      return response.data.isAuthenticated
    } catch (err) {
      error.value = err.response?.data?.error || 'Auth check failed'
      isAuthenticated.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  const login = async (credentials) => {
    try {
      isLoading.value = true
      await axios.post('http://localhost:3000/api/login', credentials, {
        withCredentials: true,
      })
      isAuthenticated.value = true
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      isAuthenticated.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      isLoading.value = true
      await axios.post('http://localhost:3000/api/logout', {}, { withCredentials: true })

      isAuthenticated.value = false
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Logout failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    isAuthenticated,
    isLoading,
    error,
    checkAuth,
    login,
    logout,
  }
})
