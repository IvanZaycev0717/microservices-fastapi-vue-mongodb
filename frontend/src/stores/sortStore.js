import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSortStore = defineStore(
  'sort',
  () => {
    const selectedOption = ref('date_desc')
    const isInitialized = ref(false)

    const sortOptions = computed(() => ({
      DATE_DESC: 'date_desc',
      DATE_ASC: 'date_asc',
      POPULAR: 'popular',
    }))

    const currentSortLabel = computed(() => {
      const options = {
        date_desc: 'Newest First',
        date_asc: 'Oldest First',
        popular: 'Most Popular',
      }
      return options[selectedOption.value] || ''
    })

    function initialize() {
      if (isInitialized.value) return

      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('sortPreference')
        if (saved && Object.values(sortOptions.value).includes(saved)) {
          selectedOption.value = saved
        }
        isInitialized.value = true
      }
    }

    function setSortOption(option) {
      if (!Object.values(sortOptions.value).includes(option)) {
        console.warn(`Invalid sort option: ${option}`)
        return
      }

      selectedOption.value = option
      persistOption()
    }

    function toggleDateSort() {
      selectedOption.value = selectedOption.value === 'date_asc' ? 'date_desc' : 'date_asc'
      persistOption()
    }

    function persistOption() {
      if (typeof window !== 'undefined') {
        localStorage.setItem('sortPreference', selectedOption.value)
      }
    }

    initialize()

    return {
      selectedOption,
      isInitialized,
      sortOptions,
      currentSortLabel,
      setSortOption,
      toggleDateSort,
      initialize,
    }
  },
  {
    persist: {
      key: 'sortPreferences',
      paths: ['selectedOption'],
    },
  },
)
