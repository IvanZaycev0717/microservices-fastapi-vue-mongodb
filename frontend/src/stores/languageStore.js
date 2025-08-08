import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLanguageStore = defineStore('language', () => {
  const language = ref(localStorage.getItem('lang'))

  const setLanguage = (newLang) => {
    if (['en', 'ru'].includes(newLang)) {
      language.value = newLang
      localStorage.setItem('lang', newLang)
    }
  }

  const isRu = computed(() => language.value === 'ru')
  const isEn = computed(() => language.value === 'en')

  return {
    language,
    setLanguage,
    isRu,
    isEn,
  }
})
