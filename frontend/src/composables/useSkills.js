import { ref } from 'vue'
import axios from 'axios'

export function useSkills() {
  const backendData = ref(null)
  const skillsData = ref({})

  const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
    headers: {
      'Content-Type': 'application/json',
    },
  })

  const loading = ref(true)
  const error = ref(null)

  const fetchTechData = async () => {
    try {
      loading.value = true
      const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_TECH)
      backendData.value = response.data.kingdoms

      skillsData.value = transformBackendData(backendData.value)
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const transformBackendData = (kingdoms) => {
    const result = {}
    kingdoms.forEach((kingdom) => {
      const key = `${kingdom.kingdom.toLowerCase()}_kingdom`
      result[key] = {
        kingdom: kingdom.kingdom,
        items: kingdom.items,
      }
    })

    return result
  }
  return [skillsData, fetchTechData, loading, error]
}
