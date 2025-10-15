<script setup>
import ContentScroll from '@components/ContentScroll.vue'
import TheHeader from '@components/TheHeader.vue'
import SidebarPanel from '@components/SidebarPanel.vue'
import SkyTheme from '@components/SkyTheme.vue'

import { onMounted, ref, provide, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useAuthStore } from '@stores/authStore.js'
import { useLanguageStore } from '@stores/languageStore.js'

const { t, locale } = useI18n()

const currentTheme = ref(localStorage.getItem('theme') || 'light')
const languageStore = useLanguageStore()
const authStore = useAuthStore()

const getSystemTheme = () => {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

const getBrowserLanguage = () => {
  const browserLang = navigator.language
  return browserLang.startsWith('ru') ? 'ru' : 'en'
}

const applyTheme = (theme) => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

const applyLanguage = (lang) => (locale.value = lang)

onMounted(async () => {
  /* Секция для работы с темами */
  const savedTheme = localStorage.getItem('theme')

  if (savedTheme) {
    applyTheme(savedTheme)
  } else {
    const systemTheme = getSystemTheme()
    applyTheme(systemTheme)
  }

  /* Секция для работы с языком */
  const savedLang = localStorage.getItem('lang')

  if (savedLang) {
    applyLanguage(savedLang)
  } else {
    const browserLang = getBrowserLanguage()
    languageStore.setLanguage(browserLang)
    applyLanguage(browserLang)
  }

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      applyTheme(e.matches ? 'dark' : 'light')
    }
  })
})

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
}

provide('theme', {
  currentTheme,
  toggleTheme,
})

watch(
  currentTheme,
  (newTheme) => {
    localStorage.setItem('theme', newTheme)

    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
    }
  },
  { immediate: true },
)

watch(
  () => languageStore.language,
  (newLang) => {
    applyLanguage(newLang)
  },
)
</script>
<template>
  <SkyTheme :theme="currentTheme" />
  <div class="app">
    <TheHeader />
    <div class="main-content">
      <SidebarPanel />
      <ContentScroll />
    </div>
  </div>
</template>

<style scoped>
.app {
  width: 100vw;
  height: 100vh;

  margin-top: 20px;

  background-image: url('/img/monastery.webp');
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  overflow-y: hidden;
}

.main-content {
  width: 95%;
  height: 100%;
  margin-top: 20px;
  position: relative;

  display: flex;
  justify-content: center;

  overflow: hidden;
}

@media (max-width: 768px) {
  .main-content {
    width: 100vw;
  }
}
</style>
