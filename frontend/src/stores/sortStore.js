import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSortStore = defineStore('sort', () => {
  const selectedOption = ref('date_desc')

  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('sortPreference')
    if (saved && ['date_desc', 'date_asc', 'popular'].includes(saved)) {
      selectedOption.value = saved
    }
  }

  function setSortOption(option) {
    if (!['date_desc', 'date_asc', 'popular'].includes(option)) {
      console.warn(`Invalid sort option: ${option}`)
      return
    }
    selectedOption.value = option
    localStorage.setItem('sortPreference', option)
  }

  return {
    selectedOption,
    setSortOption,
  }
})
