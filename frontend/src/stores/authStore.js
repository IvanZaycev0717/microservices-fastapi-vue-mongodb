import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  if (accessToken.value) {
    isAuthenticated.value = true
  }

  const setAuthData = (token, userData) => {
    accessToken.value = token
    user.value = userData
    isAuthenticated.value = true
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearAuthData = () => {
    accessToken.value = null
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  const checkAuth = async () => {
    try {
      isLoading.value = true
      
      if (!accessToken.value) {
        isAuthenticated.value = false
        return false
      }

      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_API_AUTH_VERIFY}`,
        { token: accessToken.value }
      )

      if (response.data.valid) {
        isAuthenticated.value = true
        return true
      } else {
        clearAuthData()
        return false
      }
    } catch (err) {
      console.error('Auth check failed:', err)
      clearAuthData()
      return false
    } finally {
      isLoading.value = false
    }
  }

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_API_AUTH_LOGIN}`,
        credentials,
        { withCredentials: true }
      )

      setAuthData(response.data.access_token, response.data.user)
      return { success: true, user: response.data.user }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_API_AUTH_REGISTER}`,
        userData,
        { withCredentials: true }
      )

      setAuthData(response.data.access_token, response.data.user)
      return { success: true, user: response.data.user }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      isLoading.value = true
      
      await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_API_AUTH_LOGOUT}`,
        {},
        { 
          withCredentials: true,
          headers: {
            Authorization: `Bearer ${accessToken.value}`
          }
        }
      )
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuthData()
      isLoading.value = false
    }
  }

  const refreshToken = async () => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_API_AUTH_REFRESH}`,
        {},
        { withCredentials: true }
      )

      accessToken.value = response.data.access_token
      localStorage.setItem('access_token', response.data.access_token)
      return true
    } catch (err) {
      console.error('Token refresh failed:', err)
      clearAuthData()
      return false
    }
  }

  return {
    isAuthenticated,
    isLoading,
    error,
    accessToken,
    user,
    checkAuth,
    login,
    register,
    logout,
    refreshToken
  }
})